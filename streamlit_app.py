import streamlit as st
import requests
import random
import time

# Initialize session state
if 'lockers' not in st.session_state:
    st.session_state.lockers = {
        "locker1": {"status":"free","assignedRoll":None,"pin":None,"timer":0},
        "locker2": {"status":"free","assignedRoll":None,"pin":None,"timer":0},
        "locker3": {"status":"free","assignedRoll":None,"pin":None,"timer":0}
    }

if 'otp_store' not in st.session_state:
    st.session_state.otp_store = {}

if 'otp_verified' not in st.session_state:
    st.session_state.otp_verified = False

# --- App Title ---
st.title("Get Locked With Us")

# --- Roll number input (manual) ---
roll_number = st.text_input("Enter your Roll Number:")

if roll_number:
    email = f"{roll_number}@anurag.edu.in"
    st.write(f"Email: {email}")

    # --- Check if locker already assigned ---
    assigned_locker = None
    for lid, locker in st.session_state.lockers.items():
        if locker['assignedRoll']==roll_number:
            assigned_locker = lid
            break

    if assigned_locker:
        st.warning(f"Locker already assigned: {assigned_locker}")
        # Unlocking workflow
        st.subheader("Unlock Locker")
        unlock_pin = st.text_input("Enter PIN to unlock", type="password", key="unlock_pin")
        if st.button("Unlock Locker"):
            locker = st.session_state.lockers[assigned_locker]
            if locker["pin"] == unlock_pin:
                locker["status"] = "free"
                locker["assignedRoll"] = None
                locker["pin"] = None
                locker["timer"] = 0
                st.success(f"{assigned_locker} unlocked!")
                st.experimental_rerun()  # Refresh page to show updated locker status
            else:
                st.error("Wrong PIN")
    else:
        # OTP Workflow
        if st.button("Send OTP"):
            otp = str(random.randint(100000,999999))
            st.session_state.otp_store[roll_number] = otp
            # Send OTP via Google Script
            script_url = "https://script.google.com/macros/s/AKfycbzFWZSa6P0D_u2Yz5nfkuctrA563mRAK8QQxzkwCrGf9Cjlj5-u9eTiC6CZkXmR_jbV/exec"
            try:
                requests.post(script_url, json={"email": email, "otp": otp})
                st.success(f"OTP sent to {email}")
            except Exception as e:
                st.error(f"Error sending OTP: {e}")

        otp_input = st.text_input("Enter OTP", key="otp_input")
        if st.button("Verify OTP"):
            if st.session_state.otp_store.get(roll_number) == otp_input:
                st.success("OTP verified!")
                st.session_state.otp_verified = True
            else:
                st.error("Invalid OTP")

        # PIN creation & locker assignment
        if st.session_state.otp_verified:
            pin = st.text_input("Enter PIN", type="password", key="pin")
            pin_confirm = st.text_input("Re-enter PIN", type="password", key="pin_confirm")
            if st.button("Lock Locker"):
                if not pin or pin != pin_confirm:
                    st.error("PINs do not match")
                else:
                    # Assign first free locker
                    assigned = False
                    for lid, locker in st.session_state.lockers.items():
                        if locker["status"] == "free":
                            locker["status"] = "locked"
                            locker["assignedRoll"] = roll_number
                            locker["pin"] = pin
                            locker["timer"] = 3.5 * 60 * 60  # 3.5 hours
                            st.success(f"Locker assigned: {lid}")
                            assigned = True
                            st.experimental_rerun()  # Refresh page to show updated locker status
                            break
                    if not assigned:
                        st.error("All lockers are occupied")

# --- Display Locker Status ---
st.subheader("Lockers Status")
for lid, locker in st.session_state.lockers.items():
    col1, col2 = st.columns([2,3])
    with col1:
        st.write(f"**{lid}**")
        st.write(f"Status: {locker['status']}")
    with col2:
        if locker["status"] == "locked" and locker["timer"] > 0:
            # Display countdown
            hours = int(locker["timer"] // 3600)
            minutes = int((locker["timer"] % 3600) // 60)
            seconds = int(locker["timer"] % 60)
            st.write(f"Countdown: {hours:02d}:{minutes:02d}:{seconds:02d}")
