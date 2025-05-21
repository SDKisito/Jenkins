pipeline {
    agent any

    environment {
        DOCKER_ID = "salioudiedhiou"
        DOCKER_IMAGE = "jenkins_examen"
        DOCKER_TAG = "v.${BUILD_ID}.0"
        KUBECONFIG = "/home/passwd/jenkins_kube/config"
    }

    stages {

        stage('Docker Build') {
            steps {
                sh '''
                    docker rm -f jenkins || true
                    docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG .
                '''
            }
        }

        stage('Docker Run') {
            steps {
                sh '''
                    docker run -d -p 80:80 --name jenkins $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                '''
            }
        }

        stage('Test Acceptance') {
            steps {
                sh '''
                    echo "⏳ Attente du démarrage de l'application..."
                    sleep 10
                    for i in {1..30}; do
                        curl -f http://localhost && break || sleep 1
                    done
                    curl -f http://localhost || (echo "❌ Échec du test. Logs:" && docker logs jenkins && exit 1)
                '''
            }
        }

        stage('Docker Push') {
            environment {
                DOCKER_PASS = credentials("Pass_Examen_Jenkins")
            }
            steps {
                sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_ID --password-stdin
                    docker push $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                '''
            }
        }

        stage('Deploy to dev') {
            steps {
                script {
                    deployToEnv("dev")
                }
            }
        }

        stage('Deploy to qa') {
            steps {
                script {
                    deployToEnv("qa")
                }
            }
        }

        stage('Deploy to staging') {
            steps {
                script {
                    deployToEnv("staging")
                }
            }
        }

        stage('Deploy to prod') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    input message: '🚨 Déploiement en production ?', ok: 'Oui, déployer'
                }
                script {
                    deployToEnv("prod")
                }
            }
        }
    }

    post {
        always {
            sh "docker rm -f jenkins || true"
        }
    }
}

def deployToEnv(envName) {
    sh """
        mkdir -p .kube
        cp \$KUBECONFIG .kube/config
        chmod 600 .kube/config

        cp helm/values.yaml values.yml
        sed -i 's+tag:.*+tag: ${DOCKER_TAG}+g' values.yml

        kubectl create namespace ${envName} --dry-run=client -o yaml | kubectl apply -f -
        helm upgrade --install app-${envName} helm --values=values.yml --namespace ${envName}
    """
}
