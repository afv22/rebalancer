import unittest
from src.send_email import send_email

class TestSendEmail(unittest.TestCase):
    def test_send(self):
        subject = 'Test'
        body = 'This is a test!'
        send_email(subject, body)

if __name__ == '__main__':
    unittest.main()