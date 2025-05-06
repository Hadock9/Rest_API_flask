import sys
import os

# Додаємо директорію проекту до Python path
sys.path.insert(0, '/home/vasylfalyovskij/library_api')

# Імпортуємо FastAPI додаток
from main import app

# Створюємо WSGI додаток
application = app

# Set environment variables
os.environ['SECRET_KEY'] = 'your-secret-key-here'
os.environ['REDIS_URL'] = 'redis://localhost:6379/0' 