import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import brentq

st.set_page_config(page_title="Hypotéka vs Investice", layout="wide")
st.title("Hypotéka vs Investice")
st.markdown("""
Porovnání dvou strategií:
- **Případ 1**: Vezmu si plnou hypotéku a počáteční částku ihned investuji jako jednorázovou investici
- **Případ 2**: Počáteční částkou snížím hypotéku, měsíčně investuji ušetřenou splátku
""")

st.markdown("---")

# --- Vstupy ---
st.header("Vstupní parametry")

col1, col2 = st.columns(2)

with col1:
    P0 = st.number_input("Velikost půjčky (CZK)", value=9_000_000, step=100_000, format="%d",
                         help="Celková výše hypotéky bez počáteční investice")
    st.caption(f"→ {P0:,.0f} CZK".replace(",", "."))
    P_init = st.number_input("Počáteční investice / vlastní zdroje (CZK)", value=2_000_000, step=100_000, format="%d",
                             help="Částka, kterou máš k dispozici — buď ji investuješ, nebo snížíš hypotéku")
    st.caption(f"→ {P_init:,.0f} CZK".replace(",", "."))

with col2:
    annual_mortgage_rate = st.number_input("Úroková míra hypotéky (% p.a.)", value=4.9, step=0.1, format="%.2f")
    annual_invest_rate = st.number_input("Nominální výnosnost investice (% p.a., před inflací)", value=8.0, step=0.1, format="%.2f",
                                         help="Zadej nominální výnos před inflací — stejná basis jako úroková sazba hypotéky. Např. globální index ~7–8 % p.a. nominálně.")
    inflation_rate = st.number_input("Inflace (% p.a.)", value=2.5, step=0.1, format="%.2f",
                                     help="Průměrná roční inflace pro převod na reálnou hodnotu v dnešních penězích. Historický průměr ČR ~2–3 %.")
    years = st.number_input("Doba splatnosti (roky)", value=30, step=1, min_value=1, max_value=50)

# --- Odvozené hodnoty ---
N = int(years * 12)
i = annual_mortgage_rate / 100 / 12                        # nominalni mesicni sazba (bankovni konvence)
s = (1 + annual_invest_rate / 100) ** (1 / 12) - 1        # efektivni mesicni sazba (z rocni vynosnosti)
inflation_deflator = (1 + inflation_rate / 100) ** years   # kolik bude 1 dnešní Kč stát za N let

st.markdown("---")

# --- Vzorce ---

def monthly_payment(principal, monthly_rate, n_months):
    """A = P * i*(1+i)^N / ((1+i)^N - 1)"""
    if principal <= 0:
        return 0.0
    if monthly_rate == 0:
        return principal / n_months
    return principal * monthly_rate * (1 + monthly_rate)**n_months / ((1 + monthly_rate)**n_months - 1)

def fv_lump_sum(P, monthly_rate, n_months):
    """FV = P * (1+s)^N"""
    return P * (1 + monthly_rate)**n_months

def fv_monthly_contributions(A, monthly_rate, n_months):
    """FV = A * ((1+s)^N - 1) / s"""
    if monthly_rate == 0:
        return A * n_months
    return A * ((1 + monthly_rate)**n_months - 1) / monthly_rate

# Případ 1: Plná hypotéka, počáteční částka jde do investice
A1 = monthly_payment(P0, i, N)
FV1 = fv_lump_sum(P_init, s, N)
FV1_real = FV1 / inflation_deflator

# Případ 2: Snížená hypotéka, investuji měsíční rozdíl
loan2 = P0 - P_init
A2 = monthly_payment(loan2, i, N)
delta_A = A1 - A2
FV2 = fv_monthly_contributions(delta_A, s, N)
FV2_real = FV2 / inflation_deflator

# Hraniční výnosnost (breakeven)
def fv_diff(s_annual):
    sm = (1 + s_annual) ** (1/12) - 1
    a1 = monthly_payment(P0, i, N)
    a2 = monthly_payment(loan2, i, N)
    da = a1 - a2
    fv1 = fv_lump_sum(P_init, sm, N)
    fv2 = fv_monthly_contributions(da, sm, N)
    return fv1 - fv2

try:
    breakeven_rate = brentq(fv_diff, 0.0001, 0.5) * 100
except Exception:
    breakeven_rate = None

# --- Výsledky ---
st.header("Výsledky")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Případ 1: Plná hypotéka + jednorázová investice")
    st.markdown(f"""
| Položka | Hodnota |
|---|---|
| Výše úvěru | **{str(f"{P0:,.0f}").replace(",", ".")} CZK** |
| Měsíční splátka | **{str(f"{A1:,.0f}").replace(",", ".")} CZK** |
| Počáteční investice | **{str(f"{P_init:,.0f}").replace(",", ".")} CZK** |
| Budoucí hodnota (nominální) | **{str(f"{FV1:,.0f}").replace(",", ".")} CZK** |
| Budoucí hodnota (reálná, v dnešních Kč) | **{str(f"{FV1_real:,.0f}").replace(",", ".")} CZK** |
""")
    st.latex(r"FV_1 = P_{init} \cdot (1+s)^N")

with col2:
    st.subheader("Případ 2: Snížená hypotéka + investování rozdílu splátek")
    st.markdown(f"""
| Položka | Hodnota |
|---|---|
| Výše úvěru | **{str(f"{loan2:,.0f}").replace(",", ".")} CZK** |
| Měsíční splátka | **{str(f"{A2:,.0f}").replace(",", ".")} CZK** |
| Měsíční úspora (investovaná) | **{str(f"{delta_A:,.0f}").replace(",", ".")} CZK** |
| Budoucí hodnota (nominální) | **{str(f"{FV2:,.0f}").replace(",", ".")} CZK** |
| Budoucí hodnota (reálná, v dnešních Kč) | **{str(f"{FV2_real:,.0f}").replace(",", ".")} CZK** |
""")
    st.latex(r"FV_2 = \Delta A \cdot \frac{(1+s)^N - 1}{s}")

