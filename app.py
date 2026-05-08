from flask import Flask, render_template, request

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os
from urllib.parse import quote

app = Flask(__name__)

# FD Calculation
def calculate_fd(P, r, t):
    r = r / 100
    return P * (1 + r) ** t

# MF Calculation
def calculate_mf(P, rate, t):
    r = rate / 100
    return P * (1 + r) ** t

# MF Risk Rates
def get_mf_rate(risk):

    if risk == "low":
        return ("Conservative Fund", 10)

    elif risk == "medium":
        return ("Moderate Fund", 12)

    else:
        return ("Aggressive Fund", 14)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/result', methods=['POST'])
def result():

    # USER INPUTS
    name = request.form['name']
    phone = request.form['phone']

    amount = float(request.form['amount'])
    rate = float(request.form['rate'])
    years = int(request.form['years'])

    risk = request.form['risk']

    # SAVE LEADS
    with open("leads.txt", "a") as f:
        f.write(f"{name}, {phone}, {amount}, {years}, {risk}\n")

    # FD VALUE
    fd_value = calculate_fd(amount, rate, years)

    # MF VALUE
    fund_type, mf_rate = get_mf_rate(risk)

    mf_value = calculate_mf(amount, mf_rate, years)

    # SAGEFARM VALUE (20%)
    sagefarm_rate = 20

    sagefarm_value = calculate_mf(amount, sagefarm_rate, years)

    # EXTRA RETURNS
    mf_gain = mf_value - fd_value

    sage_gain = sagefarm_value - fd_value

    # TIME LOGIC

    fd_target = fd_value

    mf_time = 0

    sage_time = 0

    # MF Time
    for t in range(1, years * 12 + 1):

        mf_temp = calculate_mf(amount, mf_rate, t / 12)

        if mf_temp >= fd_target:
            mf_time = t
            break

    # Sagefarm Time
    for t in range(1, years * 12 + 1):

        sage_temp = calculate_mf(amount, sagefarm_rate, t / 12)

        if sage_temp >= fd_target:
            sage_time = t
            break

    fd_time = years * 12

    # TIME SAVED

    time_saved = fd_time - mf_time

    sage_time_saved = fd_time - sage_time

    years_saved = max(time_saved // 12, 0)

    months_saved = max(time_saved % 12, 0)

    sage_years_saved = max(sage_time_saved // 12, 0)

    sage_months_saved = max(sage_time_saved % 12, 0)

    # SPEED FACTORS

    speed_factor = round(fd_time / mf_time, 2)

    sage_speed = round(fd_time / sage_time, 2)

    # =========================
    # GRAPH SECTION
    # =========================

    labels = ['FD', 'Mutual Fund', 'Sagefarm']

    values = [fd_value, mf_value, sagefarm_value]

    colors = ['#ef4444', '#2FA4A9', '#7c3aed']

    plt.figure(figsize=(10, 6))

    bars = plt.bar(
        labels,
        values,
        color=colors,
        width=0.55
    )

    plt.title(
        "FD vs MF vs Sagefarm",
        fontsize=20,
        fontweight='bold'
    )

    plt.ylabel(
        "Final Amount (₹)",
        fontsize=14
    )

    # DYNAMIC SCALE
    max_value = max(values)

    plt.ylim(0, max_value * 1.25)

    # GRID
    plt.grid(
        axis='y',
        linestyle='--',
        alpha=0.3
    )

    # VALUE LABELS
    for bar in bars:

        yval = bar.get_height()

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            yval + (max_value * 0.03),
            f'₹{round(yval):,}',
            ha='center',
            fontsize=11,
            fontweight='bold'
        )

    plt.tick_params(axis='y', labelsize=11)

    plt.tick_params(axis='x', labelsize=12)

    chart_path = os.path.join("static", f"chart_{name}.png")

    plt.tight_layout()

    plt.savefig(chart_path, dpi=200)

    plt.close()

    # =========================
    # PROFESSIONAL WHATSAPP MESSAGE
    # =========================

    message = f"""
Hello Sagefarm Team 👋

My name is {name}.

I recently compared my Fixed Deposit returns with Mutual Fund and Sagefarm growth projections on your platform.

📌 Investment Details:
• Investment Amount: ₹{amount:,.0f}
• Duration: {years} Years
• FD Rate: {rate}%

📊 Comparison Results:
• FD Final Value: ₹{fd_value:,.0f}
• Mutual Fund Value ({mf_rate}%): ₹{mf_value:,.0f}
• Sagefarm Strategy Value (20%): ₹{sagefarm_value:,.0f}

🚀 Additional Wealth Generated:
• Mutual Fund Extra Gain: ₹{mf_gain:,.0f}
• Sagefarm Extra Gain: ₹{sage_gain:,.0f}

⏳ Time Advantage:
• MF reaches the same goal {years_saved} years {months_saved} months earlier
• Sagefarm reaches the same goal {sage_years_saved} years {sage_months_saved} months earlier

Please guide me further regarding the best investment strategy suitable for my goals.

Thank you.
"""

    whatsapp_url = "https://wa.me/918433726774?text=" + quote(message)

    # RETURN RESULT PAGE

    return render_template(

        "result.html",

        fd=round(fd_value, 0),

        mf=round(mf_value, 0),

        sagefarm=round(sagefarm_value, 0),

        mf_gain=round(mf_gain, 0),

        sage_gain=round(sage_gain, 0),

        fund=fund_type,

        mf_rate=mf_rate,

        years_saved=years_saved,

        months_saved=months_saved,

        sage_years_saved=sage_years_saved,

        sage_months_saved=sage_months_saved,

        speed_factor=speed_factor,

        sage_speed=sage_speed,

        chart=chart_path.replace("\\", "/"),

        whatsapp_url=whatsapp_url
    )


if __name__ == "__main__":
    app.run(debug=True)
