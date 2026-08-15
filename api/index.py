import os
import sys

# Add the backend directory to Python sys.path so existing modules load seamlessly
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import the existing FastAPI app without any modifications
from app.main import app
