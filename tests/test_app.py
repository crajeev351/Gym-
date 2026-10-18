import os
import unittest
from app import create_app
from app.models import db, User, Lead, Program, TrainingType, HeroContent, SiteSetting
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF during automated unit tests


class GymTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create test admin
        self.admin = User(username='testadmin', email='testadmin@fitness.com')
        self.admin.set_password('Secret123!')
        db.session.add(self.admin)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_admin(self):
        return self.client.post('/admin/login', data={
            'username': 'testadmin',
            'password': 'Secret123!'
        }, follow_redirects=True)

    # 1. Public Website Tests
    def test_homepage_loads(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        self.assertIn("6+ Years of Transforming Lives", html)
        self.assertIn("2 Days Free Trial", html)
        self.assertIn("Fat Loss", html)
        self.assertIn("Muscle Gain", html)
        self.assertIn("One-to-One Training", html)
        self.assertIn("Claim 2 Days Free Trial", html)

    def test_booking_valid_submission(self):
        res = self.client.post('/book', data={
            'name': 'Aarav Patel',
            'phone': '9876543210',
            'email': 'aarav@example.com',
            'gender': 'Male',
            'fitness_goal': 'Fat Loss',
            'training_type': 'One-to-One Training',
            'honeypot': ''
        }, headers={'X-Requested-With': 'XMLHttpRequest'})

        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data['success'])
        self.assertIn("Thank you! We will contact you within 24 hours.", json_data['message'])

        # Verify DB entry
        lead = Lead.query.filter_by(phone='9876543210').first()
        self.assertIsNotNone(lead)
        self.assertEqual(lead.name, 'Aarav Patel')
        self.assertEqual(lead.status, 'New')

    def test_booking_invalid_phone(self):
        res = self.client.post('/book', data={
            'name': 'Pooja Verma',
            'phone': '12345',  # invalid indian phone
            'email': 'pooja@example.com',
            'gender': 'Female',
            'fitness_goal': 'Fat Loss',
            'training_type': 'One-to-One Training'
        }, headers={'X-Requested-With': 'XMLHttpRequest'})

        self.assertEqual(res.status_code, 400)
        json_data = res.get_json()
        self.assertFalse(json_data['success'])
        self.assertIn('phone', json_data['errors'])

    def test_honeypot_blocks_spam(self):
        initial_count = Lead.query.count()
        res = self.client.post('/book', data={
            'name': 'Spam Bot',
            'phone': '9876543210',
            'email': 'bot@spam.com',
            'gender': 'Male',
            'fitness_goal': 'Fat Loss',
            'training_type': 'One-to-One Training',
            'honeypot': 'http://spamsite.com'  # filled honeypot
        }, headers={'X-Requested-With': 'XMLHttpRequest'})

        self.assertEqual(res.status_code, 200)
        # Should NOT increase DB lead count!
        self.assertEqual(Lead.query.count(), initial_count)

    # 2. Admin Authentication Tests
    def test_admin_protected_routes(self):
        # Unauthenticated access should redirect to login
        res = self.client.get('/admin/', follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/admin/login', res.headers['Location'])

    def test_admin_login_and_dashboard(self):
        res = self.login_admin()
        self.assertEqual(res.status_code, 200)
        html = res.data.decode('utf-8')
        self.assertIn("Business Performance Overview", html)
        self.assertIn("Total Leads", html)

    def test_admin_lead_status_update_and_csv_export(self):
        # Create a lead
        lead = Lead(
            name='Rohit Sen',
            phone='9812345678',
            email='rohit@test.com',
            gender='Male',
            fitness_goal='Muscle Gain',
            training_type='One-to-One Training',
            status='New'
        )
        db.session.add(lead)
        db.session.commit()

        self.login_admin()

        # Update status
        res = self.client.post(f'/admin/leads/{lead.id}/status', data={
            'status': 'Contacted'
        }, headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(res.status_code, 200)

        updated_lead = db.session.get(Lead, lead.id)
        self.assertEqual(updated_lead.status, 'Contacted')

        # CSV Export
        csv_res = self.client.get('/admin/leads/export-csv')
        self.assertEqual(csv_res.status_code, 200)
        self.assertIn('text/csv', csv_res.headers['Content-Type'])
        self.assertIn('Rohit Sen', csv_res.data.decode('utf-8'))

    def test_admin_change_password(self):
        self.login_admin()
        res = self.client.post('/admin/change-password', data={
            'current_password': 'Secret123!',
            'new_password': 'BrandNewPassword999!',
            'confirm_password': 'BrandNewPassword999!'
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        user = User.query.filter_by(username='testadmin').first()
        self.assertTrue(user.check_password('BrandNewPassword999!'))


if __name__ == '__main__':
    unittest.main()
