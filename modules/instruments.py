"""
Módulo con funciones sencillas de construcción y valorización de instrumentos financieros derivados.
"""

from typing import List, Tuple


def bono_tasa_fija(
    start_time: float,
    yf: float,
    num_cupones: int,
    valor_tasa: float) -> List[Tuple[float, float]]:
    """
    Retorna los plazos y flujos de un bono a tasa fija bullet con nominal = 1.
    
    params:
    
    - start_time: fecha (expresada en fracción de año) en que comienza el devengo del primer cupón.
    - yf: fracción de año que representa la periodicidad del bono (yf = .5 -> bono semestral).
    - num_cupones: número de cupones del bono
    - valor_tasa: valor de la tasa fija del bono. Los intereses se calculan de forma lineal.
    
    return:
    
    - Una `list` de `tuple` con la fecha de pago del cupón (como instante de tiempo) y el monto del cupón.
    """
    result = []
    nominal = 100.0
    flujo = nominal * valor_tasa * yf
    for i in range(1, num_cupones + 1):
        if i == num_cupones:
            flujo += nominal
        result.append((i * yf + start_time, flujo))
    return result
