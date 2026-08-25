pipeline {
    agent any

    options {
        // Prevent Jenkins from automatically checking out the repository.
        // We perform checkout manually in the Checkout stage.
        skipDefaultCheckout(true)

        // Keep only the last 10 builds.
        buildDiscarder(logRotator(numToKeepStr: '10'))

        // Do not allow two deployments to run at the same time.
        disableConcurrentBuilds()
    }

    environment {

        // ============================================================
        // GITHUB
        // ============================================================

        GITHUB_CREDENTIALS = '550d0bdc-4a0c-432f-a86c-305bc922b13b'
        GITHUB_URL = 'https://github.com/aktiv-harsh-panchal/internal_project.git'
        GITHUB_BRANCH = 'development'


        // ============================================================
        // ODOO SERVER
        // ============================================================

        ODOO_SERVER = '192.168.1.127'
        ODOO_USER = 'odoo'
        ODOO_PORT = '8069'


        // ============================================================
        // ODOO CUSTOM ADDONS
        // ============================================================

        ODOO_CUSTOM_ADDONS = '/home/odoo/workspace/internal_project'


        // ============================================================
        // ODOO 19 ADDONS
        // ============================================================

        ODOO_ADDONS = '/home/odoo/workspace/odoo/odoo_19/addons'

        ODOO_CORE_ADDONS = '/home/odoo/workspace/odoo/odoo_19/odoo/addons'


        // ============================================================
        // ODOO EXECUTABLE
        // ============================================================

        ODOO_BIN = '/home/odoo/workspace/odoo/odoo_19/odoo-bin'


        // ============================================================
        // ODOO DATABASE
        // ============================================================

        // IMPORTANT:
        // Replace this with your real database name.
        ODOO_DB = 'YOUR_DATABASE_NAME'


        // ============================================================
        // JENKINS -> ODOO SSH CREDENTIAL
        // ============================================================

        // Create this credential in:
        // Jenkins -> Manage Jenkins -> Credentials
        //
        // Kind:
        // SSH Username with private key
        //
        // ID:
        // odoo-server-ssh

        ODOO_SSH_CREDENTIALS = 'odoo-server-ssh'
    }


    stages {

        // ============================================================
        // 1. CHECKOUT
        // ============================================================

        stage('Checkout') {

            steps {

                echo '=========================================='
                echo 'CHECKOUT DEVELOPMENT BRANCH'
                echo '=========================================='

                deleteDir()

                git(
                    branch: "${GITHUB_BRANCH}",
                    credentialsId: "${GITHUB_CREDENTIALS}",
                    url: "${GITHUB_URL}"
                )

                // Fetch previous commit so that
                // git diff HEAD~1 HEAD works correctly.
                sh '''
                    git fetch --no-tags --prune --unshallow origin development || true
                    git fetch --no-tags origin development
                '''

                sh '''
                    echo "Current branch:"
                    git branch --show-current

                    echo "Current commit:"
                    git rev-parse HEAD

                    echo "Commit message:"
                    git log -1 --pretty=%B
                '''
            }
        }


        // ============================================================
        // 2. DETECT CHANGED ODOO MODULES
        // ============================================================

        stage('Detect Changed Modules') {
	    steps {
		script {

		    echo '=========================================='
		    echo 'DETECTING CHANGED ODOO MODULES'
		    echo '=========================================='

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
		            awk -F/ 'NF >= 2 {print $1}' |
		            sort -u |
		            tr '\\n' ' '
		        ''',
		        returnStdout: true
		    ).trim()

		    if (modules) {

		        env.CHANGED_MODULES = modules

		        echo "Changed Odoo modules:"
		        echo "${env.CHANGED_MODULES}"

		    } else {

		        env.CHANGED_MODULES = ''

		        echo "No Odoo module changes detected."
		        echo "Deployment will be skipped."
		    }
		}
	    }
	}


        // ============================================================
        // 3. PYLINT
        // ============================================================

	stage('Pylint Check') {
	    steps {
		script {

		    if (env.CHANGED_MODULES?.trim()) {

		        echo "Running Pylint..."

		        sh '''
		            python3 --version
		            pylint --version
		            pylint --fail-under=7.0 ${CHANGED_MODULES}
		        '''

		    } else {

		        echo "No Odoo modules changed."
		        echo "Pylint check skipped."
		    }
		}
	    }
	}


        // ============================================================
        // 4. DEPLOY CUSTOM ADDONS
        // ============================================================

        stage('Deploy Custom Addons') {

            when {

                expression {

                    return env.CHANGED_MODULES?.trim()
                }
            }

            steps {

                echo '=========================================='
                echo 'DEPLOYING CUSTOM ADDONS'
                echo '=========================================='

                sshagent(credentials: ["${ODOO_SSH_CREDENTIALS}"]) {

                    sh '''
                        echo "Testing SSH connection..."

                        ssh \
                        -o StrictHostKeyChecking=no \
                        -p 22 \
                        ${ODOO_USER}@${ODOO_SERVER} \
                        "echo SSH connection successful"

                        echo "Deploying custom addons..."

                        rsync -avz \
                        --exclude='.git' \
                        --exclude='.gitignore' \
                        --exclude='Jenkinsfile' \
                        --exclude='build' \
                        --exclude='__pycache__' \
                        custom_addons/ \
                        ${ODOO_USER}@${ODOO_SERVER}:${ODOO_CUSTOM_ADDONS}/

                        echo "Custom addons deployed successfully."
                    '''
                }
            }
        }


        // ============================================================
        // 5. UPGRADE ODOO MODULES
        // ============================================================

        stage('Upgrade Odoo Modules') {

            when {

                expression {

                    return env.CHANGED_MODULES?.trim()
                }
            }

            steps {

                echo '=========================================='
                echo 'UPGRADING ODOO MODULES'
                echo '=========================================='

                sshagent(credentials: ["${ODOO_SSH_CREDENTIALS}"]) {

                    sh '''
                        echo "Modules to upgrade:"
                        echo "${CHANGED_MODULES}"

                        ssh \
                        -o StrictHostKeyChecking=no \
                        -p 22 \
                        ${ODOO_USER}@${ODOO_SERVER} \
                        "${ODOO_BIN} \
                        -d ${ODOO_DB} \
                        --addons-path=${ODOO_CUSTOM_ADDONS},${ODOO_ADDONS},${ODOO_CORE_ADDONS} \
                        -u ${CHANGED_MODULES} \
                        --stop-after-init"

                        echo "Odoo module upgrade completed."
                    '''
                }
            }
        }


        // ============================================================
        // 6. RESTART ODOO
        // ============================================================

        stage('Restart Odoo') {

            when {

                expression {

                    return env.CHANGED_MODULES?.trim()
                }
            }

            steps {

                echo '=========================================='
                echo 'RESTARTING ODOO'
                echo '=========================================='

                sshagent(credentials: ["${ODOO_SSH_CREDENTIALS}"]) {

                    sh '''
                        ssh \
                        -o StrictHostKeyChecking=no \
                        -p 22 \
                        ${ODOO_USER}@${ODOO_SERVER} \
                        "sudo systemctl restart odoo"

                        echo "Odoo restart command completed."
                    '''
                }
            }
        }


        // ============================================================
        // 7. HEALTH CHECK
        // ============================================================

        stage('Odoo Health Check') {

            steps {

                echo '=========================================='
                echo 'ODOO HEALTH CHECK'
                echo '=========================================='

                script {

                    if (env.CHANGED_MODULES?.trim()) {

                        sh '''
                            echo "Checking Odoo HTTP service..."

                            sleep 5

                            curl \
                            --fail \
                            --silent \
                            --show-error \
                            http://${ODOO_SERVER}:${ODOO_PORT}/web/database/selector \
                            > /dev/null

                            echo "Odoo is responding successfully."
                        '''

                    } else {

                        echo 'No deployment was performed.'
                        echo 'Odoo health check skipped.'
                    }
                }
            }
        }
    }


    // ================================================================
    // POST ACTIONS
    // ================================================================

    post {

        success {

            echo '=========================================='
            echo '          PIPELINE SUCCESS'
            echo '=========================================='

            script {

                if (env.CHANGED_MODULES?.trim()) {

                    echo "Changed modules: ${env.CHANGED_MODULES}"
                    echo 'Pylint: PASSED'
                    echo 'Deployment: SUCCESS'
                    echo 'Module upgrade: SUCCESS'
                    echo 'Odoo restart: SUCCESS'
                    echo 'Health check: SUCCESS'

                } else {

                    echo 'No Odoo modules were changed.'
                    echo 'Pylint: SKIPPED'
                    echo 'Deployment: SKIPPED'
                    echo 'Module upgrade: SKIPPED'
                    echo 'Odoo restart: SKIPPED'
                    echo 'Build completed successfully.'
                }
            }

            echo '=========================================='
        }


        failure {

            echo '=========================================='
            echo '          PIPELINE FAILED'
            echo '=========================================='

            echo 'One of the CI/CD stages failed.'
            echo 'Deployment will not continue after a failed stage.'

            echo '=========================================='
        }
    }
}
