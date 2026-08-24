pipeline {
    agent any

    stages {

        stage('Pylint Check') {
            steps {
                echo "Running Pylint check..."

                sh '''
                    python3 --version
                    pylint --version
                    pylint --fail-under=7.0 .
                '''
            }
        }

        stage('Prepare Build') {
            steps {
                echo "Preparing build..."

                sh '''
                    rm -rf build
                    mkdir -p build

                    cp -r . build/

                    echo "Build prepared successfully."
                '''
            }
        }
    }

    post {
        success {
            echo "Pylint passed and build was prepared successfully."
        }

        failure {
            echo "Pipeline failed. Build was not prepared."
        }
    }
}
