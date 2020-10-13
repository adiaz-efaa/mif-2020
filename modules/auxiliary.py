"""
Funciones auxiliares varias.

FUNCTIONS
   aux.show_leg(icp_clp_leg, 'IcpClpCashflow').style.format(format_dict)
       Retorna la estructura de un objeto Leg en un DataFrame de pandas.

"""
from finrisk import QC_Financial_3 as Qcf
import pandas as pd

def show_leg(leg, leg_type:str, leg_subtype: str = '') -> pd.DataFrame:
    """
    Retorna la estructura de un objeto Leg en un DataFrame de pandas.
    """
    tabla = []
    for i in range(0, leg.size()):
        tabla.append(Qcf.show(leg.get_cashflow_at(i)))
        
    if leg_type == 'FixedRateMultiCurrencyCashflow':
        columnas = ['fecha_inicial', 'fecha_final', 'fecha_pago', 'nominal', 'amortizacion',
                    'interes', 'amort_es_cashflow', 'flujo_moneda_nocional',
                    'moneda_nocional', 'valor_tasa', 'tipo_tasa', 'fecha_fixing_fx',
                    'moneda_pago', 'codigo_indice_fx', 'valor_indice_fx',
                    'amort_moneda_pago', 'interes_moneda_pago']
        df = pd.DataFrame(tabla, columns=columnas)
        return df

    columnas = list(Qcf.get_column_names(leg_type, leg_subtype))
    df = pd.DataFrame(tabla, columns=columnas)

    return df
