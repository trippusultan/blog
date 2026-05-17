#!/usr/bin/env python3
"""Bootstraps the blog venv and runs the Flask app."""
import sys, os

VENV_SP = os.path.join(os.path.dirname(__file__), 'venv', 'lib',
                       f'python{sys.version_info.major}.{sys.version_info.minor}',
                       'site-packages')
if os.path.isdir(VENV_SP):
    sys.path.insert(0, VENV_SP)

# Now that venv is on path, run app
os.chdir(os.path.dirname(__file__))
from app import app

if __name__ == '__main__':
    print("  Blog running → http://localhost:8001")
    print("  Admin  → http://localhost:8001/admin/login  (admin / admin123)")
    app.run(debug=True, host='0.0.0.0', port=8001)
