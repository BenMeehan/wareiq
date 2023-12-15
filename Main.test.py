import unittest
import json
from Main import app 

class FlaskAppTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_send_event_valid_email(self):
        # Valid JSON payload with a valid email address
        valid_payload = {
            'user_email': 'test@example.com',
            'event': 'test_event',
            'user_name': 'Test User',
            'event_date': '2023-01-01'
        }

        response = self.app.post('/events/send', json=valid_payload)
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['message'], 'Event sent to Kafka')

    def test_send_event_invalid_email(self):
        # Invalid JSON payload with an invalid email address
        invalid_payload = {
            'user_email': 'invalid_email',
            'event': 'test_event',
            'user_name': 'Test User',
            'event_date': '2023-01-01'
        }

        response = self.app.post('/events/send', json=invalid_payload)
        data = json.loads(response.get_data(as_text=True))

        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['status'], 'error')
        self.assertIn('Invalid email address', data['message'])

if __name__ == '__main__':
    unittest.main()
