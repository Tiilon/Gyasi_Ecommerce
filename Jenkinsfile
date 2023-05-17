pipeline {
    agent { label params['Silver'] }

    stages {
        stage('Deploy to test server') {
            steps {
                sh 'chmod +x ./pull_updates_to_test_server.sh'
                sh './pull_updates_to_test_server.sh'
            }
        }
    }
}