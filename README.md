# 🎭 CultPulse '26 — College Cultural Fest & Student Aid Portal

> **Hackathon Demo Edition**  
> A full-stack web application designed for collegiate cultural festivals to streamline student event registrations, provide outstation accommodation and logistics aid, and power live campus gate verification.

---

## 🌟 Hackathon Problem Statement & Solution

### ⚠️ The Problem
College cultural festivals bring together thousands of students across institutions for competitions in dance, music, drama, fashion, and esports. However:
1. **Chaotic Registrations**: Disjointed Google Forms and manual spreadsheets lead to double registrations and slot overbooking.
2. **Outstation Student Neglect ("Aid Gap")**: Outstation teams struggle with hostel stays, station shuttles, and musical instrument / prop logistics.
3. **Gate Confusion**: Coordinators lack a unified way to verify entry passes and validate check-in attendance on the day of the fest.

### 💡 The CultPulse Solution
- **Dynamic Event Discovery**: Filter cultural competitions by category (Dance, Music, Theatre, Fashion, Fine Arts, Gaming) with real-time remaining slot counters.
- **Intelligent Registration Form**: Automatically adapts for Solo or Team competitions, enforces unique student roll numbers, and captures outstation hostel and logistics aid requests.
- **Instant Digital E-Pass with Live QR**: Generates an official, verifiable digital pass with unique ID, QR code, and print/PDF-ready formatting.
- **Student Aid & Helpdesk**: Dedicated portal for hostel accommodations, station pick-and-drop shuttles, and prop storage requests.
- **Coordinator Control Center**: Real-time stats dashboard, live search, 1-click gate check-in toggle, and 1-click CSV export for fest organizers.

---

## 🚀 Quick Start Instructions

### 1. Requirements
- Python 3.10+ (Tested on Python 3.14)
- Flask (`pip install flask`)

### 2. Run the App
```bash
python app.py
```
Then open your browser at:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🎯 3-Minute Hackathon Demo Script for Judges

1. **Step 1: Event Showcase (Student View)**
   - Open [http://127.0.0.1:5000](http://127.0.0.1:5000).
   - Show category pills (*Dance, Music, Theatre, Fashion, Gaming*).
   - Point out real-time available slots and prize pool indicators.

2. **Step 2: Smooth Registration & E-Pass Generation**
   - Click **"Register for Event"** on any competition (e.g. *Step Up: Dance Battle* or *Natraj Solo Dance*).
   - Fill in student details: Name, Roll Number, College, and check the **"Request College Hostel Aid"** toggle.
   - Click **Confirm & Generate Digital E-Pass**.
   - Watch the celebratory confetti burst and the generated **Official Digital Pass** with dynamic QR code!
   - Highlight the **"Print / Save PDF"** capability.

3. **Step 3: Duplicate Registration Guard**
   - Try registering again with the exact same Roll No for the same event — show how CultPulse prevents duplicate entries and displays their existing Ticket ID.

4. **Step 4: Student Aid & Helpdesk**
   - Switch to **"Student Aid & FAQ"** tab.
   - Explain the 3 pillars: Free Outstation Hostel, Station Shuttle Tracking, and Prop/Instrument Logistics.
   - Demonstrate submitting a live query.

5. **Step 5: Organizer Hub & Gate Pass Verification (Live Admin View)**
   - Switch to **"Organizer Hub"** tab.
   - Show live analytics counters: Total Registrations, Colleges Represented, Hostel Aid Requests.
   - Enter the Ticket ID (or click **"Check In"** in the table) to simulate gate volunteer verification in real time.
   - Click **"Export CSV Data"** to show instant export for college administrative records.

---

## 🛠️ Tech Stack
- **Backend**: Python 3, Flask, SQLite3 (embedded, zero extra setup).
- **Frontend**: HTML5, Tailwind CSS, Google Fonts (Outfit), FontAwesome icons, Canvas Confetti, QRCode.js.
- **Data Persistence**: Local relational database (`cultpulse.db`) with automatic table creation and seed data.

