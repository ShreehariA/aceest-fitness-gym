"""
ACEest Fitness & Gym – Flask Web Application
=============================================
A RESTful web application for managing gym members, fitness classes,
workouts, BMI calculations, and membership billing.

Version : 3.2.4
"""
from __future__ import annotations

from flask import Flask, jsonify, request, abort, render_template
from datetime import date

app = Flask(__name__)

# ---------------------------------------------------------------------------
# In-memory data stores (replace with a real DB in production)
# ---------------------------------------------------------------------------
members: list[dict] = []
classes: list[dict] = [
    {"id": 1, "name": "Yoga Basics",      "trainer": "Anita",  "schedule": "Mon/Wed 7 AM",  "capacity": 20},
    {"id": 2, "name": "HIIT Blast",        "trainer": "Raj",    "schedule": "Tue/Thu 6 PM",  "capacity": 15},
    {"id": 3, "name": "Strength Training", "trainer": "Mike",   "schedule": "Mon/Fri 8 AM",  "capacity": 12},
    {"id": 4, "name": "Cardio Kickboxing", "trainer": "Sara",   "schedule": "Wed/Sat 5 PM",  "capacity": 18},
]
workouts: list[dict] = []

_next_member_id = 1
_next_workout_id = 1


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def _find_member(member_id: int) -> dict | None:
    return next((m for m in members if m["id"] == member_id), None)


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """Return BMI rounded to 1 decimal place."""
    if height_m <= 0:
        raise ValueError("Height must be greater than zero")
    return round(weight_kg / (height_m ** 2), 1)


def bmi_category(bmi: float) -> str:
    """Return the WHO BMI classification string."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    return "Obese"


def calculate_calories(weight_kg: float, height_cm: float, age: int,
                       gender: str, activity: str) -> int:
    """
    Estimate daily caloric needs using the Mifflin-St Jeor equation
    multiplied by an activity factor.
    """
    if gender.lower() == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    factors = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very active": 1.9,
    }
    multiplier = factors.get(activity.lower(), 1.55)
    return int(bmr * multiplier)


# ========================== ROUTES =========================================

# --- UI Dashboard ----------------------------------------------------------
@app.route("/ui")
def ui():
    """Serve the interactive frontend dashboard."""
    return render_template("index.html")


# --- Home ------------------------------------------------------------------
@app.route("/")
def home():
    """Landing page."""
    return jsonify({
        "message": "Welcome to ACEest Fitness & Gym 💪",
        "version": "3.2.4",
        "endpoints": [
            "/members", "/classes", "/workouts",
            "/bmi", "/calories", "/about"
        ],
    })


# --- About -----------------------------------------------------------------
@app.route("/about")
def about():
    return jsonify({
        "name": "ACEest Fitness & Gym",
        "description": "Your one-stop platform for fitness management, "
                       "workout tracking, and membership billing.",
        "established": 2024,
    })


# ---- Members CRUD --------------------------------------------------------
@app.route("/members", methods=["GET"])
def list_members():
    """Return all registered members."""
    return jsonify(members)


@app.route("/members/<int:member_id>", methods=["GET"])
def get_member(member_id: int):
    """Return a single member by ID."""
    member = _find_member(member_id)
    if member is None:
        abort(404, description="Member not found")
    return jsonify(member)


@app.route("/members", methods=["POST"])
def add_member():
    """Register a new member. Expects JSON body with 'name' at minimum."""
    global _next_member_id
    data = request.get_json(force=True)
    if not data or not data.get("name"):
        abort(400, description="Field 'name' is required")

    member = {
        "id": _next_member_id,
        "name": data["name"],
        "age": data.get("age"),
        "weight": data.get("weight"),
        "height": data.get("height"),
        "program": data.get("program", "General Fitness"),
        "membership_status": data.get("membership_status", "Active"),
        "joined": date.today().isoformat(),
    }
    members.append(member)
    _next_member_id += 1
    return jsonify(member), 201


@app.route("/members/<int:member_id>", methods=["PUT"])
def update_member(member_id: int):
    """Update an existing member's fields."""
    member = _find_member(member_id)
    if member is None:
        abort(404, description="Member not found")

    data = request.get_json(force=True)
    for key in ("name", "age", "weight", "height", "program",
                "membership_status"):
        if key in data:
            member[key] = data[key]
    return jsonify(member)


@app.route("/members/<int:member_id>", methods=["DELETE"])
def delete_member(member_id: int):
    """Remove a member by ID."""
    member = _find_member(member_id)
    if member is None:
        abort(404, description="Member not found")
    members.remove(member)
    return jsonify({"message": f"Member {member_id} deleted"}), 200


# ---- Fitness Classes ------------------------------------------------------
@app.route("/classes", methods=["GET"])
def list_classes():
    """Return the schedule of fitness classes."""
    return jsonify(classes)


@app.route("/classes/<int:class_id>", methods=["GET"])
def get_class(class_id: int):
    cls = next((c for c in classes if c["id"] == class_id), None)
    if cls is None:
        abort(404, description="Class not found")
    return jsonify(cls)


# ---- Workouts -------------------------------------------------------------
@app.route("/workouts", methods=["GET"])
def list_workouts():
    return jsonify(workouts)


@app.route("/workouts", methods=["POST"])
def add_workout():
    """Log a workout. Expects JSON with 'member_id', 'type', 'duration_min'."""
    global _next_workout_id
    data = request.get_json(force=True)
    if not data or not data.get("member_id"):
        abort(400, description="Field 'member_id' is required")

    workout = {
        "id": _next_workout_id,
        "member_id": data["member_id"],
        "type": data.get("type", "General"),
        "duration_min": data.get("duration_min", 0),
        "notes": data.get("notes", ""),
        "date": data.get("date", date.today().isoformat()),
    }
    workouts.append(workout)
    _next_workout_id += 1
    return jsonify(workout), 201


# ---- BMI Calculator -------------------------------------------------------
@app.route("/bmi", methods=["POST"])
def bmi_endpoint():
    """
    Calculate BMI.
    Expects JSON: { "weight_kg": float, "height_m": float }
    """
    data = request.get_json(force=True)
    try:
        weight = float(data["weight_kg"])
        height = float(data["height_m"])
    except (KeyError, TypeError, ValueError):
        abort(400, description="Provide numeric 'weight_kg' and 'height_m'")

    try:
        bmi = calculate_bmi(weight, height)
    except ValueError as exc:
        abort(400, description=str(exc))

    return jsonify({
        "bmi": bmi,
        "category": bmi_category(bmi),
    })


# ---- Calorie Estimator ----------------------------------------------------
@app.route("/calories", methods=["POST"])
def calories_endpoint():
    """
    Estimate daily caloric needs.
    Expects JSON: { "weight_kg", "height_cm", "age", "gender", "activity" }
    """
    data = request.get_json(force=True)
    required = ("weight_kg", "height_cm", "age", "gender", "activity")
    missing = [f for f in required if f not in data]
    if missing:
        abort(400, description=f"Missing fields: {', '.join(missing)}")

    cals = calculate_calories(
        float(data["weight_kg"]),
        float(data["height_cm"]),
        int(data["age"]),
        data["gender"],
        data["activity"],
    )
    return jsonify({"daily_calories": cals})


# ---- Error Handlers -------------------------------------------------------
@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": str(error.description)}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": str(error.description)}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
