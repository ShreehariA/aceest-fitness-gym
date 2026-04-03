// ==========================================================================
// ACEest Fitness & Gym – Jenkinsfile (Declarative Pipeline)
// ==========================================================================
// This pipeline pulls the latest code from GitHub, installs dependencies,
// runs the linter, executes the test suite, and builds the Docker image.
// ==========================================================================

pipeline {
    agent any

    environment {
        IMAGE_NAME = 'aceest-fitness-gym'
        IMAGE_TAG  = 'latest'
    }

    stages {
        stage('Checkout') {
            steps {
                echo '📥 Pulling latest code from GitHub...'
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo '🐍 Setting up Python environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                echo '🔍 Running flake8 linter...'
                sh '''
                    . venv/bin/activate
                    flake8 app.py test_app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }

        stage('Test') {
            steps {
                echo '🧪 Running pytest suite...'
                sh '''
                    . venv/bin/activate
                    pytest test_app.py -v --tb=short
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo '🐳 Building Docker image...'
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check the logs above for details.'
        }
        always {
            echo '🧹 Cleaning up workspace...'
            cleanWs()
        }
    }
}
