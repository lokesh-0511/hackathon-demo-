"""
Comprehensive Backend Test Suite for CultPulse
Tests all REST API endpoints, DB constraints, edge cases, validations, and CSV export.
"""
import unittest
import json
import csv
import io
import time
import app
import database

class BackendTestCase(unittest.TestCase):
    created_ticket_id = None
    created_roll_no = None

    @classmethod
    def setUpClass(cls):
        # Ensure database is initialized
        database.init_db()
        app.app.config['TESTING'] = True
        cls.client = app.app.test_client()

    def test_01_home_page(self):
        """Verify the main landing page renders with status 200"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CultPulse', response.data)
        self.assertIn(b'Inter-Collegiate Cultural Festival', response.data)

    def test_02_get_events(self):
        """Verify event listing returns proper structure and slots left"""
        response = self.client.get('/api/events')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['events'], list)
        self.assertGreaterEqual(len(data['events']), 8)

        first_event = data['events'][0]
        self.assertIn('title', first_event)
        self.assertIn('category', first_event)
        self.assertIn('max_slots', first_event)
        self.assertIn('registered_count', first_event)
        self.assertIn('slots_left', first_event)
        self.assertIn('prize_pool', first_event)
        self.assertIn('coordinator_contact', first_event)

    def test_03_registration_success(self):
        """Verify new student registration returns ticket and updates database"""
        unique_roll = f"ROLL_{int(time.time() * 1000)}"


        payload = {
            "event_id": 2,
            "student_name": "Siddharth Malhotra",
            "roll_no": unique_roll,
            "email": "sid@testuniv.edu",
            "phone": "+91 99887 76655",
            "college_name": "Birla Institute of Tech",
            "department": "Information Science",
            "year_of_study": "3rd Year",
            "team_name": "Neon Cadence",
            "team_members": "Siddharth, Varun, Rhea",
            "needs_hostel_aid": True,
            "special_requirements": "Need amplifier on stage"
        }

        response = self.client.post('/api/register', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('ticket', data)

        ticket = data['ticket']
        self.assertTrue(ticket['ticket_id'].startswith("CP-"))
        self.assertEqual(ticket['student_name'], "Siddharth Malhotra")
        self.assertEqual(ticket['roll_no'], unique_roll)
        self.assertTrue(ticket['needs_hostel_aid'])

        # Store for subsequent tests
        BackendTestCase.created_ticket_id = ticket['ticket_id']
        BackendTestCase.created_roll_no = unique_roll

    def test_03b_student_details_core_features(self):
        """Verify registration specifically with name, roll_no, branch, mobile, and event_id"""
        unique_roll = f"BRANCH_TEST_{int(time.time() * 1000)}"
        payload = {
            "name": "Tanvi Kulkarni",
            "roll_no": unique_roll,
            "branch": "Computer Science (CSE)",
            "mobile": "+91 98220 12345",
            "event_id": 3 # Natraj Solo Classical Dance
        }

        response = self.client.post('/api/register', json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        ticket = data['ticket']
        self.assertEqual(ticket['name'], "Tanvi Kulkarni")
        self.assertEqual(ticket['student_name'], "Tanvi Kulkarni")
        self.assertEqual(ticket['roll_no'], unique_roll)
        self.assertEqual(ticket['branch'], "Computer Science (CSE)")
        self.assertEqual(ticket['mobile'], "+91 98220 12345")
        self.assertEqual(ticket['event_id'], 3)
        self.assertIn("Natraj", ticket['event_title'])

        # Verify retrieval in /api/registrations
        reg_res = self.client.get(f"/api/registrations?search={unique_roll}")
        self.assertEqual(reg_res.status_code, 200)
        reg_data = reg_res.get_json()
        self.assertEqual(len(reg_data['registrations']), 1)
        found = reg_data['registrations'][0]
        self.assertEqual(found['name'], "Tanvi Kulkarni")
        self.assertEqual(found['branch'], "Computer Science (CSE)")
        self.assertEqual(found['mobile'], "+91 98220 12345")

    def test_04_duplicate_registration_prevention(self):
        """Verify student cannot register twice for the same event"""
        payload = {
            "event_id": 2,
            "student_name": "Siddharth Malhotra (Duplicate Attempt)",
            "roll_no": BackendTestCase.created_roll_no,
            "email": "sid@testuniv.edu",
            "phone": "+91 99887 76655",
            "college_name": "Birla Institute of Tech",
            "department": "Information Science",
            "year_of_study": "3rd Year"
        }

        response = self.client.post('/api/register', json=payload)
        self.assertEqual(response.status_code, 409)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn("already registered", data['message'])

    def test_05_registration_validation_missing_fields(self):
        """Verify validation failure when required fields are missing"""
        incomplete_payload = {
            "event_id": 1,
            "student_name": "Missing Roll No",
            # roll_no missing
            "email": "test@domain.com",
            "phone": "9876543210"
        }
        response = self.client.post('/api/register', json=incomplete_payload)
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn("required", data['message'])

    def test_06_registration_invalid_event(self):
        """Verify 404 returned when registering for non-existent event"""
        payload = {
            "event_id": 99999,
            "student_name": "Ghost Student",
            "roll_no": "GHOST001",
            "email": "ghost@college.edu",
            "phone": "9999999999",
            "college_name": "Unknown",
            "department": "Arts",
            "year_of_study": "1st Year"
        }
        response = self.client.post('/api/register', json=payload)
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertFalse(data['success'])

    def test_07_get_registrations_and_filtering(self):
        """Verify coordinator registrations retrieval, search, and event filtering"""
        # Search by ticket ID
        response = self.client.get(f'/api/registrations?search={BackendTestCase.created_ticket_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['registrations']), 1)
        self.assertEqual(data['registrations'][0]['ticket_id'], BackendTestCase.created_ticket_id)

        # Filter by event_id = 2
        response2 = self.client.get('/api/registrations?event_id=2')
        self.assertEqual(response2.status_code, 200)
        data2 = response2.get_json()
        self.assertTrue(all(r['event_id'] == 2 for r in data2['registrations']))

    def test_08_ticket_verification_and_checkin(self):
        """Verify gate pass check-in toggle mechanism"""
        ticket_id = BackendTestCase.created_ticket_id

        # Initial check-in (0 -> 1)
        res1 = self.client.post(f'/api/verify/{ticket_id}')
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertTrue(data1['success'])
        self.assertTrue(data1['checked_in'])
        self.assertIn('Checked In', data1['message'])

        # Undo check-in (1 -> 0)
        res2 = self.client.post(f'/api/verify/{ticket_id}')
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertTrue(data2['success'])
        self.assertFalse(data2['checked_in'])
        self.assertIn('Check-in Undone', data2['message'])

    def test_09_verify_nonexistent_ticket(self):
        """Verify invalid ticket verification returns 404"""
        res = self.client.post('/api/verify/INVALID-TICKET-CODE')
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertFalse(data['success'])

    def test_10_live_stats(self):
        """Verify statistics calculation matches live records"""
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['total_registrations'], 1)
        self.assertGreaterEqual(data['total_events'], 8)
        self.assertGreaterEqual(data['total_colleges'], 1)
        self.assertGreaterEqual(data['hostel_requests'], 1)
        self.assertIsInstance(data['categories'], list)

    def test_11_helpdesk_submission_and_retrieval(self):
        """Verify student aid query submission and retrieval"""
        payload = {
            "student_name": "Ananya Roy",
            "contact_info": "+91 91234 56780",
            "college_name": "National Law University",
            "category": "Hostel Accommodation",
            "query_text": "Need clarification about girls hostel check-in time after 9 PM."
        }
        res_post = self.client.post('/api/helpdesk', json=payload)
        self.assertEqual(res_post.status_code, 200)
        self.assertTrue(res_post.get_json()['success'])

        res_get = self.client.get('/api/helpdesk')
        self.assertEqual(res_get.status_code, 200)
        queries = res_get.get_json()['queries']
        self.assertTrue(any(q['student_name'] == "Ananya Roy" for q in queries))

    def test_12_helpdesk_missing_data(self):
        """Verify helpdesk validation fails with missing fields"""
        bad_payload = {"student_name": "Incomplete"}
        res = self.client.post('/api/helpdesk', json=bad_payload)
        self.assertEqual(res.status_code, 400)

    def test_13_csv_export(self):
        """Verify CSV export contains correct headers and valid records"""
        response = self.client.get('/api/export')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'text/csv')
        self.assertIn('cultpulse_fest_registrations.csv', response.headers.get('Content-Disposition', ''))

        csv_text = response.data.decode('utf-8')
        reader = csv.reader(io.StringIO(csv_text))
        header = next(reader)
        self.assertIn('Ticket ID', header)
        self.assertIn('Student Name', header)
        self.assertIn('Roll No / USN', header)
        self.assertIn('Hostel Aid Needed', header)

        rows = list(reader)
        self.assertGreaterEqual(len(rows), 1)

if __name__ == '__main__':
    unittest.main(verbosity=2)
