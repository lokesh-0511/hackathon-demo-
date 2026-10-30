"""
CultPulse - College Cultural Fest Registration & Student Aid Portal
Hackathon Demo Application Backend
"""
import os
import uuid
import csv
import io
import sqlite3
from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from database import init_db, get_db_connection

app = Flask(__name__)
app.secret_key = 'cultpulse-hackathon-supersecret-key'

# Enable CORS so any frontend (friend's laptop, Live Server, React/Vite) can connect
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        return response

# Ensure DB is created on launch
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/srk')
@app.route('/friend')
def friend_portal():
    return send_from_directory('friend_frontend', 'index.html')

@app.route('/style.css')
def friend_css():
    return send_from_directory('friend_frontend', 'style.css')

@app.route('/script.js')
def friend_js():
    return send_from_directory('friend_frontend', 'script.js')

@app.route('/friend_frontend/<path:filename>')
def friend_static_assets(filename):
    return send_from_directory('friend_frontend', filename)

@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db_connection()
    query = '''
        SELECT e.*, COUNT(r.id) as registered_count
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        GROUP BY e.id
        ORDER BY e.id ASC
    '''
    events = conn.execute(query).fetchall()
    conn.close()

    events_list = []
    for e in events:
        events_list.append({
            "id": e["id"],
            "title": e["title"],
            "category": e["category"],
            "description": e["description"],
            "team_type": e["team_type"],
            "max_team_size": e["max_team_size"],
            "date_time": e["date_time"],
            "venue": e["venue"],
            "prize_pool": e["prize_pool"],
            "rules": e["rules"],
            "coordinator_name": e["coordinator_name"],
            "coordinator_contact": e["coordinator_contact"],
            "max_slots": e["max_slots"],
            "registered_count": e["registered_count"],
            "slots_left": max(0, e["max_slots"] - e["registered_count"]),
            "image_url": e["image_url"],
            "status": "Housefull" if e["registered_count"] >= e["max_slots"] else e["status"]
        })

    return jsonify({"success": True, "events": events_list})

