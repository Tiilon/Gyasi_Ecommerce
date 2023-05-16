pipeline {
    agent any

    stages {
        stage('Testing with python env') {
            steps {
                echo 'Testing has started'
                sh 'virtualenv venv'
                sh '. venv/bin/activate'
                sh 'pip install -r requirements.txt'
                sh 'python3 manage.py makemigrations'
                sh 'python3 manage.py migrate'
                echo 'finished migrating'
            }
        }
        stage('Deploy to test server') {
            steps {
                sh 'ssh ubuntu@172.31.82.198'
                sh 'chmod +x ./pull_updates_to_test_server.sh'
                sh './pull_updates_to_test_server.sh'
            }
        }
    }
}