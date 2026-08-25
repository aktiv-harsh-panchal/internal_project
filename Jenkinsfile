pipeline {
    agent any

    environment {
        // GitHub
        GITHUB_CREDENTIALS = '550d0bdc-4a0c-432f-a86c-305bc922b13b'
        GITHUB_URL = 'https://github.com/aktiv-harsh-panchal/internal_project.git'

        // Odoo Server
        ODOO_SERVER = '192.168.1.127'
        ODOO_USER = 'odoo'

        // Custom addons on Odoo server
        ODOO_CUSTOM_ADDONS = '/home/odoo/workspace/internal_project'

        // Odoo 19 standard/core addons
        ODOO_ADDONS = '/home/odoo/workspace/odoo/odoo_19/addons'
        ODOO_CORE_ADDONS = '/home/odoo/workspace/odoo/odoo_19/odoo/addons'

        // Odoo executable
        ODOO_BIN = '/home/odoo/workspace/odoo/odoo_19/odoo-bin'

        // CHANGE THIS to your actual database name
        ODOO_DB = 'test'
    }

    stages {

        stage('Checkout') {
            steps {
                echo "Checking out development branch..."

                deleteDir()

                git(
                    branch: 'development',
                    credentialsId: "${GITHUB_CREDENTIALS}",
                    url: "${GITHUB_URL}"
                )
            }
        }

        stage('Detect Changed Modules') {
            steps {
                script {

                    echo "Detecting changed Odoo modules..."

                    def changedFiles = sh(
                        script: '''
                            git diff --name-only HEAD~1 HEAD
                        ''',
                        returnStdout: true
                    ).trim()

                    echo "Changed files:"
                    echo changedFiles

                    def modules = sh(
                        script: '''
                            git diff --name-only HEAD~1 HEAD |
                            awk -F'/' 'NF >= 2 {print $1}' |
                            sort -u
                        ''',
                        returnStdout: true
                    ).trim()

                    if (!modules) {
                        error("No changed Odoo modules detected.")
                    }

                    env.CHANGED_MODULES = modules

                    echo "Changed modules: ${env.CHANGED_MODULES}"
                }
            }
        }

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

        stage('Deploy Custom Addons') {
            steps {
                echo "Deploying custom addons to Odoo server..."

                sshagent(credentials: ['odoo-server-ssh']) {

                    sh '''
                        rsync -avz --delete \
                        --exclude='.git' \
                        --exclude='build' \
                        ./ \
                        ${ODOO_USER}@${ODOO_SERVER}:${ODOO_CUSTOM_ADDONS}/
                    '''
                }
            }
        }

        stage('Upgrade Odoo Modules') {
            steps {
                echo "Upgrading changed Odoo modules..."

                sshagent(credentials: ['odoo-server-ssh']) {

                    sh '''
                        ssh -o StrictHostKeyChecking=no \
                        ${ODOO_USER}@${ODOO_SERVER} \
                        "${ODOO_BIN} \
                        -d ${ODOO_DB} \
                        --addons-path=${ODOO_CUSTOM_ADDONS},${ODOO_ADDONS},${ODOO_CORE_ADDONS} \
                        -u ${CHANGED_MODULES} \
                        --stop-after-init"
                    '''
                }
            }
        }

        stage('Restart Odoo') {
            steps {
                echo "Restarting Odoo service..."

                sshagent(credentials: ['odoo-server-ssh']) {

                    sh '''
                        ssh -o StrictHostKeyChecking=no \
                        ${ODOO_USER}@${ODOO_SERVER} \
                        "sudo systemctl restart odoo"
                    '''
                }
            }
        }
    }

    post {

        success {
            echo "=========================================="
            echo "CI/CD PIPELINE SUCCESSFUL"
            echo "Changed modules: ${env.CHANGED_MODULES}"
            echo "Odoo deployment completed successfully."
            echo "=========================================="
        }

        failure {
            echo "=========================================="
            echo "CI/CD PIPELINE FAILED"
            echo "Odoo deployment was NOT completed."
            echo "=========================================="
        }
    }
}