@app.route('/api/register', methods=['POST'])
def register_student():
    data = request.get_json() or {}

    # Extract student details (supporting both naming conventions)
    student_name = (data.get('student_name') or data.get('name') or '').strip()
    roll_no = (data.get('roll_no') or data.get('roll_number') or '').strip()
    branch = (data.get('branch') or data.get('department') or '').strip()
    mobile = (data.get('mobile') or data.get('phone') or '').strip()
    event_id = data.get('event_id') or data.get('event')

    # Optional / defaulted fields
    college_name = (data.get('college_name') or 'Main University Campus').strip()
    email = (data.get('email') or f"{roll_no or 'student'}@college.edu").strip()
    year_of_study = (data.get('year_of_study') or 'Undergraduate').strip()
    team_name = (data.get('team_name') or '').strip()
    team_members = (data.get('team_members') or '').strip()
    needs_hostel = 1 if data.get('needs_hostel_aid') in [True, 1, '1', 'yes', 'true'] else 0
    special_requirements = (data.get('special_requirements') or '').strip()

    # Core Validation: name, roll no, branch, mobile, event selection
    if not event_id:
        return jsonify({"success": False, "message": "Event selection is required."}), 400
    if not student_name:
        return jsonify({"success": False, "message": "Student Name is required."}), 400
    if not roll_no:
        return jsonify({"success": False, "message": "Roll Number / USN is required."}), 400
    if not branch:
        return jsonify({"success": False, "message": "Branch / Stream is required."}), 400
    if not mobile:
        return jsonify({"success": False, "message": "Mobile number is required."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if event exists (supports ID or Category string like 'Dance', 'Singing', 'Photography')
    event = None
    if isinstance(event_id, int) or (isinstance(event_id, str) and str(event_id).isdigit()):
        event = cursor.execute('SELECT * FROM events WHERE id = ?', (int(event_id),)).fetchone()
    elif isinstance(event_id, str) and event_id.strip():
        search_term = event_id.strip()
        event = cursor.execute(
            'SELECT * FROM events WHERE LOWER(category) = LOWER(?) OR LOWER(title) LIKE LOWER(?) LIMIT 1',
            (search_term, f"%{search_term}%")
        ).fetchone()

    if not event:
        conn.close()
        return jsonify({"success": False, "message": f"Selected event '{event_id}' not found."}), 404

    event_id = event['id']
    reg_count = cursor.execute('SELECT COUNT(*) FROM registrations WHERE event_id = ?', (event_id,)).fetchone()[0]
    if reg_count >= event['max_slots']:
        conn.close()
        return jsonify({"success": False, "message": "Sorry, registration for this event is now full!"}), 400

    # Prevent duplicate registration for the same event and student roll number
    existing = cursor.execute(
        'SELECT * FROM registrations WHERE event_id = ? AND LOWER(roll_no) = LOWER(?)',
        (event_id, roll_no)
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({
            "success": False, 
            "message": f"Student '{student_name}' with Roll No '{roll_no}' is already registered for '{event['title']}'. Ticket ID: {existing['ticket_id']}"
        }), 409

    # Generate unique ticket ID: CP-CAT-CODE
    cat_code = event['category'][:3].upper()
    random_code = uuid.uuid4().hex[:6].upper()
    ticket_id = f"CP-{cat_code}-{random_code}"

    cursor.execute('''
        INSERT INTO registrations (
            ticket_id, event_id, event_title, student_name, roll_no,
            email, phone, college_name, department, year_of_study,
            team_name, team_members, needs_hostel_aid, special_requirements
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        ticket_id, event['id'], event['title'], student_name,
        roll_no, email, mobile, college_name, branch, year_of_study,
        team_name, team_members, needs_hostel, special_requirements
    ))

    conn.commit()

    # Fetch created record
    new_reg = cursor.execute('SELECT * FROM registrations WHERE ticket_id = ?', (ticket_id,)).fetchone()
    conn.close()

    # Response explicitly echoing student details (name, roll_no, branch, mobile, event)
    return jsonify({
        "success": True,
        "message": f"Registration successful for {student_name}! Digital pass generated.",
        "ticket": {
            "ticket_id": new_reg["ticket_id"],
            "event_id": event["id"],
            "event_title": new_reg["event_title"],
            "student_name": new_reg["student_name"],
            "name": new_reg["student_name"],
            "roll_no": new_reg["roll_no"],
            "branch": new_reg["department"],
            "department": new_reg["department"],
            "mobile": new_reg["phone"],
            "phone": new_reg["phone"],
            "college_name": new_reg["college_name"],
            "year_of_study": new_reg["year_of_study"],
            "team_name": new_reg["team_name"],
            "team_members": new_reg["team_members"],
            "venue": event["venue"],
            "date_time": event["date_time"],
            "needs_hostel_aid": bool(new_reg["needs_hostel_aid"]),
            "special_requirements": new_reg["special_requirements"],
            "created_at": new_reg["created_at"]
        }
    })

@app.route('/api/registrations', methods=['GET'])
def get_registrations():
    event_id = request.args.get('event_id')
    search = request.args.get('search', '').strip().lower()

    conn = get_db_connection()
    query = 'SELECT * FROM registrations WHERE 1=1'
    params = []

    if event_id and event_id != 'all':
        query += ' AND event_id = ?'
        params.append(event_id)

    if search:
        query += ' AND (LOWER(student_name) LIKE ? OR LOWER(roll_no) LIKE ? OR LOWER(ticket_id) LIKE ? OR LOWER(college_name) LIKE ? OR LOWER(department) LIKE ? OR LOWER(phone) LIKE ?)'
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard, wildcard, wildcard, wildcard])

    query += ' ORDER BY id DESC'
    registrations = conn.execute(query, params).fetchall()
    conn.close()

    results = []
    for r in registrations:
        d = dict(r)
        d['name'] = r['student_name']
        d['branch'] = r['department']
        d['mobile'] = r['phone']
        results.append(d)

    return jsonify({"success": True, "registrations": results})

@app.route('/api/verify/<ticket_id>', methods=['POST'])
def verify_ticket(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    reg = cursor.execute('SELECT * FROM registrations WHERE ticket_id = ?', (ticket_id,)).fetchone()

    if not reg:
        conn.close()
        return jsonify({"success": False, "message": "Invalid Ticket ID. No registration found."}), 404

    new_status = 1 if reg["checked_in"] == 0 else 0
    cursor.execute('UPDATE registrations SET checked_in = ? WHERE ticket_id = ?', (new_status, ticket_id))
    conn.commit()
    conn.close()

    status_str = "Checked In" if new_status == 1 else "Check-in Undone"
    return jsonify({
        "success": True,
        "checked_in": bool(new_status),
        "message": f"Status updated: {status_str}",
        "student_name": reg["student_name"],
        "name": reg["student_name"],
        "roll_no": reg["roll_no"],
        "branch": reg["department"],
        "mobile": reg["phone"],
        "event_title": reg["event_title"]
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    total_reg = conn.execute('SELECT COUNT(*) FROM registrations').fetchone()[0]
    total_events = conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    total_colleges = conn.execute('SELECT COUNT(DISTINCT college_name) FROM registrations').fetchone()[0]
    hostel_requests = conn.execute('SELECT COUNT(*) FROM registrations WHERE needs_hostel_aid = 1').fetchone()[0]
    checked_in_count = conn.execute('SELECT COUNT(*) FROM registrations WHERE checked_in = 1').fetchone()[0]

    category_data = conn.execute('''
        SELECT e.category, COUNT(r.id) as count
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id
        GROUP BY e.category
    ''').fetchall()

    conn.close()

    return jsonify({
        "success": True,
        "total_registrations": total_reg,
        "total_events": total_events,
        "total_colleges": total_colleges,
        "hostel_requests": hostel_requests,
        "checked_in_count": checked_in_count,
        "categories": [{ "category": row["category"], "count": row["count"] } for row in category_data]
    })

@app.route('/api/helpdesk', methods=['GET', 'POST'])
def helpdesk():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        data = request.get_json() or {}
        name = data.get('student_name', '').strip()
        contact = data.get('contact_info', '').strip()
        college = data.get('college_name', '').strip()
        category = data.get('category', 'General')
        query = data.get('query_text', '').strip()

        if not name or not contact or not query:
            conn.close()
            return jsonify({"success": False, "message": "Name, contact info, and query details are required."}), 400

        cursor.execute('''
            INSERT INTO helpdesk_queries (student_name, contact_info, college_name, category, query_text)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, contact, college, category, query))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Your aid/support request has been submitted to the fest student desk!"})

    tickets = cursor.execute('SELECT * FROM helpdesk_queries ORDER BY id DESC').fetchall()
    conn.close()
    return jsonify({"success": True, "queries": [dict(t) for t in tickets]})

@app.route('/api/export', methods=['GET'])
def export_csv():
    conn = get_db_connection()
    registrations = conn.execute('''
        SELECT ticket_id, event_title, student_name, roll_no, email, phone,
               college_name, department, year_of_study, team_name, team_members,
               needs_hostel_aid, special_requirements, checked_in, created_at
        FROM registrations
        ORDER BY id DESC
    ''').fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Ticket ID', 'Event Title', 'Student Name', 'Roll No / USN', 'Branch', 'Mobile Number', 'Email',
        'College Name', 'Year', 'Team Name', 'Team Members',
        'Hostel Aid Needed', 'Special Aid Requirements', 'Checked In', 'Registration Time'
    ])

    for r in registrations:
        writer.writerow([
            r['ticket_id'], r['event_title'], r['student_name'], r['roll_no'], r['department'], r['phone'], r['email'],
            r['college_name'], r['year_of_study'], r['team_name'] or 'N/A', r['team_members'] or 'N/A',
            'Yes' if r['needs_hostel_aid'] == 1 else 'No', r['special_requirements'] or 'None',
            'Yes' if r['checked_in'] == 1 else 'No', r['created_at']
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=cultpulse_fest_registrations.csv"}
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting College Cultural Fest Portal on http://0.0.0.0:{port} ...")
    app.run(host='0.0.0.0', port=port, debug=True)
