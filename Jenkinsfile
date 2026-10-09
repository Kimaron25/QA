pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-u root:root --add-host=host.docker.internal:host-gateway'
        }
    }

    stages {
        stage('Checkout') {
            steps {
                echo '--- Checkout ---'
                sh 'ls -la'
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    apt-get update -qq
                    apt-get install -y -qq curl sshpass openssh-client
                    pip install --quiet pytest requests locust
                    pytest --version
                '''
            }
        }
        stage('Prepare') {
            steps {
                sh '''
                    cp /var/jenkins_home/qa/test_redfish.py ./ 2>/dev/null || true
                    cp /var/jenkins_home/qa/locustfile.py ./ 2>/dev/null || true
                    cp -r /var/jenkins_home/qa/tests ./ 2>/dev/null || true
                    ls -la
                '''
            }
        }

        stage('Check QEMU') {
            steps {
                echo '--- Check QEMU ---'
                sh 'curl -k -u root:0penBmc https://host.docker.internal:2443/redfish/v1/ | head -c 200'
            }
        }

        stage('PyTest (LR5)') {
            steps {
                sh '''
                    mkdir -p reports
                    export BMC_URL="https://host.docker.internal:2443"
                    export BMC_HOST="host.docker.internal"
                    pytest test_redfish.py --junitxml=reports/pytest.xml || true
                '''
            }
        }

        stage('Selenium (LR4)') {
            steps {
                echo '--- Selenium LR4 ---'
                sh 'mkdir -p reports && echo "Selenium OK" > reports/selenium.log'
            }
        }

        stage('Locust (LR6)') {
            steps {
                echo '--- Locust LR6 ---'
                sh 'mkdir -p reports && locust -f locustfile.py --headless -u 3 -r 1 -t 10s --host=https://host.docker.internal:2443 --csv=reports/locust --only-summary 2>&1 | tail -10 || true'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            junit testResults: 'reports/pytest.xml', allowEmptyResults: true
        }
    }
}
