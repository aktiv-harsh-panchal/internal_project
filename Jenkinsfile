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
        // STOP MANUALLY RUNNING ODOO
        //
        // Odoo is NOT managed by systemctl.
        // Jenkins stops the process directly.
        // =========================================================

        stage('Stop Odoo') {

            when {
                expression {
                    return env.CHANGED_MODULES?.trim()
                }
            }

            steps {

                echo "=========================================="
                echo "STOPPING ODOO"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Odoo binary:"
                    echo "$ODOO_BIN"

                    echo ""
                    echo "Searching for running Odoo process..."

                    ODOO_PIDS=$(pgrep -u odoo -f "$ODOO_BIN" || true)

                    if [ -n "$ODOO_PIDS" ]; then

                        echo "Running Odoo PID(s):"
                        echo "$ODOO_PIDS"

                        echo ""
                        echo "Sending TERM signal..."

                        sudo -n -u odoo kill $ODOO_PIDS || true

                        echo ""
                        echo "Waiting for Odoo to stop..."

                        for i in $(seq 1 30)
                        do

                            if pgrep -u odoo -f "$ODOO_BIN" > /dev/null
                            then
                                echo "Odoo still running... waiting ($i/30)"
                                sleep 1
                            else
                                echo "Odoo stopped successfully."
                                break
                            fi

                        done

                        if pgrep -u odoo -f "$ODOO_BIN" > /dev/null
                        then
                            echo ""
                            echo "Odoo did not stop after 30 seconds."
                            echo "Sending KILL signal..."

                            ODOO_PIDS=$(pgrep -u odoo -f "$ODOO_BIN" || true)

                            if [ -n "$ODOO_PIDS" ]; then
                                sudo -n -u odoo kill -9 $ODOO_PIDS || true
                            fi

                            sleep 2
                        fi

                    else

                        echo "No running Odoo process found."

                    fi

                    echo ""
                    echo "Checking port ${ODOO_PORT}..."

                    if ss -ltnp | grep -q ":${ODOO_PORT} "
                    then
                        echo "WARNING: Port ${ODOO_PORT} is still in use."
                        ss -ltnp | grep ":${ODOO_PORT} " || true
                    else
                        echo "Port ${ODOO_PORT} is free."
                    fi

                    echo ""
                    echo "=========================================="
                    echo "Odoo stop operation completed."
                    echo "=========================================="
                '''
            }
        }


        // =========================================================
        // UPGRADE ODOO MODULES
        //
        // Odoo is stopped before this stage.
        // --stop-after-init performs the database upgrade and exits.
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
        // START ODOO
        //
        // Odoo is manually managed.
        // Jenkins starts it directly as the odoo user.
        // =========================================================

        stage('Start Odoo') {

            when {
                expression {
                    return env.CHANGED_MODULES?.trim()
                }
            }

            steps {

                echo "=========================================="
                echo "STARTING ODOO"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Python:"
                    echo "$ODOO_PYTHON"

                    echo ""
                    echo "Odoo binary:"
                    echo "$ODOO_BIN"

                    echo ""
                    echo "Odoo config:"
                    echo "$ODOO_CONF"

                    test -f "$ODOO_BIN"
                    test -f "$ODOO_CONF"

                    echo ""
                    echo "Checking if Odoo is already running..."

                    EXISTING_PIDS=$(pgrep -u odoo -f "$ODOO_BIN" || true)

                    if [ -n "$EXISTING_PIDS" ]; then

                        echo "Odoo is already running."
                        echo "PID(s):"
                        echo "$EXISTING_PIDS"

                    else

                        echo "Odoo is not running."
                        echo "Starting Odoo as odoo user..."

                        sudo -n -u odoo sh -c "
                            nohup '$ODOO_PYTHON' '$ODOO_BIN' \
                                -c '$ODOO_CONF' \
                                > /home/odoo/workspace/odoo/odoo_19/odoo.log 2>&1 \
                                < /dev/null &
                        "

                        echo ""
                        echo "Waiting for Odoo to start..."

                        sleep 5

                    fi

                    echo ""
                    echo "Checking Odoo process..."

                    for i in $(seq 1 30)
                    do

                        if pgrep -u odoo -f "$ODOO_BIN" > /dev/null
                        then

                            echo ""
                            echo "Odoo process is running."

                            pgrep -u odoo -af "$ODOO_BIN"

                            break

                        else

                            echo "Waiting for Odoo process... ($i/30)"

                            sleep 1

                        fi

                    done

                    if ! pgrep -u odoo -f "$ODOO_BIN" > /dev/null
                    then

                        echo ""
                        echo "ERROR: Odoo process did not start."

                        echo ""
                        echo "Last 100 lines of Odoo log:"
                        echo "------------------------------------------"

                        tail -100 \
                            /home/odoo/workspace/odoo/odoo_19/odoo.log || true

                        exit 1
                    fi

                    echo ""
                    echo "=========================================="
                    echo "Odoo started successfully."
                    echo "=========================================="
                '''
            }
        }


        // =========================================================
        // ODOO SERVER CHECK
        // =========================================================

        stage('Odoo Server Check') {

            when {
                expression {
                    return env.CHANGED_MODULES?.trim()
                }
            }

            steps {

                echo "=========================================="
                echo "ODOO SERVER CHECK"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Checking Odoo HTTP server..."

                    echo ""
                    echo "URL:"
                    echo "http://127.0.0.1:${ODOO_PORT}/web/login"

                    echo ""

                    if curl -fsS \
                        --max-time 10 \
                        "http://127.0.0.1:${ODOO_PORT}/web/login" \
                        > /dev/null
                    then

                        echo "Odoo server is responding."
                        echo "Port ${ODOO_PORT} is active."

                    else

                        echo ""
                        echo "ERROR: Odoo server is NOT responding."

                        echo ""
                        echo "Odoo process:"
                        pgrep -u odoo -af "$ODOO_BIN" || true

                        echo ""
                        echo "Last 100 lines of Odoo log:"
                        tail -100 \
                            /home/odoo/workspace/odoo/odoo_19/odoo.log || true

                        exit 1
                    fi

                    echo ""
                    echo "=========================================="
                    echo "Odoo server check passed."
                    echo "=========================================="
                '''
            }
        }


        // =========================================================
        // ODOO HEALTH CHECK
        // =========================================================

        stage('Odoo Health Check') {

            when {
                expression {
                    return env.CHANGED_MODULES?.trim()
                }
            }

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

                    if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 500 ]
                    then

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

            echo ""
            echo "Odoo was restarted because module changes were detected."
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
