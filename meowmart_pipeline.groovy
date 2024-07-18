pipeline {
    agent {
        label 'jenkins-slave'
    }

    environment {
        GIT_REPO = 'git@github.com:ShaqDevOps/meowmart_terraform.git'
        MARKER_FILE = "${env.WORKSPACE}/.first_run_marker"
    }

    stages {
        stage('Print Environment') {
            steps {
                sh 'echo $PATH'
                sh 'which docker-compose'
                sh 'docker-compose --version'
            }
        }

        stage('Clone Repository') {
            steps {
                sshagent (credentials: ['github-ssh-key']) {
                    script {
                        if (fileExists('meowmartdev')) {
                            echo "Directory meowmartdev exists. Fetching updates."
                            dir('meowmartdev') {
                                sh 'git fetch --all'
                                sh 'git reset --hard origin/main'
                            }
                        } else {
                            echo "Directory meowmartdev does not exist. Cloning repository."
                            sh 'git clone -b main ${GIT_REPO}'
                        }
                    }
                }
                sh 'ls -la meowmartdev'
            }
        }

        stage('Create .env file') {
            steps {
                withCredentials([
                    string(credentialsId: 'DOMAIN', variable: 'DOMAIN')
                ]) {
                    script {
                        def envFileContents = """
                        DOMAIN=${DOMAIN}
                        """
                        writeFile file: 'meowmartdev/.env', text: envFileContents
                    }
                }
            }
        }

        stage('Conditional Execution') {
            steps {
                script {
                    if (!fileExists("${MARKER_FILE}")) {
                        // First run
                        sh '''
                            echo "First run - performing initial setup..."
                            echo "Creating marker file..."
                            touch ${MARKER_FILE}
                            
                            # Get certificates
                            echo "Getting certificates..."
                            docker-compose -f meowmartdev/docker-compose.deploy.yml run --rm certbot /opt/certify-init.sh

                            # Stop and remove containers, networks, volumes, and images
                            echo "Stopping services..."
                            docker-compose -f meowmartdev/docker-compose.deploy.yml down

                            # Build the services
                            echo "Building services..."
                            docker-compose -f meowmartdev/docker-compose.deploy.yml build

                            # Start the services in the background
                            echo "Starting services..."
                            docker-compose -f meowmartdev/docker-compose.deploy.yml up -d
                        '''
                    } else {
                        // Subsequent runs
                        sh '''
                            echo "Subsequent run - updating services..."
                            
                            echo "Stopping previous containers..."
                            docker stop meowmart_initial-proxy-1 meowmart_initial-app-1 || true
                            docker rm meowmart_initial-proxy-1 meowmart_initial-app-1 || true

                            # Stop and remove containers, networks, volumes, and images
                            echo "Stopping services..."
                            docker-compose -f meowmartdev/docker-compose.deploy.yml down

                            # Build the services
                            echo "Building services..."
                            docker-compose -f meowmartdev/docker-compose.deploy.yml build

                            # Start the services in the background
                            echo "Starting services..."
                            docker-compose -f meowmartdev/docker-compose.deploy.yml up -d
                        '''
                    }
                }
            }
        }
    }
}
