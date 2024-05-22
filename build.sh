#!/bin/bash

# Step 1: Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Step 2: Upgrade pip
pip install --upgrade pip

# Step 3: Install dependencies
pip install -r requirements.txt

# Step 4: Run the Flask application
FLASK_APP=app.py FLASK_ENV=development flask run --host=0.0.0.0 --port=5001

# Step 4: Run the Flask application with Gunicorn
gunicorn --certfile=cert.pem --keyfile=key.pem -b 0.0.0.0:5001 app:app
