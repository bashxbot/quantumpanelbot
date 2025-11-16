"""
WSGI Configuration for PythonAnywhere
Copy this content to your WSGI configuration file on PythonAnywhere
"""

import sys
import os

# Add your project directory to the sys.path
# Replace 'yourusername' with your actual PythonAnywhere username
project_home = '/home/yourusername/quantumpanelbot'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask app
from flask_app import app as application
