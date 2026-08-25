pipeline {
    agent any

    environment {
        ODOO_PYTHON = '/home/odoo/.virtualenvs/odoo19/bin/python3'
        ODOO_BIN = '/home/odoo/workspace/odoo/odoo_19/odoo-bin'
        ODOO_CONF = '/home/odoo/workspace/odoo/odoo_19/odoo_19.conf'

        ODOO_CUSTOM_ADDONS = '/home/odoo/workspace/internal_project'

        ODOO_ADDONS = '/home/odoo/workspace/odoo/odoo_19/addons'
        ODOO_CORE_ADDONS = '/home/odoo/workspace/odoo/odoo_19/odoo/addons'

        ODOO_DATABASE = 'test'
        ODOO_PORT = '8069'
    }

    stages {

        // =========================================================
        // CHECKOUT
        // =========================================================
        stage('Checkout') {
            steps {

                echo "=========================================="
                echo "CHECKOUT DEVELOPMENT BRANCH"
                echo "=========================================="

                deleteDir()

                git(
                    branch: 'development',
                    credentialsId: '550d0bdc-4a0c-432f-a86c-305bc922b13b',
                    url: 'https://github.com/aktiv-harsh-panchal/internal_project.git'
                )

                echo "Repository checkout completed."

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


        // =========================================================
        // DETECT CHANGED MODULES
        // =========================================================
        stage('Detect Changed Modules') {
            steps {

                script {

                    echo "=========================================="
                    echo "DETECTING CHANGED ODOO MODULES"
                    echo "=========================================="

                    def previousCommit = sh(
                        script: 'git rev-parse HEAD~1',
                        returnStdout: true
                    ).trim()

                    def changedFiles = sh(
                        script: "git diff --name-only ${previousCommit} HEAD",
                        returnStdout: true
                    ).trim()

                    echo ""
                    echo "Changed files:"
                    echo "------------------------------------------"

                    if (changedFiles) {
                        echo changedFiles
                    } else {
                        echo "No files changed."
                    }

                    def modules = sh(
                        script: """
                            git diff --name-only ${previousCommit} HEAD |
                            awk -F/ 'NF >= 2 {print \$1}' |
                            sort -u |
                            tr '\\n' ' '
                        """,
                        returnStdout: true
                    ).trim()

                    if (!modules) {

                        env.CHANGED_MODULES = ''

                        echo ""
                        echo "No Odoo modules changed."

                    } else {

                        env.CHANGED_MODULES = modules

                        echo ""
                        echo "Changed Odoo modules:"
                        echo "------------------------------------------"
                        echo env.CHANGED_MODULES
                    }
                }
            }
        }


        // =========================================================
        // PYLINT
        // =========================================================
        stage('Pylint Check') {

            when {
                expression {
                    return env.CHANGED_MODULES?.trim()
                }
            }

            steps {

                script {

                    echo "=========================================="
                    echo "PYLINT CHECK"
                    echo "=========================================="

                    echo "Changed modules: ${env.CHANGED_MODULES}"
                    echo "Minimum required Pylint score: 3.0"

                    sh '''
                        set -e

                        echo ""
                        echo "Python:"
                        "$ODOO_PYTHON" --version

                        echo ""
                        echo "Python executable:"
                        "$ODOO_PYTHON" -c \
                            "import sys; print(sys.executable)"

                        echo ""
                        echo "Pylint:"
                        "$ODOO_PYTHON" -m pylint --version

                        echo ""
                        echo "Running Pylint..."
                        echo "------------------------------------------"

                        for MODULE in $CHANGED_MODULES
                        do

                            echo ""
                            echo "Checking module: $MODULE"

                            "$ODOO_PYTHON" -m pylint \
                                --fail-under=3.0 \
                                "$MODULE"

                        done

                        echo ""
                        echo "=========================================="
                        echo "Pylint check passed."
                        echo "=========================================="
                    '''
                }
            }
        }


        // =========================================================
        // DEPLOY CUSTOM ADDONS
        // =========================================================
        stage('Deploy Custom Addons') {

            when {
                expression {
                    return env.CHANGED_MODULES?.trim()
                }
            }

            steps {

                echo "=========================================="
                echo "DEPLOYING CUSTOM ADDONS"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Jenkins workspace:"
                    pwd

                    echo ""
                    echo "Target directory:"
                    echo "$ODOO_CUSTOM_ADDONS"

                    test -d "$ODOO_CUSTOM_ADDONS"

                    echo ""
                    echo "Modules to deploy:"
                    echo "$CHANGED_MODULES"

                    for MODULE in $CHANGED_MODULES
                    do

                        echo ""
                        echo "Deploying module: $MODULE"

                        if [ ! -d "$MODULE" ]; then
                            echo "ERROR: Module directory does not exist:"
                            echo "$MODULE"
                            exit 1
                        fi

                        echo "Removing old module..."

                        rm -rf "$ODOO_CUSTOM_ADDONS/$MODULE"

                        echo "Copying new module..."

                        cp -r "$MODULE" "$ODOO_CUSTOM_ADDONS/"

                    done

                    echo ""
                    echo "Fixing ownership..."

                    sudo -n chown -R odoo:odoo "$ODOO_CUSTOM_ADDONS"

                    echo ""
                    echo "Fixing permissions..."

                    sudo -n chmod -R 777 "$ODOO_CUSTOM_ADDONS"

                    echo ""
                    echo "Final permissions:"
                    echo "------------------------------------------"

                    ls -ld "$ODOO_CUSTOM_ADDONS"

                    for MODULE in $CHANGED_MODULES
                    do
                        echo ""
                        echo "Module: $MODULE"
                        ls -ld "$ODOO_CUSTOM_ADDONS/$MODULE"
                    done

                    echo ""
                    echo "=========================================="
                    echo "Custom addons deployed successfully."
                    echo "=========================================="
                '''
            }
        }


        // =========================================================
        // UPGRADE ODOO MODULES
        // =========================================================
        stage('Upgrade Odoo Modules') {

            when {
                expression {
                    return env.CHANGED_MODULES?.trim()
                }
            }

            steps {

                echo "=========================================="
                echo "UPGRADING ODOO MODULES"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Python:"
                    "$ODOO_PYTHON" --version

                    echo ""
                    echo "Checking passlib:"

                    "$ODOO_PYTHON" -c \
                        "import passlib; print('passlib:', passlib.__version__)"

                    echo ""
                    echo "Odoo binary:"
                    echo "$ODOO_BIN"

                    echo ""
                    echo "Odoo config:"
                    echo "$ODOO_CONF"

                    echo ""
                    echo "Odoo database:"
                    echo "$ODOO_DATABASE"

                    test -f "$ODOO_CONF"
                    test -f "$ODOO_BIN"

                    echo ""
                    echo "Modules to upgrade:"
                    echo "------------------------------------------"
                    echo "$CHANGED_MODULES"

                    # Convert:
                    #
                    # ai_invoice_agent sale_project_management
                    #
                    # into:
                    #
                    # ai_invoice_agent,sale_project_management

                    MODULES_TO_UPGRADE=$(echo "$CHANGED_MODULES" | tr ' ' ',')

                    echo ""
                    echo "Odoo upgrade list:"
                    echo "$MODULES_TO_UPGRADE"

                    echo ""
                    echo "Running Odoo module upgrade as odoo user..."
                    echo "------------------------------------------"

                    sudo -n -u odoo \
                        "$ODOO_PYTHON" \
                        "$ODOO_BIN" \
                        -c "$ODOO_CONF" \
                        -d "$ODOO_DATABASE" \
                        -u "$MODULES_TO_UPGRADE" \
                        --stop-after-init

                    echo ""
                    echo "=========================================="
                    echo "Odoo module upgrade completed successfully."
                    echo "=========================================="
                '''
            }
        }


        // =========================================================
        // ODOO SERVER CHECK
        //
        // IMPORTANT:
        // Odoo is manually running on this server.
        // Jenkins must NOT start or restart Odoo.
        // =========================================================
        stage('Odoo Server Check') {

            steps {

                echo "=========================================="
                echo "ODOO SERVER CHECK"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Odoo is expected to be running manually."

                    echo ""
                    echo "Checking port:"
                    echo "$ODOO_PORT"

                    echo ""
                    echo "Checking Odoo HTTP server..."

                    if curl -fsS \
                        --max-time 10 \
                        "http://127.0.0.1:${ODOO_PORT}/web/login" \
                        > /dev/null
                    then

                        echo ""
                        echo "Odoo server is running."
                        echo "Port ${ODOO_PORT} is responding."
                        echo "No restart required."

                    else

                        echo ""
                        echo "ERROR: Odoo server is NOT responding."
                        echo ""
                        echo "Expected:"
                        echo "http://127.0.0.1:${ODOO_PORT}/web/login"
                        echo ""
                        echo "Please start Odoo manually."

                        exit 1
                    fi
                '''
            }
        }


        // =========================================================
        // ODOO HEALTH CHECK
        // =========================================================
        stage('Odoo Health Check') {

            steps {

                echo "=========================================="
                echo "ODOO HEALTH CHECK"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Checking Odoo health..."

                    HTTP_CODE=$(curl \
                        -s \
                        -o /dev/null \
                        -w "%{http_code}" \
                        --max-time 10 \
                        "http://127.0.0.1:${ODOO_PORT}/web/login")

                    echo ""
                    echo "HTTP status: $HTTP_CODE"

                    if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 500 ]; then

                        echo ""
                        echo "=========================================="
                        echo "Odoo health check passed."
                        echo "=========================================="

                    else

                        echo ""
                        echo "ERROR: Odoo health check failed."
                        echo "HTTP status: $HTTP_CODE"

                        exit 1
                    fi
                '''
            }
        }
    }


    // =============================================================
    // POST ACTIONS
    // =============================================================
    post {

        success {

            echo "=========================================="
            echo "          PIPELINE SUCCESS"
            echo "=========================================="

            echo "Deployment completed successfully."

            echo "Changed modules: ${env.CHANGED_MODULES ?: 'None'}"
        }

        failure {

            echo "=========================================="
            echo "          PIPELINE FAILED"
            echo "=========================================="

            echo "One of the CI/CD stages failed."

            echo "Deployment did not complete successfully."

            echo "Changed modules: ${env.CHANGED_MODULES ?: 'None'}"
        }

        always {

            echo "=========================================="
            echo "          PIPELINE FINISHED"
            echo "=========================================="
        }
    }
}
