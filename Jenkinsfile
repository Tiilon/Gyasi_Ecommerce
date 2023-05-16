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
        stage('Test') {
            steps {
                echo 'Testing..'
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying....'
            }
        }
    }
}