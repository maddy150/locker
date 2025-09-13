from flask import Flask, render_template, request, jsonify
import random
import threading
import time
import requests

app = Flask(__name__)

# Locker data
lockers = {
    "locker1": {"status":"free","assignedRoll":None,"pin":None,"timer":None},
    "locker2": {"status":"free","assignedRoll":None,"pin":None,"timer":None},
    "locker3": {"status":"free","assignedRoll":None,"pin":None,"timer":None}
}

# OTP store
otp_store = {}

# Countdown timer function
def start_countdown(locker_id, seconds):
    def countdown():
        while seconds > 0:
            lockers[locker_id]['timer'] = seconds
            time.sleep(1)
            seconds -= 1
        lockers[locker_id]['status'] = 'free'
        lockers[locker_id]['assignedRoll'] = None
        lockers[locker_id]['pin'] = None
        lockers[locker_id]['timer'] = None
    t = threading.Thread(target=countdown)
    t.start()

@app.route("/")
def index():
    return render_template("index.html", lockers=lockers)

@app.route("/check_roll", methods=["POST"])
def check_roll():
    roll = request.json.get("roll")
    assigned = None
    for lid,data in lockers.items():
        if data['assignedRoll']==roll:
            assigned = lid
            break
    return jsonify({"assigned_locker":assigned})

@app.route("/send_otp", methods=["POST"])
def send_otp():
    roll = request.json.get("roll")
    email = f"{roll}@anurag.edu.in"
    otp = str(random.randint(100000,999999))
    otp_store[roll] = otp

    # Send OTP via Google Script
    script_url = "https://script.google.com/macros/s/AKfycbzFWZSa6P0D_u2Yz5nfkuctrA563mRAK8QQxzkwCrGf9Cjlj5-u9eTiC6CZkXmR_jbV/exec"
    payload = {"email": email, "otp": otp}
    try:
        requests.post(script_url, json=payload)
    except Exception as e:
        print("Error sending OTP:", e)

    return jsonify({"status":"sent"})

@app.route("/verify_otp", methods=["POST"])
def verify_otp():
    roll = request.json.get("roll")
    otp_input = request.json.get("otp")
    if otp_store.get(roll) == otp_input:
        return jsonify({"status":"verified"})
    return jsonify({"status":"invalid"})

@app.route("/assign_locker", methods=["POST"])
def assign_locker():
    roll = request.json.get("roll")
    pin = request.json.get("pin")
    for lid,data in lockers.items():
        if data['status']=="free":
            data['status']="locked"
            data['assignedRoll']=roll
            data['pin']=pin
            start_countdown(lid, int(3.5*60*60))
            return jsonify({"status":"assigned","locker":lid})
    return jsonify({"status":"full"})

@app.route("/unlock_locker", methods=["POST"])
def unlock_locker():
    locker_id = request.json.get("locker")
    pin = request.json.get("pin")
    if lockers[locker_id]['pin']==pin:
        lockers[locker_id]['status']="free"
        lockers[locker_id]['assignedRoll']=None
        lockers[locker_id]['pin']=None
        lockers[locker_id]['timer']=None
        return jsonify({"status":"unlocked"})
    return jsonify({"status":"wrong_pin"})

if __name__=="__main__":
    app.run(debug=True)
