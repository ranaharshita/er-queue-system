from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Import heap
from heap import er_heap

# Import database connection
from db import get_connection

# ─────────────────────────────────────
# Load existing waiting patients into
# heap when server starts
# ─────────────────────────────────────
def load_heap_from_db():
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM patients WHERE status = 'Waiting' ORDER BY arrival_time ASC"
    )
    patients = cursor.fetchall()

    cursor.close()
    conn.close()

    for patient in patients:
        # Convert datetime to string for comparison
        patient["arrival_time"] = str(patient["arrival_time"])
        er_heap.insert(patient)

    print(f"Loaded {len(patients)} patients into heap")

# Load heap on startup
import os
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    load_heap_from_db()

# Import routes after app is created
from routes import *

if __name__ == "__main__":
    app.run(debug=True, port=5000)