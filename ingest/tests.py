import os
from django.test import TestCase
from dotenv import load_dotenv

load_dotenv(override=True)
# Create your tests here.
print(os.getenv('EMAIL_HOST_PASSWORD'))
