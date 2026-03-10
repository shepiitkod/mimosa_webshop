import os

STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')

if not STRIPE_PUBLIC_KEY or not STRIPE_SECRET_KEY:
    raise ValueError("Stripe keys are not set in the environment variables.")