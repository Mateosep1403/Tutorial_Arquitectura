from rest_framework import serializers
from tienda_app.models import Libro, Orden


class LibroSerializer(serializers.ModelSerializer):
    stock_actual = serializers.SerializerMethodField()

    class Meta:
        model = Libro
        fields = ['id', 'titulo', 'precio', 'stock_actual']

    def get_stock_actual(self, obj):
        # obj.inventario viene del OneToOneField definido en Inventario
        inventario = getattr(obj, 'inventario', None)
        return inventario.cantidad if inventario else 0


class OrdenInputSerializer(serializers.Serializer):
    """
    Serializer para VALIDAR la entrada de datos, no ligado a un modelo.
    Actúa como un DTO (Data Transfer Object).
    """
    libro_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(default=1, min_value=1)
    direccion_envio = serializers.CharField(max_length=200)