import os
from ..domain.interfaces import ProcesadorPago
from .gateways import BancoNacionalProcesador


class MockPaymentProcessor(ProcesadorPago):
    """
    Implementación ligera para pruebas (Mocking).
    Cumple el mismo contrato que BancoNacionalProcesador.
    """
    def pagar(self, monto: float) -> bool:
        print(f"[DEBUG] Mock Payment: Procesando pago de ${monto} sin cargo real.")
        return True


class PaymentFactory:
    @staticmethod
    def get_processor() -> ProcesadorPago:
        provider = os.getenv('PAYMENT_PROVIDER', 'BANCO')

        if provider == 'MOCK':
            return MockPaymentProcessor()

        return BancoNacionalProcesador()