from django.test import TestCase

# Create your tests here.
from dotenv import load_dotenv
import os

load_dotenv()

print(os.getenv("DB_NAME"))