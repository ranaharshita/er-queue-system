from flask import request, jsonify
from app import app, er_heap
from db import get_connection

# ─────────────────────────────────────
# API 1: Add a new patient
# ─────────────────────────────────────
@app.route("/add", methods=["POST"])
def add_patient():
    data     = request.get_json()
    name     = data["name"]
    age      = data["age"]
    severity = data["severity"]

    # Step 1: Save to MySQL
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "INSERT INTO patients (name, age, severity) VALUES (%s, %s, %s)",
        (name, age, severity)
    )
    conn.commit()

    # Step 2: Get the auto-assigned ID and arrival time
    patient_id = cursor.lastrowid
    cursor.execute(
        "SELECT * FROM patients WHERE id = %s", (patient_id,)
    )
    patient = cursor.fetchone()

    cursor.close()
    conn.close()

    # Step 3: Convert datetime to string
    patient["arrival_time"] = str(patient["arrival_time"])

    # Step 4: Insert into Max Heap
    er_heap.insert(patient)

    print(f"Heap after insert: {[p['name'] for p in er_heap.heap]}")

    return jsonify({
        "message": "Patient added successfully",
        "patient": patient
    })


# ─────────────────────────────────────
# API 2: View queue (heap sorted)
# ─────────────────────────────────────
@app.route("/queue", methods=["GET"])
def get_queue():
    # Get priority sorted list from heap
    sorted_queue = er_heap.get_sorted_queue()
    return jsonify(sorted_queue)


# ─────────────────────────────────────
# API 3: Peek - see next patient
# without removing them
# ─────────────────────────────────────
@app.route("/next", methods=["GET"])
def next_patient():
    patient = er_heap.peek()

    if patient is None:
        return jsonify({"message": "No patients in queue"}), 404

    return jsonify(patient)


# ─────────────────────────────────────
# API 4: Treat top priority patient
# ─────────────────────────────────────
@app.route("/treat", methods=["POST"])
def treat_patient():
    # Step 1: Remove from heap (heapify down happens here)
    patient = er_heap.remove_max()

    if patient is None:
        return jsonify({"message": "No patients to treat"}), 404

    # Step 2: Update status in MySQL
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE patients SET status = 'Treated' WHERE id = %s",
        (patient["id"],)
    )
    conn.commit()

    cursor.close()
    conn.close()

    print(f"Treated: {patient['name']}")
    print(f"Heap after treat: {[p['name'] for p in er_heap.heap]}")

    return jsonify({
        "message": f"{patient['name']} has been treated",
        "patient": patient
    })
# ─────────────────────────────────────
# API 5: Priority Aging
# Automatically called every 30 seconds
# Checks waiting time and upgrades severity
# ─────────────────────────────────────
@app.route("/aging", methods=["POST"])
def priority_aging():
    from datetime import datetime

    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM patients WHERE status = 'Waiting'"
    )
    patients = cursor.fetchall()

    upgraded = []

    for patient in patients:
        arrival   = patient["arrival_time"]
        now       = datetime.now()
        wait_mins = (now - arrival).total_seconds() / 60

        current_severity = patient["severity"]
        new_severity     = None

        # ── TESTING VALUES (1 min, 2 mins) ──
        if current_severity == "Mild" and wait_mins >= 1:
            new_severity = "Moderate"

        elif current_severity == "Moderate" and wait_mins >= 2:
            new_severity = "Critical"

        if new_severity:
            cursor.execute(
                "UPDATE patients SET severity = %s WHERE id = %s",
                (new_severity, patient["id"])
            )
            er_heap.update_severity(patient["id"], new_severity)

            upgraded.append({
                "name"        : patient["name"],
                "old_severity": current_severity,
                "new_severity": new_severity,
                "waited_mins" : round(wait_mins)
            })

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "message" : f"{len(upgraded)} patients upgraded",
        "upgraded": upgraded
    })