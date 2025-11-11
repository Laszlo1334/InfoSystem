#!/bin/sh

# Initialize database
python database.py

# Start Flask application
exec python main.py

