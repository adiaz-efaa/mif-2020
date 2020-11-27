"""
Contiene funciones relacionadas con el modelo de Hull-White en tiempo continuo.
"""
from scipy.interpolate import interp1d
import numpy as np


def b_hw(gamma: float, t: float, T: float) -> float:
    """
    Calcula el valor de la función B(t,T) que interviene en la fórmula
    para el valor de un bono cupón cero en el modelo de HW.
    
    params:
    
    - gamma: intensidad de reversión del modelo HW
    - t: fecha (instante de tiempo) en la que se está calculando
    - T: fecha (instante de tiempo) de vencimiento del bono
    
    return:
    
    - valor de la función B(t, T)
    """
    aux = 1 - math.exp(- gamma * (T - t))
    return aux / gamma


def a_hw(zrate, fwd, gamma: float, sigma: float, t: float, T: float,
         verbose = False):
    """
    Calcula el valor de la función A(t,T) que interviene en la fórmula
    para el valor de un bono cupón cero en el modelo de HW.
    
    params:
    
    - zrate:
    - fwd:
    - gamma: intensidad de reversión del modelo HW
    - sigma: parámetro de volatilidad del modelo HW
    - t: fecha (instante de tiempo) en la que se está calculando
    - T: fecha (instante de tiempo) de vencimiento del bono
    - verbose: cuando es True imprime los valores de c1, c2 y c3.
    
    return:
    
    - valor de la función A(t,T)
    """
    b = b_hw(gamma, t, T)
    dfT = math.exp(-zrate(T) * T)
    dft = math.exp(-zrate(t) * t)
    c1 = math.log(dfT / dft)
    c2 = b * fwd(t)
    c3 = (sigma**2) / (4 * gamma) * (b**2) * (1 - math.exp(-2 * gamma * t))
    if verbose:
        print("c1: " + str(c1))
        print("c2: " + str(c2))
        print("c3: " + str(c3))
    return c1 + c2 - c3


def zero_hw(r: float, gamma: float, sigma: float,
            zrate, fwd, t: float, T: float) -> float:
    """
    Calcula en t el valor de un bono cupón cero que vence en T según la fórmula del modelo de HW.
    
    params:
    
    - r: valor de la tasa corta en t
    - gamma: intensidad de reversión del modelo HW
    - sigma: parámetro de volatilidad del modelo HW
    - zrate:
    - fwd:
    - t: fecha (instante de tiempo) en la que se está calculando
    - T: fecha (instante de tiempo) de vencimiento del bono
    
    return:
    
    - valor del bono cupón cero (factor de descuento)
    """
    a = a_hw(zrate, fwd, gamma, sigma, t, T)
    b = b_hw(gamma, t, T)
    return math.exp(a - b * r)


def get_zrate_and_theta(plazos, tasas):
    """
    Construye un interpolador por cubic spline para la curva cero cupón y la función theta del modelo de HW.
    
    params:
    
    - plazos: iterable con los plazos de la curva en convención yf Act/365
    - tasas: iterable con las tasas de la curva en convención expAct/365
    
    return:
    
    - una `tuple` cuyo primer elemento es el cubic spline y cuyo segundo elemento es la función theta.
    """
    # Esto es la curva cero cupón embedida en un interpolador diferenciable.
    # zrate(t: float) -> float. Para un plazo t calcula la tasa al plazo t (con el cubic spline).
    zrate = interp1d(curva['t'],
                  curva['rate'],
                  kind='cubic', # <--- diferenciable (cubic spline)
                  fill_value="extrapolate")
    
    def dzrate(t: float) -> float:
        delta = .0001
        return (zcurva(t + delta) - zrate(t)) / delta

    def d2zrate(t: float) -> float:
        delta = .0001
        return (dzrate(t + delta) - dzrate(t)) / delta
    
    def fwd(t: float) -> float:
        return zrate(t) + t * dzrate(t)

    def dfwd(t: float) -> float:
        return 2 * dzrate(t) + t * d2zrate(t)
    
    def theta(t: float) -> float:
        aux = (sigma ** 2) / (2.0 * gamma) * (1 - math.exp(-2.0 * gamma * t))
        return dfwd(t) + gamma * fwd(t) + aux
    
    return zrate, theta


def sim_hw_many(gamma, sigma, theta, r0, num_sim, num_steps, seed = None):
    """
    Simula trayectorias del modelo de HW con un paso de simulación diario dt = 1/264.
    
    params:
    
    - gamma: intensidad de reversión del modelo HW
    - sigma: parámetro de volatilidad del modelo HW
    - theta: función theta del modelo de HW
    - r0: valor de la tasa corta a tiempo t = 0 (valor inicial de todas las trayectorias)
    - num_sim: número de trayectorias a calcular
    - num_steps: número de pasos de simulación de cada trayectoria. El horizonte final de cada trayectoria
    está dado por num_steps * dt (donde dt=1/264).
    - seed: semilla a usar en la simulación. Cuando es `None` la semilla es aleatoria.
    
    return:
    
    - una matriz (numpy.array), donde cada fila es una trayectoria y cada columna
    es un paso de simulación.
    """
    dt = 1 / 264.0
    num_steps += 1
    
    # Calcula los números aleatorios
    alea = np.zeros((num_sim, num_steps))
    np.random.seed(seed)

    for i in range(0, num_sim):
        for j in range(0, num_steps):
            alea[i][j] = random.normal()
            
    # Calcula los valores de Theta. Theta sólo depende del tiempo, no de la simulación. 
    theta_array = np.zeros(num_steps)
    tiempo = np.zeros(num_steps)
    for i in range(0, num_steps):np.
        tiempo[i] = i * dt
        theta_array[i] = theta(i * dt)
    
    # Simula las trayectorias
    sqdt_sigma = math.sqrt(dt) * sigma
    gamma_dt = gamma * dt
    sim = np.zeros((num_sim, num_steps))
    for i in range(0, num_sim):
        sim[i][0] = r0
        r = r0
        for j in range(1, num_steps):
            r = r + theta_array[j - 1] * dt - gamma_dt * r + sqdt_sigma * alea[i][j - 1]
            sim[i][j] = r
    return tiempo, sim
