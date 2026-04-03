"""
ACEest Fitness & Gym – Comprehensive Test Suite
================================================
Uses pytest to validate every endpoint, helper function, and error path
in the Flask application.

Run:  pytest test_app.py -v
"""

import pytest
import app as app_module
from app import app, calculate_bmi, bmi_category, calculate_calories, members, workouts


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def client():
    """Create a Flask test client with a fresh application context."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def reset_data():
    """Clear in-memory stores and reset ID counters before each test."""
    members.clear()
    workouts.clear()
    app_module._next_member_id = 1
    app_module._next_workout_id = 1
    yield
    members.clear()
    workouts.clear()


# ===========================================================================
# 1. UNIT TESTS – Pure helper functions
# ===========================================================================
class TestCalculateBMI:
    def test_normal_bmi(self):
        assert calculate_bmi(70, 1.75) == 22.9

    def test_high_bmi(self):
        assert calculate_bmi(110, 1.70) == 38.1

    def test_low_bmi(self):
        assert calculate_bmi(45, 1.75) == 14.7

    def test_zero_height_raises(self):
        with pytest.raises(ValueError, match="Height must be greater than zero"):
            calculate_bmi(70, 0)

    def test_negative_height_raises(self):
        with pytest.raises(ValueError):
            calculate_bmi(70, -1.5)


class TestBMICategory:
    def test_underweight(self):
        assert bmi_category(17.0) == "Underweight"

    def test_normal(self):
        assert bmi_category(22.0) == "Normal weight"

    def test_overweight(self):
        assert bmi_category(27.5) == "Overweight"

    def test_obese(self):
        assert bmi_category(35.0) == "Obese"

    def test_boundary_18_5(self):
        assert bmi_category(18.5) == "Normal weight"

    def test_boundary_25(self):
        assert bmi_category(25.0) == "Overweight"

    def test_boundary_30(self):
        assert bmi_category(30.0) == "Obese"


class TestCalculateCalories:
    def test_male_moderate(self):
        cals = calculate_calories(80, 180, 30, "male", "moderate")
        assert isinstance(cals, int)
        assert cals > 0

    def test_female_sedentary(self):
        cals = calculate_calories(60, 165, 25, "female", "sedentary")
        assert isinstance(cals, int)
        assert cals > 0

    def test_male_very_active(self):
        cals_active = calculate_calories(80, 180, 30, "male", "very active")
        cals_sed = calculate_calories(80, 180, 30, "male", "sedentary")
        assert cals_active > cals_sed  # more activity → more calories


# ===========================================================================
# 2. INTEGRATION TESTS – Flask routes
# ===========================================================================

# --- Home & About ----------------------------------------------------------
class TestHomeRoute:
    def test_home_status(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_home_json_keys(self, client):
        data = client.get("/").get_json()
        assert "message" in data
        assert "version" in data
        assert "endpoints" in data

    def test_home_welcome_message(self, client):
        data = client.get("/").get_json()
        assert "ACEest" in data["message"]


class TestAboutRoute:
    def test_about_status(self, client):
        resp = client.get("/about")
        assert resp.status_code == 200

    def test_about_fields(self, client):
        data = client.get("/about").get_json()
        assert data["name"] == "ACEest Fitness & Gym"
        assert "description" in data


# --- Members CRUD ----------------------------------------------------------
class TestMembers:
    def _add_member(self, client, name="Alice", **kwargs):
        payload = {"name": name, **kwargs}
        return client.post("/members", json=payload)

    def test_list_empty(self, client):
        resp = client.get("/members")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_add_member(self, client):
        resp = self._add_member(client, "Alice", age=28, weight=65)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Alice"
        assert data["id"] == 1
        assert data["membership_status"] == "Active"

    def test_add_member_missing_name(self, client):
        resp = client.post("/members", json={"age": 30})
        assert resp.status_code == 400

    def test_get_member(self, client):
        self._add_member(client, "Bob")
        resp = client.get("/members/1")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Bob"

    def test_get_member_not_found(self, client):
        resp = client.get("/members/999")
        assert resp.status_code == 404

    def test_update_member(self, client):
        self._add_member(client, "Carol")
        resp = client.put("/members/1", json={"program": "Muscle Gain"})
        assert resp.status_code == 200
        assert resp.get_json()["program"] == "Muscle Gain"

    def test_update_member_not_found(self, client):
        resp = client.put("/members/999", json={"name": "X"})
        assert resp.status_code == 404

    def test_delete_member(self, client):
        self._add_member(client, "Dan")
        resp = client.delete("/members/1")
        assert resp.status_code == 200
        # Confirm list is empty
        assert client.get("/members").get_json() == []

    def test_delete_member_not_found(self, client):
        resp = client.delete("/members/999")
        assert resp.status_code == 404

    def test_multiple_members(self, client):
        self._add_member(client, "Eve")
        self._add_member(client, "Frank")
        data = client.get("/members").get_json()
        assert len(data) == 2


# --- Classes ---------------------------------------------------------------
class TestClasses:
    def test_list_classes(self, client):
        resp = client.get("/classes")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) >= 4  # seeded data

    def test_get_class(self, client):
        resp = client.get("/classes/1")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Yoga Basics"

    def test_get_class_not_found(self, client):
        resp = client.get("/classes/999")
        assert resp.status_code == 404


# --- Workouts --------------------------------------------------------------
class TestWorkouts:
    def test_list_empty(self, client):
        resp = client.get("/workouts")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_add_workout(self, client):
        resp = client.post("/workouts", json={
            "member_id": 1,
            "type": "Strength",
            "duration_min": 45,
            "notes": "Leg day"
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["type"] == "Strength"
        assert data["duration_min"] == 45

    def test_add_workout_missing_member(self, client):
        resp = client.post("/workouts", json={"type": "Cardio"})
        assert resp.status_code == 400


# --- BMI Endpoint ----------------------------------------------------------
class TestBMIEndpoint:
    def test_valid_bmi(self, client):
        resp = client.post("/bmi", json={"weight_kg": 70, "height_m": 1.75})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["bmi"] == 22.9
        assert data["category"] == "Normal weight"

    def test_missing_fields(self, client):
        resp = client.post("/bmi", json={"weight_kg": 70})
        assert resp.status_code == 400

    def test_zero_height(self, client):
        resp = client.post("/bmi", json={"weight_kg": 70, "height_m": 0})
        assert resp.status_code == 400


# --- Calories Endpoint -----------------------------------------------------
class TestCaloriesEndpoint:
    def test_valid_request(self, client):
        resp = client.post("/calories", json={
            "weight_kg": 75, "height_cm": 175,
            "age": 30, "gender": "male", "activity": "moderate"
        })
        assert resp.status_code == 200
        assert "daily_calories" in resp.get_json()

    def test_missing_fields(self, client):
        resp = client.post("/calories", json={"weight_kg": 75})
        assert resp.status_code == 400


# --- Error Handlers --------------------------------------------------------
class TestErrorHandlers:
    def test_405_method_not_allowed(self, client):
        resp = client.delete("/classes")  # DELETE not allowed on /classes
        assert resp.status_code == 405
