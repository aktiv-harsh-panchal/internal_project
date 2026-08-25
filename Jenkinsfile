pipeline {
    agent any

    environment {
        // GitHub
        GITHUB_CREDENTIALS = '550d0bdc-4a0c-432f-a86c-305bc922b13b'
        GITHUB_URL = 'https://github.com/aktiv-harsh-panchal/internal_project.git'

        // Odoo Server
        ODOO_SERVER = '192.168.1.127'
        ODOO_USER = 'odoo'

        // Custom addons
        ODOO_CUSTOM_ADDONS = '/home/odoo/workspace/internal_project'

        // Odoo 19 addons
        ODOO_ADDONS = '/home/odoo/workspace/odoo/odoo_19/addons'
        ODOO_CORE_ADDONS = '/home/odoo/workspace/odoo/odoo_19/odoo/addons'

        // Odoo executable
        ODOO_BIN = '/home/odoo/workspace/odoo/odoo_19/odoo-bin'

        // Change this to your actual Odoo database name
        ODOO_DB = 'YOUR_DATABASE_NAME'
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
                            grep '^custom_addons/' |
                            cut -d'/' -f2 |
                            sort -u |
                            tr '\\n' ' '
                        ''',
                        returnStdout: true
                    ).trim()

                    if (!modules) {
                        echo "No Odoo module changes detected."
                        echo "Nothing to deploy."

                        env.CHANGED_MODULES = ''
                    } else {
                        env.CHANGED_MODULES = modules

                        echo "Changed Odoo modules:"
                        echo env.CHANGED_MODULES
                    }
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
            when {
                expression {
                    return env.CHANGED_MODULES?.trim()
                }
            }

            steps {
                echo "Deploying changed Odoo modules..."

                sshagent(credentials: ['odoo-server-ssh']) {

                    sh '''
                        rsync -avz \
                        --exclude='.git' \
                        --exclude='build' \
                        custom_addons/ \
                        ${ODOO_USER}@${ODOO_SERVER}:${ODOO_CUSTOM_ADDONS}/
                    '''
                }
            }
        }

        stage('Upgrade Odoo Modules') {
            when {
                expression {
                    return env.CHANGED_MODULES?.trim()
                }
            }

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
            when {
                expression {
                    return env.CHANGED_MODULES?.trim()
                }
            }

            steps {
                echo "Restarting Odoo..."

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
            echo "=========================================="

            script {
                if (env.CHANGED_MODULES?.trim()) {
                    echo "Changed modules: ${env.CHANGED_MODULES}"
                    echo "Odoo deployment completed successfully."
                } else {
                    echo "No Odoo modules were changed."
                    echo "Deployment was skipped."
                }
            }
        }

        failure {
            echo "=========================================="
            echo "CI/CD PIPELINE FAILED"
            echo "=========================================="
            echo "Odoo deployment was NOT completed."
        }
    }
}
