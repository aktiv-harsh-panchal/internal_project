pipeline {

    agent any

    environment {
        PYTHON = "/home/odoo/.virtualenvs/odoo19/bin/python3"
        ODOO_BIN = "/home/odoo/workspace/odoo/odoo_19/odoo-bin"
        ODOO_CONFIG = "/home/odoo/workspace/odoo/odoo_19/odoo_19.conf"
        ODOO_LOG = "/home/odoo/workspace/odoo/odoo_19/odoo.log"

        DATABASE = "test"

        SOURCE_DIR = "/home/odoo/workspace/internal_project"

        PYLINT_MIN_SCORE = "3.0"

        ODOO_PORT = "8069"
    }

    stages {

        /*
         * Jenkins already performs SCM checkout automatically.
         * Therefore we do NOT perform another git checkout here.
         */

        stage('Git Information') {
            steps {

                echo "=========================================="
                echo "GIT INFORMATION"
                echo "=========================================="

                sh '''
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


        stage('Detect Changed Modules') {

            steps {

                script {

                    echo "=========================================="
                    echo "DETECTING CHANGED ODOO MODULES"
                    echo "=========================================="

                    def previousCommit = sh(
                        script: "git rev-parse HEAD~1",
                        returnStdout: true
                    ).trim()

                    echo "Previous commit: ${previousCommit}"
                    echo "Current commit: ${env.GIT_COMMIT ?: sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()}"

                    def changedFiles = sh(
                        script: """
                            git diff --name-only ${previousCommit} HEAD \
                            | grep -v '^.*__pycache__/.*' \
                            | grep -v '\\.pyc\$' \
                            | grep -v '^Jenkinsfile\$' \
                            | grep -v '^\\.gitignore\$' \
                            || true
                        """,
                        returnStdout: true
                    ).trim()

                    echo ""
                    echo "Changed files:"
                    echo "------------------------------------------"

                    if (changedFiles) {
                        echo changedFiles
                    } else {
                        echo "No relevant files changed."
                    }

                    /*
                     * Find first directory component.
                     *
                     * Example:
                     *
                     * ai_invoice_agent/models/account_move.py
                     *
                     * becomes:
                     *
                     * ai_invoice_agent
                     */

                    def modules = sh(
                        script: """
                            git diff --name-only ${previousCommit} HEAD \
                            | grep -v '^.*__pycache__/.*' \
                            | grep -v '\\.pyc\$' \
                            | grep -v '^Jenkinsfile\$' \
                            | grep -v '^\\.gitignore\$' \
                            | awk -F/ 'NF >= 2 {print \$1}' \
                            | sort -u \
                            | while read module; do
                                if [ -f "\$module/__manifest__.py" ]; then
                                    echo "\$module"
                                fi
                            done \
                            | tr '\\n' ' '
                        """,
                        returnStdout: true
                    ).trim()

                    echo ""
                    echo "Changed Odoo modules:"
                    echo "------------------------------------------"

                    if (modules) {
                        echo modules
                    } else {
                        echo "No Odoo modules changed."
                    }

                    env.CHANGED_MODULES = modules
                }
            }
        }


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
                    echo "Minimum required Pylint score: ${env.PYLINT_MIN_SCORE}"

                    sh '''
                        set -e

                        echo ""
                        echo "Python:"
                        ${PYTHON} --version

                        echo ""
                        echo "Python executable:"
                        ${PYTHON} -c "import sys; print(sys.executable)"

                        echo ""
                        echo "Pylint:"
                        ${PYTHON} -m pylint --version

                        echo ""
                        echo "Running Pylint..."
                        echo "------------------------------------------"

                        for module in ${CHANGED_MODULES}; do

                            echo ""
                            echo "Checking module: ${module}"

                            ${PYTHON} -m pylint \
                                --fail-under=${PYLINT_MIN_SCORE} \
                                ${module}

                        done

                        echo ""
                        echo "=========================================="
                        echo "Pylint check passed."
                        echo "=========================================="
                    '''
                }
            }
        }


        stage('Deploy Custom Addons') {

            when {
                expression {
                    return env.CHANGED_MODULES?.trim()
                }
            }

            steps {

                script {

                    echo "=========================================="
                    echo "DEPLOYING CUSTOM ADDONS"
                    echo "=========================================="

                    sh '''
                        set -e

                        echo "Jenkins workspace:"
                        pwd

                        echo ""
                        echo "Target directory:"
                        echo "${SOURCE_DIR}"

                        test -d "${SOURCE_DIR}"

                        echo ""
                        echo "Modules to deploy:"
                        echo "${CHANGED_MODULES}"

                        for module in ${CHANGED_MODULES}; do

                            echo ""
                            echo "=========================================="
                            echo "Deploying module: ${module}"
                            echo "=========================================="

                            if [ ! -d "${module}" ]; then
                                echo "ERROR: Module ${module} does not exist."
                                exit 1
                            fi

                            echo "Removing old module..."

                            rm -rf "${SOURCE_DIR}/${module}"

                            echo "Copying new module..."

                            cp -a "${module}" "${SOURCE_DIR}/"

                        done

                        echo ""
                        echo "Fixing ownership..."

                        sudo -n chown -R odoo:odoo "${SOURCE_DIR}"

                        echo ""
                        echo "Fixing permissions..."

                        sudo -n chmod -R 777 "${SOURCE_DIR}"

                        echo ""
                        echo "Final permissions:"
                        echo "------------------------------------------"

                        ls -ld "${SOURCE_DIR}"

                        for module in ${CHANGED_MODULES}; do

                            echo ""
                            echo "Module: ${module}"

                            ls -ld "${SOURCE_DIR}/${module}"

                        done

                        echo ""
                        echo "=========================================="
                        echo "Custom addons deployed successfully."
                        echo "=========================================="
                    '''
                }
            }
        }


        /*
         * IMPORTANT:
         *
         * Do not use:
         *
         * sudo fuser -k 8069/tcp
         *
         * because Jenkins does not have passwordless sudo for fuser.
         *
         * Instead we identify the Odoo process and terminate it.
         */

        stage('Stop Odoo') {
	    steps {
		echo "=========================================="
		echo "STOPPING ODOO"
		echo "=========================================="

		sh '''
		    set -e

		    echo "Checking port 8069..."

		    if ss -ltn | grep -q ':8069 '; then

		        echo "Port 8069 is currently in use."

		        echo "Finding process..."
		        sudo -n fuser -v 8069/tcp

		        echo "Stopping process using port 8069..."
		        sudo -n fuser -k 8069/tcp

		        echo "Waiting for port to be released..."

		        for i in $(seq 1 20); do
		            if ! ss -ltn | grep -q ':8069 '; then
		                echo "Port 8069 has been released."
		                break
		            fi

		            echo "Port still in use... waiting ($i/20)"
		            sleep 1
		        done

		    else
		        echo "Port 8069 is already free."
		    fi

		    echo ""
		    echo "Final port check..."

		    if ss -ltn | grep -q ':8069 '; then
		        echo "ERROR: Port 8069 is still in use."
		        sudo -n fuser -v 8069/tcp
		        exit 1
		    fi

		    echo "Odoo stopped successfully."
		'''
	    }
	}


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
                    ${PYTHON} --version

                    echo ""
                    echo "Odoo binary:"
                    echo "${ODOO_BIN}"

                    echo ""
                    echo "Odoo config:"
                    echo "${ODOO_CONFIG}"

                    echo ""
                    echo "Odoo database:"
                    echo "${DATABASE}"

                    test -f "${ODOO_CONFIG}"
                    test -f "${ODOO_BIN}"

                    MODULES_TO_UPGRADE=$(echo "${CHANGED_MODULES}" | tr ' ' ',')

                    echo ""
                    echo "Modules to upgrade:"
                    echo "${MODULES_TO_UPGRADE}"

                    echo ""
                    echo "Running Odoo module upgrade as odoo user..."
                    echo "------------------------------------------"

                    sudo -n -u odoo \
                        "${PYTHON}" \
                        "${ODOO_BIN}" \
                        -c "${ODOO_CONFIG}" \
                        -d "${DATABASE}" \
                        -u "${MODULES_TO_UPGRADE}" \
                        --stop-after-init

                    echo ""
                    echo "=========================================="
                    echo "Odoo module upgrade completed successfully."
                    echo "=========================================="
                '''
            }
        }


        stage('Start Odoo') {

            steps {

                echo "=========================================="
                echo "STARTING ODOO"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Python:"
                    echo "${PYTHON}"

                    echo ""
                    echo "Odoo binary:"
                    echo "${ODOO_BIN}"

                    echo ""
                    echo "Odoo config:"
                    echo "${ODOO_CONFIG}"

                    test -f "${ODOO_BIN}"
                    test -f "${ODOO_CONFIG}"


                    echo ""
                    echo "Checking if Odoo is already running..."

                    EXISTING_PIDS=$(pgrep -u odoo -f "${ODOO_BIN}" || true)

                    if [ -n "${EXISTING_PIDS}" ]; then

                        echo "Odoo is already running:"
                        echo "${EXISTING_PIDS}"

                    else

                        echo "Odoo is not running."

                        echo ""
                        echo "Checking port ${ODOO_PORT}..."

                        if ss -ltn | grep -q ":${ODOO_PORT} "; then

                            echo "ERROR: Port ${ODOO_PORT} is already in use."

                            ss -ltnp | grep ":${ODOO_PORT} " || true

                            exit 1
                        fi


                        echo ""
                        echo "Starting Odoo as odoo user..."

                        sudo -n -u odoo sh -c "
                            nohup '${PYTHON}' '${ODOO_BIN}' \
                            -c '${ODOO_CONFIG}' \
                            > '${ODOO_LOG}' 2>&1 \
                            < /dev/null &
                        "

                    fi


                    echo ""
                    echo "Waiting for Odoo to start..."

                    for i in $(seq 1 30); do

                        if pgrep -u odoo -f "${ODOO_BIN}" > /dev/null; then

                            echo "Odoo process started."

                            break

                        fi

                        echo "Waiting for Odoo process... (${i}/30)"

                        sleep 1

                    done


                    echo ""

                    if ! pgrep -u odoo -f "${ODOO_BIN}" > /dev/null; then

                        echo "ERROR: Odoo process did not start."

                        echo ""
                        echo "Last 100 lines of Odoo log:"
                        echo "------------------------------------------"

                        tail -100 "${ODOO_LOG}" || true

                        exit 1
                    fi


                    echo "Odoo process is running."

                    echo ""
                    echo "Checking port ${ODOO_PORT}..."

                    for i in $(seq 1 30); do

                        if ss -ltn | grep -q ":${ODOO_PORT} "; then

                            echo "Port ${ODOO_PORT} is listening."

                            break

                        fi

                        echo "Waiting for port ${ODOO_PORT}... (${i}/30)"

                        sleep 1

                    done


                    if ! ss -ltn | grep -q ":${ODOO_PORT} "; then

                        echo "ERROR: Odoo process is running but port ${ODOO_PORT} is not listening."

                        echo ""
                        echo "Odoo log:"
                        tail -100 "${ODOO_LOG}" || true

                        exit 1
                    fi


                    echo ""
                    echo "=========================================="
                    echo "Odoo started successfully."
                    echo "=========================================="
                '''
            }
        }


        stage('Odoo Server Check') {

            steps {

                echo "=========================================="
                echo "ODOO SERVER CHECK"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Checking Odoo process..."

                    pgrep -u odoo -f "${ODOO_BIN}"

                    echo ""
                    echo "Checking port ${ODOO_PORT}..."

                    ss -ltn | grep ":${ODOO_PORT} "

                    echo ""
                    echo "Odoo server is running correctly."
                '''
            }
        }


        stage('Odoo Health Check') {

            steps {

                echo "=========================================="
                echo "ODOO HEALTH CHECK"
                echo "=========================================="

                sh '''
                    set -e

                    echo "Checking HTTP endpoint..."

                    for i in $(seq 1 30); do

                        if curl -fsS \
                            --max-time 5 \
                            "http://127.0.0.1:${ODOO_PORT}/web/database/selector" \
                            > /dev/null; then

                            echo ""
                            echo "Odoo HTTP health check passed."

                            exit 0
                        fi

                        echo "Waiting for Odoo HTTP service... (${i}/30)"

                        sleep 2

                    done


                    echo ""
                    echo "ERROR: Odoo HTTP health check failed."

                    echo ""
                    echo "Last 100 lines of Odoo log:"
                    echo "------------------------------------------"

                    tail -100 "${ODOO_LOG}" || true

                    exit 1
                '''
            }
        }
    }


    post {

        always {

            echo "=========================================="
            echo "PIPELINE FINISHED"
            echo "=========================================="

        }

        success {

            echo "=========================================="
            echo "          PIPELINE SUCCESS"
            echo "=========================================="

            echo "Deployment completed successfully."

            echo "Changed modules: ${env.CHANGED_MODULES ?: 'None'}"

            echo "=========================================="
        }

        failure {

            echo "=========================================="
            echo "          PIPELINE FAILED"
            echo "=========================================="

            echo "One of the CI/CD stages failed."

            echo "Deployment did not complete successfully."

            echo "Changed modules: ${env.CHANGED_MODULES ?: 'None'}"

            echo ""
            echo "Check Odoo log:"
            echo "${ODOO_LOG}"

            echo "=========================================="
        }
    }
}
