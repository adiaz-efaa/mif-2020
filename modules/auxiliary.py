"""
Funciones auxiliares varias.

FUNCTIONS

- show_leg: retorna la estructura de un objeto Leg en un DataFrame de pandas.
- get_curve_from_dataframe: retorna un objeto Qcf.ZeroCouponCurve.
   
"""
from finrisk import QC_Financial_3 as Qcf
from enum import Enum
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


def get_curve_from_dataframe(yf: Qcf.QCYearFraction, wf: Qcf.QCWealthFactor,
                             df_curva: pd.DataFrame, is_plazos_yf_float: bool = False) -> Qcf.ZeroCouponCurve:
    """
    Retorna un objeto Qcf.ZeroCouponCurve. Esta función requiere que `df_curva` tenga una columna
    de nombre 'plazo' y una columna de nombre 'tasa'. Se usa interpolación lineal en la curva que
    se retorna.
    """
    if is_plazos_yf_float:
        plazos = Qcf.double_vec()
    else:
        plazos = Qcf.long_vec()
    
    tasas = Qcf.double_vec()
    for row in df_curva.itertuples():
        plazos.append(row.plazo)
        tasas.append(row.tasa)
    curva = Qcf.QCCurve(plazos, tasas)
    curva = Qcf.QCLinearInterpolator(curva)
    tipo_tasa = Qcf.QCInterestRate(0.0, yf, wf)
    curva = Qcf.ZeroCouponCurve(curva, tipo_tasa)
    return curva


class BusCal(Enum):
    NY = 1
    SCL = 2

    
def get_cal(code: BusCal) -> Qcf.BusinessCalendar:
    """
    """
    if code == BusCal.NY:
        cal = Qcf.BusinessCalendar(Qcf.QCDate(1, 1, 2020), 20)
        for agno in range(2020, 2071):
            f = Qcf.QCDate(12, 10, agno)
            if f.week_day() == Qcf.WeekDay.SAT:
                cal.add_holiday(Qcf.QCDate(14, 10, agno))
            elif f.week_day() == Qcf.WeekDay.SUN:
                cal.add_holiday(Qcf.QCDate(13, 10, agno))
            elif f.week_day() == Qcf.WeekDay.MON:
                cal.add_holiday(Qcf.QCDate(12, 10, agno))
            elif f.week_day() == Qcf.WeekDay.TUE:
                cal.add_holiday(Qcf.QCDate(11, 10, agno))
            elif f.week_day() == Qcf.WeekDay.WED:
                cal.add_holiday(Qcf.QCDate(10, 10, agno))
            elif f.week_day() == Qcf.WeekDay.THU:
                cal.add_holiday(Qcf.QCDate(9, 10, agno))
            else:
                cal.add_holiday(Qcf.QCDate(8, 10, agno))
        cal.add_holiday(Qcf.QCDate(15, 2, 2021))
        
    return cal


class TypeOis(Enum):
    SOFR = 1
    ICP = 2
    

type_ois_template = {
    TypeOis.SOFR: {
        'currency': Qcf.QCUSD(),
        'periodicity': Qcf.Tenor('1Y'),
        'stub_period': Qcf.StubPeriod.SHORTFRONT,
        'settlement_lag': 0,
        'calendar': BusCal.NY,
        'bus_adj_rule': Qcf.BusyAdjRules.MODFOLLOW,
        'amort_is_cashflow': True,
        'fixed_rate': Qcf.QCInterestRate(0.0, Qcf.QCAct360(), Qcf.QCLinearWf()),
    },
    TypeOis.ICP: {
        'currency': Qcf.QCCLP(),
        'periodicity': Qcf.Tenor('6M'),
        'stub_period': Qcf.StubPeriod.SHORTFRONT,
        'settlement_lag': 0,
        'calendar': BusCal.SCL,
        'bus_adj_rule': Qcf.BusyAdjRules.MODFOLLOW,
        'amort_is_cashflow': True,
        'fixed_rate': Qcf.QCInterestRate(0.0, Qcf.QCAct360(), Qcf.QCLinearWf()),
    }
}


def get_ois_using_template(template,
                           type_ois: TypeOis, rp: Qcf.RecPay, notional: float, start_date: Qcf.QCDate,
                           tenor: Qcf.Tenor, fixed_rate_value: float, spread: float, gearing: float):
    """
    """
    template_dict = template[type_ois]
    meses = tenor.get_years() * 12 + tenor.get_months()
    end_date = start_date.add_months(meses)
    template_dict['fixed_rate'].set_value(fixed_rate_value)
    es_bono = False

    # Construye la pata fija
    fixed_rate_leg = Qcf.LegFactory.build_bullet_fixed_rate_leg(
        rp,
        start_date,
        end_date,
        template_dict['bus_adj_rule'],
        template_dict['periodicity'],
        template_dict['stub_period'],
        get_cal(template_dict['calendar']),
        template_dict['settlement_lag'],
        notional,
        template_dict['amort_is_cashflow'],
        template_dict['fixed_rate'],
        template_dict['currency'],
        es_bono)

    # Construye la pata ois
    rp = Qcf.RecPay.PAY if rp == Qcf.RecPay.RECEIVE else Qcf.RecPay.RECEIVE
    icp_clp_leg = Qcf.LegFactory.build_bullet_icp_clp2_leg(
        rp,
        start_date,
        end_date,
        template_dict['bus_adj_rule'],
        template_dict['periodicity'],
        template_dict['stub_period'],
        get_cal(template_dict['calendar']),
        template_dict['settlement_lag'],
        notional,
        template_dict['amort_is_cashflow'],
        spread,
        gearing,
        True
    )

    for i in range(icp_clp_leg.size()):
        cshflw = icp_clp_leg.get_cashflow_at(i)
        cshflw.set_start_date_icp(1.0)
        cshflw.set_end_date_icp(1.0)

    return (fixed_rate_leg, icp_clp_leg)