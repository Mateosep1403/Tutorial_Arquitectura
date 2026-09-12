from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import OrdenInputSerializer
from tienda_app.services import CompraService       # <--- REUTILIZACION
from tienda_app.infra.factories import PaymentFactory


class CompraAPIView(APIView):
    """
    Endpoint para procesar compras vía JSON.
    POST /api/v1/comprar/
    Payload: {"libro_id": 1, "cantidad": 1, "direccion_envio": "Calle 123"}
    """

    def post(self, request):
        # 1. Validación de datos de entrada (Adapter)
        serializer = OrdenInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data

        try:
            # 2. Inyección de Dependencias (Factory)
            gateway = PaymentFactory.get_processor()

            # 3. Ejecución de Lógica de Negocio (Service Layer)
            servicio = CompraService(procesador_pago=gateway)

            usuario = request.user if request.user.is_authenticated else None

            # Nota: el servicio NO cambia, solo cambia quién lo llama.
            total = servicio.ejecutar_compra(
                libro_id=datos['libro_id'],
                cantidad=datos['cantidad'],
                direccion=datos['direccion_envio'],
                usuario=usuario,
            )

            return Response({
                "estado": "exito",
                "mensaje": f"Orden creada. Total: {total}"
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            # Errores de negocio (ej: Sin stock)
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)

        except Exception as e:
            # Errores inesperados (ej: banco rechazó el pago)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)