import os
import unittest

class TestStripeIntegration(unittest.TestCase):
    def test_stripe_keys(self):
        public_key = os.getenv('STRIPE_PUBLIC_KEY')
        secret_key = os.getenv('STRIPE_SECRET_KEY')
        self.assertIsNotNone(public_key)
        self.assertIsNotNone(secret_key)

if __name__ == '__main__':
    unittest.main()