import streamlit as st
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
import io

# Set up the web page configurations (Responsive title and layout)
st.set_page_config(
    page_title="TrueWage Engine & Financial Tracker",
    page_icon="💰",
    layout="centered", # Keeps it looking tight and clean on both phones and PCs
)

# Custom CSS styling to give it that modern dark look matching your audience
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    .stNumberInput, .stSelectbox { margin-bottom: 10px; }
    h1, h2, h3 { color: #38bdf8 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 1. MATHEMATICAL LOGIC FUNCTIONS ---

def format_money(amount):
    return f"${amount:,.2f}"

def calc_paycheck(paytype, hours, hourly_wage, salary, tax_rate):
    if paytype == "Hourly":
        reg_hours = min(hours, 40)
        ot_hours = max(hours - 40, 0)
        reg_pay = hourly_wage * reg_hours
        ot_pay = hourly_wage * 1.5 * ot_hours
        gross_weekly = reg_pay + ot_pay
        annual_gross = gross_weekly * 52
    else:
        annual_gross = salary
        gross_weekly = salary / 52 if hours != 0 else 0
        hourly_wage = gross_weekly / hours if hours != 0 else 0
        reg_hours = min(hours, 40)
        ot_hours = max(hours - 40, 0)
        reg_pay = hourly_wage * reg_hours
        ot_pay = hourly_wage * 1.5 * ot_hours

    monthly_gross = annual_gross / 12
    net_hourly = hourly_wage * (1 - tax_rate/100)
    weekly_tax = gross_weekly * tax_rate/100
    net_weekly = gross_weekly - weekly_tax
    annual_tax = weekly_tax * 52
    annual_net = annual_gross - annual_tax
    monthly_tax = annual_tax / 12
    monthly_net = monthly_gross - monthly_tax

    return {
        "gross_hourly": hourly_wage,
        "net_hourly": net_hourly,
        "gross_weekly": gross_weekly,
        "reg_pay": reg_pay,
        "ot_pay": ot_pay,
        "weekly_tax": weekly_tax,
        "net_weekly": net_weekly,
        "annual_gross": annual_gross,
        "annual_tax": annual_tax,
        "annual_net": annual_net,
        "monthly_gross": monthly_gross,
        "monthly_tax": monthly_tax,
        "monthly_net": monthly_net,
        "reg_hours": reg_hours,
        "ot_hours": ot_hours,
    }

def calc_savings(monthly_contrib, principal, rate, years):
    months = int(years * 12)
    rate_decimal = rate / 100
    if months == 0:
        return principal, 0, 0, [principal]
    r_monthly = rate_decimal / 12
    balance = principal
    total_contrib = principal
    growth = [balance]
    for _ in range(months):
        balance = balance * (1 + r_monthly) + monthly_contrib
        total_contrib += monthly_contrib
        growth.append(balance)
    total_interest = balance - total_contrib
    return balance, total_contrib, total_interest, growth

# --- 2. WEB APP USER INTERFACE ---

# Display branding image logo cleanly if it exists, otherwise use modern text
try:
    st.image("F.png", width=120)
except Exception:
    st.title("💰 TrueWage Engine")

st.markdown("### Know your *real* worth after taxes & plan your future.")
st.write("---")

# Layout: Split inputs into two clean expanding panels/sections
with st.expander("💼 Step 1: Your Job Profile", expanded=True):
    paytype = st.selectbox("Payment Structure", ["Hourly", "Salary"])
    
    # Dynamically toggle input boxes just like your old Tkinter app!
    if paytype == "Hourly":
        hourly_wage = st.number_input("Hourly Wage ($)", min_value=0.0, value=15.0, step=0.50)
        salary = 0.0
    else:
        salary = st.number_input("Annual Salary ($)", min_value=0.0, value=45000.0, step=1000.0)
        hourly_wage = 0.0
        
    hours = st.number_input("Hours Worked Per Week", min_value=0.0, value=40.0, step=1.0)
    tax_rate = st.number_input("Estimated Tax Rate (%)", min_value=0.0, max_value=100.0, value=20.0, step=1.0)

with st.expander("📈 Step 2: Wealth Multiplier Settings", expanded=True):
    principal = st.number_input("Initial Bank Balance / Starting Capital ($)", min_value=0.0, value=0.0, step=100.0)
    save_pct = st.number_input("Percent of Income to Save/Invest (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
    interest = st.number_input("Annual APY / Investment Return Rate (%)", min_value=0.0, value=7.0, step=0.5)
    years = st.number_input("Growth Timeline (Years)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)

# Run calculations instantly when variables tweak
paycheck = calc_paycheck(paytype, hours, hourly_wage, salary, tax_rate)
monthly_contrib = paycheck["monthly_gross"] * save_pct / 100
balance, total_contrib, total_interest, growth = calc_savings(monthly_contrib, principal, interest, years)

# --- 3. SHOW REAL-TIME RESULTS ---
st.write("---")
st.subheader("📊 Your Live Financial Breakdown")

# Visual Callout Metrics for Mobile
col1, col2 = st.columns(2)
with col1:
    st.metric(label="★ REAL NET WAGE", value=f"{format_money(paycheck['net_hourly'])} / hr")
with col2:
    st.metric(label="★ FUTURE NEST EGG", value=format_money(balance))

# Layout Side-by-Side breakdown boxes using code markdown format
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Take-Home Details")
    results_txt = (
        f"Gross Hourly Offer: {format_money(paycheck['gross_hourly'])}\n"
        f"Regular Hours: {paycheck['reg_hours']} | Overtime: {paycheck['ot_hours']}\n"
        f"Regular Base Pay: {format_money(paycheck['reg_pay'])}\n"
        f"Overtime Extra Pay: {format_money(paycheck['ot_pay'])}\n"
        f"Weekly Take-Home: {format_money(paycheck['net_weekly'])}\n"
        f"Monthly Take-Home: {format_money(paycheck['monthly_net'])}\n"
        f"Annual Net Wealth: {format_money(paycheck['annual_net'])}\n"
        f"Annual Taxes Taken: {format_money(paycheck['annual_tax'])}"
    )
    st.code(results_txt, language="text")

with col_right:
    st.markdown("#### Savings Blueprint")
    savings_txt = (
        f"Initial Bank Deposit: {format_money(principal)}\n"
        f"Auto-Savings Plan: {save_pct:.1f}% of gross\n"
        f"Monthly Stash Amount: {format_money(monthly_contrib)}\n"
        f"Out-of-Pocket Deposits: {format_money(total_contrib)}\n"
        f"Free Interest Growth: {format_money(total_interest)}"
    )
    st.code(savings_txt, language="text")

# --- 4. EMBED GRAPH TREND DIRECTLY IN PAGE ---
st.write("---")
st.markdown("#### Wealth Accumulation Trend")
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(7, 3.5))
ax.plot(np.arange(len(growth))/12, growth, color='#0ea5e9', linewidth=2.5)
ax.set_xlabel("Timeline (Years)", fontsize=9)
ax.set_ylabel("Account Balance ($)", fontsize=9)
ax.grid(True, linestyle='--', alpha=0.2)
plt.tight_layout()
st.pyplot(fig) # Embeds the matplotlib object seamlessly into the website structure

# --- 5. HANDLING MOBILE PDF EXPORT GENERATION ---
# Instead of opening a saving desktop popup box, mobile browsers expect file streams downloads:
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=16)
pdf.cell(0, 12, "Real Income & Wealth Forecast Report", ln=True, align='C')
pdf.set_font("Arial", size=12)
pdf.ln(5)
pdf.cell(0, 10, f"REAL NET WAGE: {format_money(paycheck['net_hourly'])} / hr", ln=True)
pdf.cell(0, 10, f"FUTURE NEST EGG: {format_money(balance)}", ln=True)

# Generate PDF to binary memory string buffer stream
pdf_buffer = io.BytesIO()
pdf_string = pdf.output(dest='S').encode('latin1') # output as string, convert to bytes
pdf_buffer.write(pdf_string)
pdf_buffer.seek(0)

st.download_button(
    label="📥 Download Professional Job PDF Report",
    data=pdf_buffer,
    file_name="TrueWage_Financial_Report.pdf",
    mime="application/pdf",
    use_container_width=True
)