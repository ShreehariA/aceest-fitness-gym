# ACEest Fitness & Gym 💪

> A Flask-based web application for fitness and gym management, fully containerised with Docker, tested with Pytest, and delivered via automated CI/CD pipelines (GitHub Actions + Jenkins).

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Tech Stack](#tech-stack)  
3. [Project Structure](#project-structure)  
4. [Local Setup & Execution](#local-setup--execution)  
5. [Running Tests](#running-tests)  
6. [Docker Usage](#docker-usage)  
7. [CI/CD – GitHub Actions](#cicd--github-actions)  
8. [CI/CD – Jenkins Integration](#cicd--jenkins-integration)  
9. [API Endpoints](#api-endpoints)  
10. [Version History](#version-history)  

---

## Project Overview

ACEest Fitness & Gym is a rapidly scaling startup. This repository contains the **Flask web application** and the complete **DevOps pipeline** infrastructure that ensures:

- ✅ Code quality via linting (flake8)  
- ✅ Functional correctness via automated tests (pytest)  
- ✅ Environment consistency via containerisation (Docker)  
- ✅ Continuous Integration & Delivery via GitHub Actions and Jenkins  

---

## Tech Stack

| Layer              | Technology           |
| ------------------ | -------------------- |
| **Language**       | Python 3.9           |
| **Framework**      | Flask 3.0            |
| **Testing**        | Pytest 8.2           |
| **Linting**        | Flake8 7.1           |
| **Containerisation** | Docker (python:3.9-slim) |
| **WSGI Server**    | Gunicorn 22.0        |
| **CI/CD**          | GitHub Actions, Jenkins |

---

## Project Structure

```
aceest-project/
├── app.py                     # Flask application (all routes & business logic)
├── test_app.py                # Pytest test suite (unit + integration)
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container image definition
├── Jenkinsfile                # Jenkins declarative pipeline
├── .github/
│   └── workflows/
│       └── main.yml           # GitHub Actions CI/CD workflow
├── .gitignore
├── README.md                  # This file
└── Aceestver-*.py             # Historical version snapshots
```

---

## Local Setup & Execution

### Prerequisites

- Python 3.9+ installed  
- pip package manager  
- (Optional) Docker Desktop for containerised runs  

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/aceest-fitness-gym.git
cd aceest-fitness-gym

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

The app will be available at **http://localhost:5000**.

---

## Running Tests

```bash
# Activate the virtual environment first, then:
pytest test_app.py -v
```

Expected output: **all tests pass** covering home, about, members CRUD, classes, workouts, BMI calculator, calorie estimator, and error handlers.

To see a coverage summary (optional):

```bash
pip install pytest-cov
pytest test_app.py -v --cov=app --cov-report=term-missing
```

---

## Docker Usage

### Build the image

```bash
docker build -t aceest-fitness-gym:latest .
```

### Run the container

```bash
docker run -d -p 5000:5000 --name aceest aceest-fitness-gym:latest
```

### Verify

```bash
curl http://localhost:5000/
# → {"endpoints":[...],"message":"Welcome to ACEest Fitness & Gym 💪","version":"3.2.4"}
```

### Run tests inside the container

```bash
docker run --rm aceest-fitness-gym:latest pytest test_app.py -v
```

### Stop & remove

```bash
docker stop aceest && docker rm aceest
```

---

## CI/CD – GitHub Actions

The workflow file is located at `.github/workflows/main.yml`.

### Trigger

Every **push** or **pull_request** to the `main` branch.

### Pipeline Stages

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  🔍 Lint     │────▶│  🧪 Test     │────▶│  🐳 Docker   │
│  (flake8)    │     │  (pytest)    │     │  (build &    │
│              │     │              │     │   verify)    │
└──────────────┘     └──────────────┘     └──────────────┘
```

1. **Lint** – Runs `flake8` to catch syntax errors and code-quality issues.  
2. **Test** – Executes the full `pytest` suite; the pipeline fails if any test fails.  
3. **Docker** – Builds the Docker image and performs a smoke test (starts the container and verifies a `200 OK` response from `/`).

---

## CI/CD – Jenkins Integration

### Overview

A `Jenkinsfile` (declarative pipeline) is included for Jenkins-based builds.

### Pipeline Stages

| Stage | Description |
|-------|-------------|
| **Checkout** | Pulls the latest code from the connected GitHub repo |
| **Setup Python Environment** | Creates a virtual environment and installs dependencies |
| **Lint** | Runs `flake8` static analysis |
| **Test** | Runs `pytest` suite |
| **Docker Build** | Builds the Docker image |

### Jenkins Setup Steps

1. Install Jenkins on your server/VM (or use Docker):
   ```bash
   docker run -d -p 8080:8080 -p 50000:50000 jenkins/jenkins:lts
   ```
2. Install required plugins: **Pipeline**, **Git**, **Docker Pipeline**.  
3. Create a new **Pipeline** project.  
4. Under *Pipeline → Definition*, select **Pipeline script from SCM**.  
5. Set SCM to **Git** and enter the GitHub repository URL.  
6. The `Jenkinsfile` in the repo root will be detected automatically.  
7. Click **Build Now** to trigger the pipeline.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome page & available endpoints |
| `GET` | `/about` | Application information |
| `GET` | `/members` | List all members |
| `POST` | `/members` | Register a new member |
| `GET` | `/members/<id>` | Get member by ID |
| `PUT` | `/members/<id>` | Update a member |
| `DELETE` | `/members/<id>` | Remove a member |
| `GET` | `/classes` | List fitness classes |
| `GET` | `/classes/<id>` | Get class by ID |
| `GET` | `/workouts` | List all workouts |
| `POST` | `/workouts` | Log a new workout |
| `POST` | `/bmi` | Calculate BMI |
| `POST` | `/calories` | Estimate daily caloric needs |

### Example – Register a Member

```bash
curl -X POST http://localhost:5000/members \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "age": 28, "weight": 65, "height": 1.68, "program": "Fat Loss"}'
```

### Example – Calculate BMI

```bash
curl -X POST http://localhost:5000/bmi \
  -H "Content-Type: application/json" \
  -d '{"weight_kg": 70, "height_m": 1.75}'
```

---

## Version History

| Version | Highlights |
|---------|-----------|
| 1.0 | Initial fitness tracker script |
| 1.1 | Added BMI and calorie calculations |
| 1.1.2 | Bug fixes, improved input validation |
| 2.0.1 | Introduced SQLite database layer |
| 2.1.2 | Added workout logging module |
| 2.2.1 | Membership billing & status tracking |
| 2.2.4 | PDF report generation |
| 3.0.1 | Migrated to Flask web application |
| 3.1.2 | Full REST API with CRUD for members |
| 3.2.4 | Docker + CI/CD pipeline (current) |

---

## Author

**ACEest DevOps Team** – Introduction to DevOps (CSIZG514 / SEZG514 / SEUSZG514) – S2-25

---

## License

This project is for academic purposes as part of the DevOps coursework.
