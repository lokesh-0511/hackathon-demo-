function goToRegister() {
    document.getElementById("register").scrollIntoView({
        behavior: "smooth"
    });
}

// Live Backend Integration for SRK FEST 2027
document.getElementById("registrationForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const form = this;
    const inputs = form.querySelectorAll("input");
    const selects = form.querySelectorAll("select");
    const submitBtn = form.querySelector("button[type='submit']");

    const name = inputs[0].value.trim();
    const rollNo = inputs[1].value.trim();
    const branch = selects[0].value;
    const mobile = inputs[2].value.trim();
    const email = inputs[3].value.trim();
    const selectedEvent = selects[1].value;

    if (!selectedEvent) {
        alert("Please select an event.");
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerText = "Registering...";

    const payload = {
        name: name,
        roll_no: rollNo,
        branch: branch,
        mobile: mobile,
        email: email,
        event: selectedEvent
    };

    try {
        const response = await fetch("/api/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        submitBtn.disabled = false;
        submitBtn.innerText = "Register";

        if (data.success) {
            const ticket = data.ticket;
            showPassModal(ticket);
            form.reset();
        } else {
            alert("⚠️ Registration Failed:\n" + data.message);
        }
    } catch (err) {
        submitBtn.disabled = false;
        submitBtn.innerText = "Register";
        console.error("Backend connection error:", err);
        alert("⚠️ Could not connect to the backend server. Make sure Python app.py is running on port 5000.");
    }
});

// Show Digital Pass Popup
function showPassModal(ticket) {
    let modal = document.getElementById("pass-modal-srk");
    if (!modal) {
        modal = document.createElement("div");
        modal.id = "pass-modal-srk";
        modal.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,30,70,0.85);display:flex;align-items:center;justify-content:center;z-index:9999;padding:15px;";
        document.body.appendChild(modal);
    }

    modal.innerHTML = `
        <div style="background:white;color:#172b4d;padding:25px;border-radius:14px;max-width:440px;width:100%;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,0.3);border:2px solid #0756b5;font-family:Arial,sans-serif;">
            <div style="font-size:24px;color:#0756b5;font-weight:bold;margin-bottom:5px;">SRK FEST 2027</div>
            <div style="font-size:12px;color:#666;text-transform:uppercase;letter-spacing:1px;margin-bottom:15px;">Official Festival Entry Pass</div>
            
            <div style="background:#f0f6ff;padding:12px;border-radius:8px;border:1px dashed #0756b5;margin-bottom:15px;">
                <div style="font-size:11px;color:#666;">TICKET ID</div>
                <div style="font-size:20px;font-weight:bold;color:#0756b5;font-family:monospace;">${ticket.ticket_id}</div>
            </div>

            <div style="text-align:left;font-size:13px;line-height:1.6;margin-bottom:15px;background:#fafafa;padding:12px;border-radius:8px;">
                <div><strong>Participant:</strong> ${ticket.name}</div>
                <div><strong>Roll Number:</strong> ${ticket.roll_no}</div>
                <div><strong>Branch:</strong> ${ticket.branch}</div>
                <div><strong>Event:</strong> ${ticket.event_title}</div>
                <div><strong>Venue:</strong> ${ticket.venue}</div>
                <div><strong>Schedule:</strong> ${ticket.date_time}</div>
            </div>

            <div style="margin-bottom:15px;">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=${encodeURIComponent(ticket.ticket_id)}" alt="QR Code" style="border:1px solid #ddd;padding:4px;border-radius:6px;">
            </div>

            <button onclick="document.getElementById('pass-modal-srk').style.display='none'" style="background:#0756b5;color:white;padding:10px 25px;border:none;border-radius:6px;cursor:pointer;font-weight:bold;">Close Pass</button>
            <button onclick="window.print()" style="background:#28a745;color:white;padding:10px 25px;border:none;border-radius:6px;cursor:pointer;font-weight:bold;margin-left:8px;">Print Pass</button>
        </div>
    `;

    modal.style.display = "flex";
}
