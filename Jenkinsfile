pipeline {
    agent any

    options {
        // Jenkins will not automatically checkout the repository.
        // Checkout is handled manually in the Checkout stage.
        skipDefaultCheckout(true)

        // Keep only the last 10 builds.
        buildDiscarder(logRotator(numToKeepStr: '10'))

        // Prevent two deployments from running at the same time.
        disableConcurrentBuilds()
    }

    environment {

        // ============================================================
        // GITHUB - HTTPS
        // ============================================================

        GITHUB_CREDENTIALS = '550d0bdc-4a0c-432f-a86c-305bc922b13b'

        GITHUB_URL = 'https://github.com/aktiv-harsh-panchal/internal_project.git'

        GITHUB_BRANCH = 'development'


        // ============================================================
        // ODOO SERVER
        // ============================================================

        ODOO_SERVER = '192.168.1.127'

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

        ODOO_DB = 'test'
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

                // Clean Jenkins workspace.
                deleteDir()

                /*
                 * GitHub is accessed using HTTPS.
                 *
                 * No SSH Agent is required.
                 */

                git(
                    branch: "${GITHUB_BRANCH}",
                    credentialsId: "${GITHUB_CREDENTIALS}",
                    url: "${GITHUB_URL}"
                )

                echo 'Repository checkout completed.'

                sh '''
                    echo "=========================================="
                    echo "GIT INFORMATION"
                    echo "=========================================="

                    echo "Current branch:"
                    git branch --show-current

                    echo ""

                    echo "Current commit:"
                    git rev-parse HEAD

                    echo ""

                    echo "Commit message:"
                    git log -1 --pretty=%B

                    echo ""

                    echo "Remote:"
                    git remote -v
                '''
            }
        }


        // ============================================================
        // 2. DETECT CHANGED MODULES
        // ============================================================

        stage('Detect Changed Modules') {

            steps {

                script {

                    echo '=========================================='
                    echo 'DETECTING CHANGED ODOO MODULES'
                    echo '=========================================='

                    /*
                     * Check whether HEAD~1 exists.
                     */

                    def hasPreviousCommit = sh(
                        script: '''
                            git rev-parse HEAD~1 >/dev/null 2>&1
                        ''',
                        returnStatus: true
                    ) == 0


                    if (!hasPreviousCommit) {

                        echo 'No previous commit available.'

                        env.CHANGED_MODULES = sh(
                            script: '''
                                find . -mindepth 2 -maxdepth 2 -type f \\
                                \\( -name "__manifest__.py" -o -name "__openerp__.py" \\) |
                                sed 's#^./##' |
                                cut -d/ -f1 |
                                sort -u |
                                tr '\\n' ' '
                            ''',
                            returnStdout: true
                        ).trim()

                    } else {

                        def changedFiles = sh(
                            script: '''
                                git diff --name-only HEAD~1 HEAD
                            ''',
                            returnStdout: true
                        ).trim()


                        echo 'Changed files:'

                        if (changedFiles) {
                            echo changedFiles
                        } else {
                            echo 'No files changed.'
                        }


                        /*
                         * Detect top-level Odoo modules.
                         */

                        def modules = sh(
                            script: '''
                                git diff --name-only HEAD~1 HEAD |
                                awk -F/ 'NF >= 2 {print $1}' |
                                sort -u |
                                tr '\\n' ' '
                            ''',
                            returnStdout: true
                        ).trim()


                        env.CHANGED_MODULES = modules
                    }


                    if (env.CHANGED_MODULES?.trim()) {

                        echo 'Changed Odoo modules:'

                        echo "${env.CHANGED_MODULES}"

                    } else {

                        env.CHANGED_MODULES = ''

                        echo 'No Odoo module changes detected.'

                        echo 'Deployment will be skipped.'
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

                        echo '=========================================='
                        echo 'PYLINT CHECK'
                        echo '=========================================='

                        echo "Changed modules: ${env.CHANGED_MODULES}"

                        echo 'Minimum required Pylint score: 4.0'


                        sh '''
                            python3 --version

                            pylint --version

                            pylint --fail-under=4.0 ${CHANGED_MODULES}
                        '''


                        echo 'Pylint check passed.'

                    } else {

                        echo 'No Odoo modules changed.'

                        echo 'Pylint check skipped.'
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


                /*
                 * No SSH.
                 *
                 * Jenkins and Odoo are assumed to be on the same
                 * machine.
                 *
                 * Copy the changed repository content directly
                 * into the Odoo custom addons directory.
                 */

                sh '''
                    set -e

                    echo "Jenkins workspace:"
                    pwd

                    echo ""

                    echo "Odoo custom addons directory:"
                    echo "${ODOO_CUSTOM_ADDONS}"

                    echo ""

                    echo "Checking target directory..."

                    test -d "${ODOO_CUSTOM_ADDONS}"

                    echo "Target directory exists."

                    echo ""

                    echo "Deploying custom addons..."

                    cp -r \
                        ${CHANGED_MODULES} \
                        "${ODOO_CUSTOM_ADDONS}/"

                    echo ""

                    echo "Custom addons deployed successfully."
                '''
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


                /*
                 * Odoo is running on the same machine.
                 *
                 * Therefore no SSH is required.
                 */

                sh '''
                    set -e

                    echo "Modules to upgrade:"

                    echo "${CHANGED_MODULES}"

                    echo ""

                    echo "Running Odoo module upgrade..."

                    ${ODOO_BIN} \
                        -d "${ODOO_DB}" \
                        --addons-path="${ODOO_CUSTOM_ADDONS},${ODOO_ADDONS},${ODOO_CORE_ADDONS}" \
                        -u "${CHANGED_MODULES}" \
                        --stop-after-init

                    echo ""

                    echo "Odoo module upgrade completed."
                '''
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


                sh '''
                    set -e

                    echo "Restarting Odoo service..."

                    sudo systemctl restart odoo

                    echo ""

                    echo "Odoo restart command completed."

                    echo ""

                    echo "Checking Odoo service status..."

                    sudo systemctl is-active --quiet odoo

                    echo "Odoo service is running."
                '''
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
                            set -e

                            echo "Waiting for Odoo to start..."

                            sleep 5

                            echo "Checking Odoo HTTP service..."

                            curl \
                                --fail \
                                --silent \
                                --show-error \
                                "http://${ODOO_SERVER}:${ODOO_PORT}/web/database/selector" \
                                > /dev/null

                            echo ""

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

                    echo 'Health check: SKIPPED'

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
