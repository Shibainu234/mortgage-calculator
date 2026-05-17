import streamlit as st
import numpy as np
import pandas as pd
from scipy.optimize import brentq

st.set_page_config(page_title="Hypotéka vs Investice", layout="wide", initial_sidebar_state="collapsed")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Page background */
.stApp { background-color: #f7f9fc; }

/* Hero header */
.hero {
    background: linear-gradient(135deg, #1a1f36 0%, #2d3561 100%);
    border-radius: 16px;
    padding: 40px 48px;
    margin-bottom: 32px;
    color: white;
}
.hero h1 { font-size: 2.2rem; font-weight: 700; margin: 0 0 8px 0; color: white; }
.hero p  { font-size: 1rem; color: #a0aec0; margin: 0; }

/* Section headers */
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1f36;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 32px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #e2e8f0;
}

/* Input card */
.input-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    margin-bottom: 16px;
}

/* Result cards */
.result-card {
    background: white;
    border-radius: 12px;
    padding: 28px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    height: 100%;
}
.result-card.pripad1 { border-top: 4px solid #4f6ef7; }
.result-card.pripad2 { border-top: 4px solid #38b2ac; }

.card-title {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 20px;
}
.card-title.blue { color: #4f6ef7; }
.card-title.teal { color: #38b2ac; }

.row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #f0f4f8;
    font-size: 0.9rem;
}
.row:last-child { border-bottom: none; }
.row-label { color: #718096; }
.row-value { font-weight: 600; color: #1a1f36; }
.row-value.highlight { color: #4f6ef7; font-size: 1rem; }
.row-value.highlight-teal { color: #38b2ac; font-size: 1rem; }
.row-value.real { color: #a0aec0; font-size: 0.85rem; font-weight: 400; }

/* Verdict box */
.verdict {
    border-radius: 12px;
    padding: 24px 32px;
    margin: 24px 0;
    display: flex;
    align-items: center;
    gap: 16px;
}
.verdict.win1 { background: #ebf4ff; border-left: 5px solid #4f6ef7; }
.verdict.win2 { background: #e6fffa; border-left: 5px solid #38b2ac; }
.verdict-title { font-size: 1.1rem; font-weight: 700; margin-bottom: 4px; }
.verdict-title.blue { color: #4f6ef7; }
.verdict-title.teal { color: #38b2ac; }
.verdict-body { font-size: 0.9rem; color: #4a5568; }

/* Breakeven box */
.breakeven {
    background: white;
    border-radius: 12px;
    padding: 24px 32px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    border-left: 5px solid #ed8936;
    margin: 24px 0;
}
.breakeven-rate { font-size: 2rem; font-weight: 700; color: #ed8936; }
.breakeven-label { font-size: 0.85rem; color: #718096; margin-top: 4px; }
.breakeven-body { font-size: 0.9rem; color: #4a5568; margin-top: 12px; }

/* Metric cards */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    text-align: center;
}
.metric-label { font-size: 0.78rem; color: #718096; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
.metric-value { font-size: 1.35rem; font-weight: 700; color: #1a1f36; }
.metric-value.blue { color: #4f6ef7; }
.metric-value.teal { color: #38b2ac; }
.metric-sub { font-size: 0.8rem; color: #a0aec0; margin-top: 4px; }

/* Hide default streamlit elements */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>Hypotéka vs Investice</h1>
    <p>Porovnej dvě strategie: investuj počáteční kapitál hned, nebo ho vlož do hypotéky a investuj měsíční úsporu.</p>
</div>
""", unsafe_allow_html=True)

# ── Inputs ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Vstupní parametry</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    P0_m = st.number_input("Velikost půjčky (mil. CZK)", value=9.0, step=0.1, format="%.2f",
                         help="Celková výše hypotéky bez počáteční investice")
    P0 = P0_m * 1_000_000
    st.caption(f"→ {fmt(P0)} CZK")
    P_init_m = st.number_input("Vlastní zdroje / počáteční kapitál (mil. CZK)", value=2.0, step=0.1, format="%.2f",
                             help="Částka, kterou máš k dispozici — buď ji investuješ, nebo snížíš hypotéku")
    P_init = P_init_m * 1_000_000
    st.caption(f"→ {fmt(P_init)} CZK")

with col2:
    annual_mortgage_rate = st.number_input("Úroková míra hypotéky (% p.a.)", value=4.9, step=0.1, format="%.2f")
    annual_invest_rate   = st.number_input("Nominální výnosnost investice (% p.a., před inflací)", value=8.0, step=0.1, format="%.2f",
                                           help="Nominální výnos před inflací — stejná basis jako sazba hypotéky. Globální index ~7–8 % p.a.")
    inflation_rate       = st.number_input("Inflace (% p.a.)", value=2.5, step=0.1, format="%.2f",
                                           help="Průměrná roční inflace. Historický průměr ČR ~2–3 %.")
    years                = st.number_input("Doba splatnosti (roky)", value=30, step=1, min_value=1, max_value=50)

# ── Calculations ──────────────────────────────────────────────────────────────
N                  = int(years * 12)
i                  = annual_mortgage_rate / 100 / 12
s                  = (1 + annual_invest_rate / 100) ** (1 / 12) - 1
inflation_deflator = (1 + inflation_rate / 100) ** years

def fmt(n): return str(f"{n:,.0f}").replace(",", ".")

def monthly_payment(principal, monthly_rate, n_months):
    if principal <= 0: return 0.0
    if monthly_rate == 0: return principal / n_months
    return principal * monthly_rate * (1 + monthly_rate)**n_months / ((1 + monthly_rate)**n_months - 1)

def fv_lump_sum(P, monthly_rate, n_months):
    return P * (1 + monthly_rate)**n_months

def fv_monthly_contributions(A, monthly_rate, n_months):
    if monthly_rate == 0: return A * n_months
    return A * ((1 + monthly_rate)**n_months - 1) / monthly_rate

A1    = monthly_payment(P0, i, N)
FV1   = fv_lump_sum(P_init, s, N)
FV1_real = FV1 / inflation_deflator

loan2   = P0 - P_init
A2      = monthly_payment(loan2, i, N)
delta_A = A1 - A2
FV2     = fv_monthly_contributions(delta_A, s, N)
FV2_real = FV2 / inflation_deflator

def fv_diff(s_annual):
    sm = (1 + s_annual) ** (1/12) - 1
    da = monthly_payment(P0, i, N) - monthly_payment(loan2, i, N)
    return fv_lump_sum(P_init, sm, N) - fv_monthly_contributions(da, sm, N)

try:
    breakeven_rate = brentq(fv_diff, 0.0001, 0.5) * 100
except Exception:
    breakeven_rate = None

# ── Results ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Výsledky</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
<div class="result-card pripad1">
    <div class="card-title blue">Případ 1 — Plná hypotéka + jednorázová investice</div>
    <div class="row"><span class="row-label">Výše úvěru</span><span class="row-value">{fmt(P0)} CZK</span></div>
    <div class="row"><span class="row-label">Měsíční splátka</span><span class="row-value">{fmt(A1)} CZK</span></div>
    <div class="row"><span class="row-label">Investovaný kapitál</span><span class="row-value">{fmt(P_init)} CZK</span></div>
    <div class="row"><span class="row-label">Budoucí hodnota (nominální)</span><span class="row-value highlight">{fmt(FV1)} CZK</span></div>
    <div class="row"><span class="row-label">Budoucí hodnota (reálná)</span><span class="row-value real">{fmt(FV1_real)} CZK v dnešních Kč</span></div>
</div>
""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
<div class="result-card pripad2">
    <div class="card-title teal">Případ 2 — Snížená hypotéka + měsíční investice</div>
    <div class="row"><span class="row-label">Výše úvěru</span><span class="row-value">{fmt(loan2)} CZK</span></div>
    <div class="row"><span class="row-label">Měsíční splátka</span><span class="row-value">{fmt(A2)} CZK</span></div>
    <div class="row"><span class="row-label">Měsíční úspora (investovaná)</span><span class="row-value">{fmt(delta_A)} CZK</span></div>
    <div class="row"><span class="row-label">Budoucí hodnota (nominální)</span><span class="row-value highlight-teal">{fmt(FV2)} CZK</span></div>
    <div class="row"><span class="row-label">Budoucí hodnota (reálná)</span><span class="row-value real">{fmt(FV2_real)} CZK v dnešních Kč</span></div>
</div>
""", unsafe_allow_html=True)

# ── Verdict ───────────────────────────────────────────────────────────────────
diff      = FV1 - FV2
diff_real = FV1_real - FV2_real

if diff > 0:
    st.markdown(f"""
<div class="verdict win1">
    <div>
        <div class="verdict-title blue">Případ 1 vítězí</div>
        <div class="verdict-body">
            Jednorázová investice je lepší o <strong>{fmt(diff)} CZK nominálně</strong>
            ({fmt(diff_real)} CZK v dnešních penězích) po {years:.0f} letech.<br>
            Váš kapitál má plných {years:.0f} let na složené úročení — každá koruna pracuje od prvního dne.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
else:
    st.markdown(f"""
<div class="verdict win2">
    <div>
        <div class="verdict-title teal">Případ 2 vítězí</div>
        <div class="verdict-body">
            Snížená hypotéka + měsíční investice je lepší o <strong>{fmt(-diff)} CZK nominálně</strong>
            ({fmt(-diff_real)} CZK v dnešních penězích) po {years:.0f} letech.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Breakeven ─────────────────────────────────────────────────────────────────
if breakeven_rate is not None:
    st.markdown(f"""
<div class="breakeven">
    <div class="breakeven-rate">{breakeven_rate:.2f} % p.a.</div>
    <div class="breakeven-label">Hraniční výnosnost investice</div>
    <div class="breakeven-body">
        Při sazbě hypotéky <strong>{annual_mortgage_rate:.2f} %</strong> jsou obě strategie shodné právě při výnosnosti <strong>{breakeven_rate:.2f} %</strong>.<br>
        Věříš v <strong>vyšší výnos</strong> → zvol Případ 1 &nbsp;·&nbsp; Věříš v <strong>nižší výnos</strong> → zvol Případ 2
    </div>
</div>
""", unsafe_allow_html=True)

# ── Key metrics ───────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Klíčová čísla</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">Splátka — Případ 1</div>
    <div class="metric-value blue">{fmt(A1)} CZK</div>
    <div class="metric-sub">měsíčně</div>
</div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">Splátka — Případ 2</div>
    <div class="metric-value teal">{fmt(A2)} CZK</div>
    <div class="metric-sub">úspora {fmt(delta_A)} CZK/měs</div>
</div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">FV nominální / reálná — Případ 1</div>
    <div class="metric-value blue">{fmt(FV1)} CZK</div>
    <div class="metric-sub">{fmt(FV1_real)} CZK v dnešních Kč</div>
</div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
<div class="metric-card">
    <div class="metric-label">FV nominální / reálná — Případ 2</div>
    <div class="metric-value teal">{fmt(FV2)} CZK</div>
    <div class="metric-sub">{fmt(FV2_real)} CZK v dnešních Kč</div>
</div>""", unsafe_allow_html=True)

# ── Chart ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Vývoj v čase</div>', unsafe_allow_html=True)

months                   = np.arange(1, N + 1)
fv1_nominal              = P_init * (1 + s)**months
fv2_nominal              = delta_A * ((1 + s)**months - 1) / s if s != 0 else delta_A * months
inflation_deflator_m     = (1 + inflation_rate / 100) ** (months / 12)
fv1_real_t               = fv1_nominal / inflation_deflator_m
fv2_real_t               = fv2_nominal / inflation_deflator_m

chart_df = pd.DataFrame({
    "Rok":                            months / 12,
    "Případ 1 – nominální":           fv1_nominal,
    "Případ 2 – nominální":           fv2_nominal,
    "Případ 1 – reálná (dnešní Kč)": fv1_real_t,
    "Případ 2 – reálná (dnešní Kč)": fv2_real_t,
})

tab1, tab2 = st.tabs(["📈 Nominální hodnoty", "💰 Reálné hodnoty (v dnešních Kč)"])
with tab1:
    st.line_chart(chart_df, x="Rok", y=["Případ 1 – nominální", "Případ 2 – nominální"])
    st.caption("Nominální hodnoty — bez zohlednění inflace")
with tab2:
    st.line_chart(chart_df, x="Rok", y=["Případ 1 – reálná (dnešní Kč)", "Případ 2 – reálná (dnešní Kč)"])
    st.caption("Reálné hodnoty — převedeno do dnešní kupní síly")

# ── Sensitivity table ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Citlivostní analýza</div>', unsafe_allow_html=True)
st.markdown("Rozdíl budoucí hodnoty Případ 1 − Případ 2 (nominálně, v mil. CZK) pro různé kombinace sazeb. **Zelená = Případ 1 vítězí. Červená = Případ 2 vítězí.**")

invest_rates  = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
mortgage_rates = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]

def compute_diff(inv_r, mort_r):
    i_  = mort_r / 100 / 12
    s_  = (1 + inv_r / 100) ** (1 / 12) - 1
    a1_ = monthly_payment(P0, i_, N)
    a2_ = monthly_payment(loan2, i_, N)
    da_ = a1_ - a2_
    fv1_ = fv_lump_sum(P_init, s_, N)
    fv2_ = fv_monthly_contributions(da_, s_, N)
    return (fv1_ - fv2_) / 1_000_000  # v milionech

table_data = {}
for mort_r in mortgage_rates:
    col_data = []
    for inv_r in invest_rates:
        col_data.append(compute_diff(inv_r, mort_r))
    table_data[f"{mort_r:.1f}%"] = col_data

sens_df = pd.DataFrame(table_data, index=[f"{r}%" for r in invest_rates])
sens_df.index.name = "Investice →  /  Hypotéka ↓"

def color_cells(val):
    if val > 0:
        intensity = min(val / 5, 1.0)
        r = int(220 - intensity * 80)
        g = int(240 - intensity * 20)
        b = int(220 - intensity * 80)
        return f"background-color: rgb({r},{g},{b}); color: #1a5c1a; font-weight: 600;"
    else:
        intensity = min(-val / 5, 1.0)
        r = int(240 - intensity * 20)
        g = int(220 - intensity * 80)
        b = int(220 - intensity * 80)
        return f"background-color: rgb({r},{g},{b}); color: #5c1a1a; font-weight: 600;"

styled = sens_df.style\
    .map(color_cells)\
    .format("{:+.2f} M")\
    .set_table_styles([
        {"selector": "th", "props": [("background-color", "#1a1f36"), ("color", "white"),
                                      ("font-size", "0.8rem"), ("padding", "8px 12px")]},
        {"selector": "td", "props": [("text-align", "center"), ("padding", "8px 12px"),
                                      ("font-size", "0.85rem")]},
        {"selector": "tr:hover td", "props": [("filter", "brightness(0.95)")]},
    ])

st.dataframe(styled, use_container_width=True)
st.caption(f"Počítáno pro půjčku {fmt(P0)} CZK, vlastní zdroje {fmt(P_init)} CZK, doba {years:.0f} let. Hodnoty v milionech CZK. Zvýrazněný řádek odpovídá zadaným sazbám.")

# ── Math expander ─────────────────────────────────────────────────────────────
with st.expander("Matematické vzorce (rozbalit)"):
    st.markdown("#### Měsíční splátka hypotéky")
    st.latex(r"A = P_0 \cdot \frac{i \cdot (1+i)^N}{(1+i)^N - 1}")
    st.markdown("kde $i$ = měsíční úroková sazba, $N$ = počet měsíců, $P_0$ = výše úvěru")
    st.markdown("#### Budoucí hodnota – jednorázová investice (Případ 1)")
    st.latex(r"FV_1 = P_{init} \cdot (1+s)^N")
    st.markdown("#### Budoucí hodnota – pravidelné měsíční investice (Případ 2)")
    st.latex(r"FV_2 = \Delta A \cdot \frac{(1+s)^N - 1}{s}")
    st.markdown("kde $\\Delta A = A_1 - A_2$ je měsíční úspora díky snížené hypotéce")
    st.markdown("#### Převod na reálnou hodnotu")
    st.latex(r"FV_{reálná} = \frac{FV_{nominální}}{(1 + \pi)^{roky}}")
    st.markdown("Inflace se vyruší v porovnání obou případů — neovlivňuje, která strategie vyhraje.")

st.markdown("---")
st.caption("Zjednodušený model: konstantní sazby, bez daní a poplatků. Výnosnost investice je nominální (před inflací).")
