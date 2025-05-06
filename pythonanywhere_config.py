import os

# PythonAnywhere configuration
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Redis configuration
REDIS_URL = 'redis://localhost:6379/0'

# API configuration
API_PREFIX = '/api'
API_VERSION = 'v1' 