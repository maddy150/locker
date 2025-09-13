let roll = null;
const rollSpan = document.getElementById('roll');
const emailSpan = document.getElementById('email');
const otpSection = document.getElementById('otp-section');
const pinSection = document.getElementById('pin-section');
const unlockSection = document.getElementById('unlock-section');

// Manual input
document.getElementById('manual-submit').addEventListener('click',()=>{
  const r = document.getElementById('manual-roll').value.trim();
  if(!r) return;
  handleRoll(r);
});

// Camera scan
document.getElementById('scan-btn').addEventListener('click',()=>{
  const html5QrcodeScanner = new Html5QrcodeScanner("reader",{fps:15,qrbox:300});
  html5QrcodeScanner.render((decodedText)=>{
    handleRoll(decodedText.trim());
    html5QrcodeScanner.clear();
  });
});

function handleRoll(r){
  roll = r;
  rollSpan.innerText = r;
  emailSpan.innerText = r+"@anurag.edu.in";

  fetch("/check_roll",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({roll:r})
  }).then(res=>res.json()).then(data=>{
    if(data.assigned_locker){
      unlockSection.classList.remove('hidden');
      pinSection.classList.add('hidden');
      otpSection.classList.add('hidden');
      document.getElementById('locker-unlock').value = data.assigned_locker;
    } else {
      fetch("/send_otp",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({roll:r})
      }).then(()=>otpSection.classList.remove('hidden'));
    }
  });
}

// OTP Verification
document.getElementById('verify-otp').addEventListener('click',()=>{
  const otp = document.getElementById('otp-input').value.trim();
  fetch("/verify_otp",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({roll:roll,otp:otp})
  }).then(res=>res.json()).then(data=>{
    if(data.status=="verified"){
      otpSection.classList.add('hidden');
      pinSection.classList.remove('hidden');
    } else alert("Incorrect OTP");
  });
});

// Locking
document.getElementById('lock-btn').addEventListener('click',()=>{
  const pin = document.getElementById('pin').value.trim();
  const pin2 = document.getElementById('pin-confirm').value.trim();
  if(!pin || pin!==pin2){ alert("Pins do not match"); return; }
  fetch("/assign_locker",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({roll:roll,pin:pin})
  }).then(res=>res.json()).then(data=>{
    if(data.status=="assigned"){
      alert("Locker assigned: "+data.locker);
      pinSection.classList.add('hidden');
    } else alert("All lockers occupied");
  });
});

// Unlocking
document.getElementById('unlock-btn').addEventListener('click',()=>{
  const locker = document.getElementById('locker-unlock').value.trim();
  const pin = document.getElementById('pin-unlock').value.trim();
  fetch("/unlock_locker",{
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body:JSON.stringify({locker:locker,pin:pin})
  }).then(res=>res.json()).then(data=>{
    if(data.status=="unlocked") alert("Locker unlocked!");
    else alert("Wrong PIN");
  });
});