st.markdown("---")

# --- Verdikt ---
diff = FV1 - FV2
diff_real = FV1_real - FV2_real
if diff > 0:
    st.success(
        f"**Případ 1 je lepší o {diff:,.0f} CZK nominálně** ({diff_real:,.0f} CZK v dnešních penězích) po {years:.0f} letech."
    )
    st.markdown(f"Důvod: Váš kapitál **{P_init:,.0f} CZK** má plných **{years:.0f} let** na složené úročení. "
                f"Měsíční investice v Případu 2 začíná malými částkami, které nemají tolik času růst.")
else:
    st.success(
        f"**Případ 2 je lepší o {-diff:,.0f} CZK nominálně** ({-diff_real:,.0f} CZK v dnešních penězích) po {years:.0f} letech."
    )

# --- Hraniční výnosnost ---
if breakeven_rate is not None:
    st.markdown("---")
    st.header("Hraniční výnosnost investice")
    st.info(
        f"Při úrokové sazbě hypotéky **{annual_mortgage_rate:.2f} %** jsou obě strategie shodné, "
        f"pokud investice vynáší přesně **{breakeven_rate:.2f} % p.a.**\n\n"
        f"- Pokud věříš, že investice vynese **více než {breakeven_rate:.2f} %** → zvol Případ 1 (investuj vše hned)\n"
        f"- Pokud věříš, že investice vynese **méně než {breakeven_rate:.2f} %** → zvol Případ 2 (splať hypotéku)"
    )

# --- Klíčová čísla ---
st.markdown("---")
st.header("Klíčová čísla")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Splátka – Případ 1", f"{A1:,.0f} CZK/měs")
col2.metric("Splátka – Případ 2", f"{A2:,.0f} CZK/měs", delta=f"-{delta_A:,.0f} CZK/měs")
col3.metric("Reálná FV – Případ 1", f"{FV1_real:,.0f} CZK", help="V dnešních penězích po zohlednění inflace")
col4.metric("Reálná FV – Případ 2", f"{FV2_real:,.0f} CZK", help="V dnešních penězích po zohlednění inflace")

# --- Graf vývoje ---
st.markdown("---")
st.header("Vývoj v čase")

months = np.arange(1, N + 1)
fv1_nominal = P_init * (1 + s)**months
fv2_nominal = delta_A * ((1 + s)**months - 1) / s if s != 0 else delta_A * months

inflation_deflator_monthly = (1 + inflation_rate / 100) ** (months / 12)
fv1_real = fv1_nominal / inflation_deflator_monthly
fv2_real = fv2_nominal / inflation_deflator_monthly

chart_df = pd.DataFrame({
    "Rok": months / 12,
    "Případ 1 – nominální": fv1_nominal,
    "Případ 2 – nominální": fv2_nominal,
    "Případ 1 – reálná (dnešní Kč)": fv1_real,
    "Případ 2 – reálná (dnešní Kč)": fv2_real,
})

tab1, tab2 = st.tabs(["Nominální hodnoty", "Reálné hodnoty (v dnešních Kč)"])
with tab1:
    st.line_chart(chart_df, x="Rok", y=["Případ 1 – nominální", "Případ 2 – nominální"])
with tab2:
    st.line_chart(chart_df, x="Rok", y=["Případ 1 – reálná (dnešní Kč)", "Případ 2 – reálná (dnešní Kč)"])

# --- Matematické vzorce ---
with st.expander("Matematické vzorce (rozbalit)"):
    st.markdown("#### Měsíční splátka hypotéky")
    st.latex(r"A = P_0 \cdot \frac{i \cdot (1+i)^N}{(1+i)^N - 1}")
    st.markdown("kde $i$ = měsíční úroková sazba, $N$ = počet měsíců, $P_0$ = výše úvěru")

    st.markdown("#### Budoucí hodnota – jednorázová investice (Případ 1)")
    st.latex(r"FV_1 = P_{init} \cdot (1+s)^N")

    st.markdown("#### Budoucí hodnota – pravidelné měsíční investice (Případ 2)")
    st.latex(r"FV_2 = \Delta A \cdot \frac{(1+s)^N - 1}{s}")
    st.markdown("kde $\\Delta A = A_1 - A_2$ je měsíční úspora díky snížené hypotéce")

    st.markdown("#### Převod na reálnou hodnotu (dnešní kupní síla)")
    st.latex(r"FV_{reálná} = \frac{FV_{nominální}}{(1 + \pi)^{roky}}")
    st.markdown("kde $\\pi$ = roční míra inflace. Inflace se vyruší v porovnání obou případů — neovlivňuje, která strategie vyhraje, ale ukazuje skutečnou kupní sílu.")

    st.markdown("#### Proč jednorázová investice často vítězí")
    st.markdown("""
Protože $P_{init}$ má **plných N let** na složené úročení.
Zatímco měsíční investice začíná malými částkami — první koruna má N měsíců, ale poslední koruna má jen 1 měsíc.
Exponenciála je extrémně citlivá na čas.
""")

st.markdown("---")
st.caption("Zjednodušený model: konstantní sazby, bez daní a poplatků. Výnosnost investice je nominální (před inflací). Reálné hodnoty jsou přepočteny pomocí zadané inflace.")
