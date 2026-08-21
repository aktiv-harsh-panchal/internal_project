pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out development branch..."
                checkout scm
            }
        }

        stage('Pylint Check') {
            steps {
                echo "Running Pylint..."

                sh '''
                    python3 --version
                    pylint --version

                    pylint --fail-under=7.0 .
                '''
            }
        }

        stage('Build') {
            steps {
                echo "Preparing build..."

                sh '''
                    echo "Build started..."

                    mkdir -p build
                    cp -r . build/

                    echo "Build completed successfully."
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed!'
        }

        always {
            echo 'Pipeline finished.'
        }
    }
}
