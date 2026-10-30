"""
Database setup and seed data for CultPulse - College Cultural Fest & Aid Portal.
Uses standard Python sqlite3 library for zero external DB dependency.
"""
import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'cultpulse.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create Events Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            team_type TEXT NOT NULL, -- Solo / Duet / Group (3-10)
            max_team_size INTEGER DEFAULT 1,
            date_time TEXT NOT NULL,
            venue TEXT NOT NULL,
            prize_pool TEXT NOT NULL,
            rules TEXT NOT NULL,
            coordinator_name TEXT NOT NULL,
            coordinator_contact TEXT NOT NULL,
            max_slots INTEGER DEFAULT 30,
            image_url TEXT,
            status TEXT DEFAULT 'Open' -- Open / Filling Fast / Closed
        )
    ''')

    # Create Registrations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            event_id INTEGER NOT NULL,
            event_title TEXT NOT NULL,
            student_name TEXT NOT NULL,
            roll_no TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            college_name TEXT NOT NULL,
            department TEXT NOT NULL,
            year_of_study TEXT NOT NULL,
            team_name TEXT,
            team_members TEXT, -- JSON or comma separated string
            needs_hostel_aid INTEGER DEFAULT 0, -- 1 for Yes, 0 for No
            special_requirements TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checked_in INTEGER DEFAULT 0,
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')

    # Create Aid / Helpdesk Requests Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS helpdesk_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            contact_info TEXT NOT NULL,
            college_name TEXT NOT NULL,
            category TEXT NOT NULL, -- Accommodation / Travel / Props & Audio / Schedule
            query_text TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Check if events already seeded
    cursor.execute('SELECT COUNT(*) FROM events')
    count = cursor.fetchone()[0]

    if count == 0:
        seed_events = [
            (
                "Step Up: Western & Hip-Hop Dance Battle",
                "Dance",
                "Showcase high-energy crew choreography and power-packed individual freestyle moves on the main stage.",
                "Group (4-12)",
                12,
                "Day 1 - 2:00 PM to 5:00 PM",
                "Main Auditorium Stage",
                "Rs. 25,000",
                "Time limit: 6-8 minutes. Track must be submitted 2 hrs prior. Props allowed with prior safety approval.",
                "Rohan Verma",
                "+91 98765 43210",
                25,
                "https://images.unsplash.com/photo-1547153760-18fc86324498?w=700&q=80",
                "Filling Fast"
            ),
            (
                "Battle of the Bands: Sound Clash",
                "Music",
                "Live rock, fusion, and indie band competition. Bring your original riffs and electrifying crowd-pleasers.",
                "Group (3-8)",
                8,
                "Day 1 - 6:00 PM to 10:00 PM",
                "Open Air Amphitheatre",
                "Rs. 35,000",
                "15 minutes slot including 3 mins sound check. Drum kit provided. Bring your own guitars and processors.",
                "Ananya Sharma",
                "+91 98111 22334",
                15,
                "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=700&q=80",
                "Open"
            ),
            (
                "Natraj: Classical Solo Dance",
                "Dance",
                "Expressive storytelling and rhythm through Bharatanatyam, Kathak, Odissi, and other Indian classical dance forms.",
                "Solo",
                1,
                "Day 2 - 10:00 AM to 1:00 PM",
                "Seminar Hall A",
                "Rs. 15,000",
                "Performance duration: 7 minutes max. Live orchestra or recorded track permitted. Classical costume mandatory.",
                "Dr. Meera Iyer",
                "+91 98220 54321",
                20,
                "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=700&q=80",
                "Open"
            ),
            (
                "Nukkad Natak: Street Play & Drama",
                "Theatre",
                "Raise your voice on impactful social themes with catchy slogans, dholaks, and synchronized dramatics.",
                "Group (8-20)",
                20,
                "Day 2 - 11:30 AM to 3:30 PM",
                "Central Quadrangle Ground",
                "Rs. 20,000",
                "Time limit: 12-15 minutes. No microphones provided. Only acoustic instruments (Dholak, Harmonium, Gulal) permitted.",
                "Kabir Sen",
                "+91 98450 67890",
                12,
                "https://images.unsplash.com/photo-1460723237483-7a6dc9d0b212?w=700&q=80",
                "Open"
            ),
            (
                "Vogue Vista: The Cultural Runway",
                "Fashion",
                "A thematic fashion walk celebrating Indo-Western couture, sustainability, and avant-garde designs.",
                "Group (10-16)",
                16,
                "Day 2 - 6:30 PM to 9:30 PM",
                "Grand Arena",
                "Rs. 40,000",
                "Time limit: 10 minutes. Theme explanation narration allowed. Green rooms and steam irons will be provided.",
                "Pooja Hegde",
                "+91 99000 11223",
                10,
                "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=700&q=80",
                "Filling Fast"
            ),
            (
                "Canvas Clash: Live Digital & Acrylic Art",
                "Fine Arts",
                "Unleash your visual creativity live on theme revealed on the spot. Digital tablets and canvas easels supported.",
                "Solo",
                1,
                "Day 1 - 11:00 AM to 2:00 PM",
                "Design Studio Block 3",
                "Rs. 10,000",
                "Canvas provided (18x24 inches). Bring your own paints/brushes or iPad. Theme announced at 10:45 AM.",
                "Vikram Patel",
                "+91 97654 32190",
                30,
                "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=700&q=80",
                "Open"
            ),
            (
                "Voice of Campus: Solo Singing (Eastern & Western)",
                "Music",
                "Mesmerize the audience with your vocal control, pitch, and emotive melody.",
                "Solo",
                1,
                "Day 1 - 3:00 PM to 6:00 PM",
                "Mini Auditorium",
                "Rs. 12,000",
                "Time limit: 4 minutes. Karaoke backing track or single acoustic accompanist allowed.",
                "Neha Rao",
                "+91 98333 44556",
                35,
                "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=700&q=80",
                "Open"
            ),
            (
                "Battleground Blitz: Valorant & BGMI LAN Arena",
                "Gaming",
                "Compete against collegiate esports champions in a high-octane 5v5 tactical shooter tournament.",
                "Group (5)",
                5,
                "Day 2 - 10:00 AM to 6:00 PM",
                "Computing Center 1",
                "Rs. 20,000",
                "LAN setup provided with 144Hz monitors. Players may bring personal mouse, keyboard, and headsets.",
                "Aditya Roy",
                "+91 98888 77766",
                16,
                "https://images.unsplash.com/photo-1542751371-adc38448a05e?w=700&q=80",
                "Filling Fast"
            )
        ]

        cursor.executemany('''
            INSERT INTO events (
                title, category, description, team_type, max_team_size,
                date_time, venue, prize_pool, rules, coordinator_name,
                coordinator_contact, max_slots, image_url, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', seed_events)

        # Also add 2 sample registrations for realistic demo presentation
        sample_regs = [
            (
                "PASS-DNC-8492", 1, "Step Up: Western & Hip-Hop Dance Battle",
                "Aarav Mehta", "21CS042", "aarav.m@college.edu", "+91 98765 00001",
                "St. Xavier's Institute", "Computer Science", "3rd Year",
                "Urban Groovers Crew", "Aarav Mehta, Riya Joshi, Kunal Bose, Simran Kaur",
                1, "Requesting girls & boys separate hostel accommodation for 1 night."
            ),
            (
                "PASS-MUS-1029", 2, "Battle of the Bands: Sound Clash",
                "Devansh Sen", "22EC019", "devansh.band@sound.org", "+91 98111 88888",
                "National Institute of Technology", "Electronics", "2nd Year",
                "Echoes of Horizon", "Devansh Sen, Tanmay Bhatia, Kevin Joseph, Alok Nair",
                0, "Drum kit setup required with double bass pedal."
            )
        ]

        cursor.executemany('''
            INSERT INTO registrations (
                ticket_id, event_id, event_title, student_name, roll_no,
                email, phone, college_name, department, year_of_study,
                team_name, team_members, needs_hostel_aid, special_requirements
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_regs)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("CultPulse Database initialized successfully.")

