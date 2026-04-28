from flask import Flask, render_template, request

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from urllib.parse import quote

app = Flask(__name__)

def calculate_fd(P, r, t):
    r = r / 100
    return P * (1 + r) ** t

def calculate_mf(P, rate, t):
    r = rate / 100
    return P * (1 + r) ** t

def get_mf_rate(risk):
    if risk == "low":
        return ("Debt Fund (Short-term Avg)", 7.5)
    elif risk == "medium":
        return ("Hybrid Fund (Balanced Avg)", 11)
    else:
        return ("Equity Fund (Long-term Avg)", 14)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    amount = float(request.form['amount'])
    rate = float(request.form['rate'])
    years = int(request.form['years'])
    risk = request.form['risk']

    # NEW: Lead capture
    name = request.form['name']
    phone = request.form['phone']

    # Save leads
    with open("leads.txt", "a") as f:
        f.write(f"{name}, {phone}, {amount}, {years}, {risk}\n")

    fd_value = calculate_fd(amount, rate, years)
    fund_type, mf_rate = get_mf_rate(risk)
    mf_value = calculate_mf(amount, mf_rate, years)

    gain = mf_value - fd_value

    # TIME LOGIC
    fd_target = fd_value
    mf_time = 0

    for t in range(1, years * 12 + 1):
        mf_temp = calculate_mf(amount, mf_rate, t / 12)
        if mf_temp >= fd_target:
            mf_time = t
            break

    fd_time = years * 12
    time_saved = fd_time - mf_time

    years_saved = max(time_saved // 12, 0)
    months_saved = max(time_saved % 12, 0)

    # SPEED FACTOR
    speed_factor = round(fd_time / mf_time, 2) if mf_time > 0 else 1

    # GRAPH
    labels = ['FD', 'Mutual Fund']
    values = [fd_value, mf_value]

    plt.figure()
    plt.bar(labels, values)
    plt.title("FD vs Mutual Fund")

    chart_path = os.path.join("static", "chart.png")
    plt.savefig(chart_path)
    plt.close()

    # NEW: WhatsApp message
    message = f"Hi, I'm {name}. I checked FD vs MF.\nFD: ₹{round(fd_value)}\nMF: ₹{round(mf_value)}\nPlease guide me."
    whatsapp_url = "https://wa.me/918433726774?text=" + quote(message)

    return render_template("result.html",
                           fd=round(fd_value, 0),
                           mf=round(mf_value, 0),
                           gain=round(gain, 0),
                           fund=fund_type,
                           years_saved=years_saved,
                           months_saved=months_saved,
                           speed_factor=speed_factor,
                           mf_rate=mf_rate,
                           chart=chart_path,
                           whatsapp_url=whatsapp_url)

if __name__ == "__main__":
    app.run(debug=True)