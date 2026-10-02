from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, request
from django.views import View
from django.http import JsonResponse

from .infra.factories import PaymentFactory
from .services import CompraService
from .models import Libro, Inventario, Orden


import datetime


class CompraView(View):
   

    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)

        inventario = Inventario.objects.get(libro_id=libro_id)
        contexto['stock'] = inventario.cantidad

        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        try:
            total = servicio.ejecutar_compra(libro_id, cantidad=1)
            return render(
                request,
                self.template_name,
                {
                    'mensaje_exito': f"¡Gracias por su compra! Total: ${total:.2f}",
                    'total': total,
                },
            )
        except Exception as e:
            print("ERROR:", e)
            raise





def compra_rapida_fbv(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if request.method == 'POST':
        # VIOLACIÓN SRP: Lógica de inventario en la vista
        inventario = Inventario.objects.get(libro=libro)

        if inventario.cantidad > 0:
            # VIOLACIÓN OCP: Cálculo de negocio hardcoded
            total = float(libro.precio) * 1.19

            # VIOLACIÓN DIP: Proceso de pago acoplado al sistema de archivos
            with open("pagos_manuales.log", "a") as f:
                f.write(f"[{datetime.datetime.now()}] Pago FBV: ${total}\n")

            inventario.cantidad -= 1
            inventario.save()

            Orden.objects.create(
                libro=libro,
                total=total
            )

            return HttpResponse(f"Compra exitosa: {libro.titulo}")

        return HttpResponse("Sin stock", status=400)

    total_estimado = float(libro.precio) * 1.19

    return render(
        request,
        "tienda_app/compra_rapida.html",
        {
            "libro": libro,
            "total": total_estimado
        }
    )




class CompraRapidaView(View):
    template_name = 'tienda_app/compra_rapida.html'

    def get(self, request, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = float(libro.precio) * 1.19

        return render(
            request,
            self.template_name,
            {
                'libro': libro,
                'total': total
            }
        )

    def post(self, request, libro_id):
        # La lógica de negocio aún reside aquí, pero separada del GET
        libro = get_object_or_404(Libro, id=libro_id)
        inv = Inventario.objects.get(libro=libro)

        if inv.cantidad > 0:
            total = float(libro.precio) * 1.19


            return HttpResponse("Comprado via CBV")

        return HttpResponse("Error", status=400)


def lista_productos(request):
    productos = list(Libro.objects.values('id', 'titulo', 'precio'))
    return JsonResponse({"productos": productos})