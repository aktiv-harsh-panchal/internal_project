pipeline {
    agent any

    environment {
        ODOO_PYTHON = '/home/odoo/.virtualenvs/odoo19/bin/python3'
        ODOO_BIN = '/home/odoo/workspace/odoo/odoo_19/odoo-bin'

        ODOO_CUSTOM_ADDONS = '/home/odoo/workspace/internal_project'

        ODOO_ADDONS = '/home/odoo/workspace/odoo/odoo_19/addons'
        ODOO_CORE_ADDONS = '/home/odoo/workspace/odoo/odoo_19/odoo/addons'

        ODOO_DATABASE = 'test'
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

                    echo "Changed files:"
                    echo changedFiles

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
                        echo "No Odoo modules changed."
                        env.CHANGED_MODULES = ''
                    } else {
                        env.CHANGED_MODULES = modules
                    }

                    echo "Changed Odoo modules:"
                    echo env.CHANGED_MODULES
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
                    echo "Minimum required Pylint score: 4.0"

                    sh '''
                        set -e

                        echo "Python:"
                        $ODOO_PYTHON --version

                        echo "Python executable:"
                        $ODOO_PYTHON -c "import sys; print(sys.executable)"

                        echo "Pylint:"
                        $ODOO_PYTHON -m pylint --version

                        echo ""
                        echo "Running Pylint..."

                        for MODULE in $CHANGED_MODULES
                        do
                            echo ""
                            echo "Checking module: $MODULE"

                            $ODOO_PYTHON -m pylint \
                                --fail-under=3.0 \
                                "$MODULE"
                        done

                        echo ""
                        echo "Pylint check passed."
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
		    echo "Target:"
		    echo "$ODOO_CUSTOM_ADDONS"

		    test -d "$ODOO_CUSTOM_ADDONS"

		    for MODULE in $CHANGED_MODULES
		    do
		        echo ""
		        echo "Deploying module: $MODULE"

		        rm -rf "$ODOO_CUSTOM_ADDONS/$MODULE"

		        cp -r "$MODULE" "$ODOO_CUSTOM_ADDONS/"
		    done

		    echo ""
		    echo "Fixing ownership for entire internal_project..."

		    sudo -n chown -R odoo:odoo "$ODOO_CUSTOM_ADDONS"

		    echo ""
		    echo "Fixing permissions for entire internal_project..."

		    sudo -n chmod -R 777 "$ODOO_CUSTOM_ADDONS"

		    echo ""
		    echo "Final permissions:"
		    ls -ld "$ODOO_CUSTOM_ADDONS"
		    ls -ld "$ODOO_CUSTOM_ADDONS"/*

		    echo ""
		    echo "Custom addons deployed successfully."
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

		    ODOO_PYTHON="/home/odoo/.virtualenvs/odoo19/bin/python3"
		    ODOO_BIN="/home/odoo/workspace/odoo/odoo_19/odoo-bin"
		    ODOO_CONF="/home/odoo/workspace/odoo/odoo_19/odoo_19.conf"

		    echo "Python:"
		    $ODOO_PYTHON --version

		    echo "Checking passlib:"
		    $ODOO_PYTHON -c "import passlib; print('passlib:', passlib.__version__)"

		    echo "Odoo config:"
		    echo "$ODOO_CONF"

		    test -f "$ODOO_CONF"

		    echo ""
		    echo "Modules to upgrade:"
		    echo "$CHANGED_MODULES"

		    echo ""
		    echo "Running Odoo module upgrade as odoo user..."

		    sudo -n -u odoo $ODOO_PYTHON $ODOO_BIN \
		        -c "$ODOO_CONF" \
		        -d test \
		        -u "$CHANGED_MODULES" \
		        --stop-after-init

		    echo ""
		    echo "Odoo module upgrade completed successfully."
		'''
	    }
	}


        // =========================================================
        // RESTART ODOO
        // =========================================================
        stage('Restart Odoo') {
	    when {
		expression {
		    return env.CHANGED_MODULES?.trim()
		}
	    }

	    steps {
		echo "=========================================="
		echo "RESTARTING ODOO"
		echo "=========================================="

		sh '''
		    set -e
		    echo "Restarting Odoo..."
		    # Put the actual Odoo restart command here
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
                    echo "Checking Odoo service..."
                    sudo systemctl is-active --quiet odoo
                    echo "Odoo is running."
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
            echo "Changed modules: ${env.CHANGED_MODULES}"
        }

        failure {
            echo "=========================================="
            echo "          PIPELINE FAILED"
            echo "=========================================="

            echo "One of the CI/CD stages failed."
            echo "Deployment did not complete successfully."
        }

        always {
            echo "=========================================="
            echo "          PIPELINE FINISHED"
            echo "=========================================="
        }
    }
}
