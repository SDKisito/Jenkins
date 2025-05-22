pipeline {
    agent any

    environment {
        DOCKER_ID    = "salioudiedhiou"
        DOCKER_IMAGE = "jenkins_examen"
        DOCKER_TAG   = "v.${BUILD_ID}.0"
    }

    stages {
        stage("Print Variables") {
            steps {
                echo "DOCKER_ID = ${env.DOCKER_ID}"
                echo "DOCKER_IMAGE = ${env.DOCKER_IMAGE}"
                echo "DOCKER_TAG = ${env.DOCKER_TAG}"
                echo "BUILD_ID = ${env.BUILD_ID}"
                sh "printenv"
            }
        }

        stage("Docker Build") {
            steps {
                script {
                    sh '''
                    docker rm -f jenkins || true
                    docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG .
                    sleep 6
                    '''
                }
            }
        }

        stage("Docker Run") {
            steps {
                script {
                    sh '''
                    docker run -d -p 80:80 --name jenkins $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                    sleep 10
                    '''
                }
            }
        }

        stage("Test Acceptance") {
            steps {
                script {
                    sh '''
                    curl -f http://localhost || { echo "Test échoué"; exit 1; }
                    '''
                }
            }
        }

        stage("Docker Push") {
            environment {
                DOCKER_PASS = credentials("Pass_Examen_Jenkins")
            }
            steps {
                script {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_ID --password-stdin
                    docker push $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                    '''
                }
            }
        }

        stage("Préparer kubeconfig") {
            steps {
                script {
                    sh '''
                    rm -rf /var/lib/jenkins/.kube
                    mkdir -p /var/lib/jenkins/.kube

                    cp /home/passwd/.minikube/ca.crt /var/lib/jenkins/.kube/
                    cp /home/passwd/.minikube/profiles/minikube/client.crt /var/lib/jenkins/.kube/
                    cp /home/passwd/.minikube/profiles/minikube/client.key /var/lib/jenkins/.kube/

                    cat <<EOF | sudo tee /var/lib/jenkins/.kube/config > /dev/null
apiVersion: v1
kind: Config
clusters:
- name: minikube
  cluster:
    server: https://192.168.58.2:8443
    certificate-authority: /var/lib/jenkins/.kube/ca.crt
contexts:
- name: minikube
  context:
    cluster: minikube
    namespace: default
    user: minikube
current-context: minikube
users:
- name: minikube
  user:
    client-certificate: /var/lib/jenkins/.kube/client.crt
    client-key: /var/lib/jenkins/.kube/client.key
EOF

                    chown -R jenkins:jenkins /var/lib/jenkins/.kube
                    chmod 600 /var/lib/jenkins/.kube/config
                    chmod 600 /var/lib/jenkins/.kube/client.key
                    chmod 600 /var/lib/jenkins/.kube/client.crt
                    chmod 644 /var/lib/jenkins/.kube/ca.crt
                    '''
                }
            }
        }

        stage("Déploiement en dev") {
            steps {
                script {
                    sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    cp helm/values.yaml values.yml
                    sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml
                    helm upgrade --install app helm --values=values.yml --namespace dev --kubeconfig=$KUBECONFIG
                    '''
                }
            }
        }

        stage("Déploiement en QA") {
            steps {
                script {
                    sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    cp helm/values.yaml values.yml
                    sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml
                    helm upgrade --install app helm --values=values.yml --namespace qa --kubeconfig=$KUBECONFIG
                    '''
                }
            }
        }

        stage("Déploiement en staging") {
            steps {
                script {
                    sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    cp helm/values.yaml values.yml
                    sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml
                    helm upgrade --install app helm --values=values.yml --namespace staging --kubeconfig=$KUBECONFIG
                    '''
                }
            }
        }

        stage("Déploiement en prod") {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    input message: 'Souhaitez-vous déployer en production ?', ok: 'Déployer'
                }
                script {
                    sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    cp helm/values.yaml values.yml
                    sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml
                    helm upgrade --install app helm --values=values.yml --namespace prod --kubeconfig=$KUBECONFIG
                    '''
                }
            }
        }
    }

    post {
        always {
            echo 'Nettoyage...'
            sh 'docker rm -f jenkins || true'
            sh 'rm -rf .kube || true'
        }
        success {
            echo '✅ Pipeline exécuté avec succès !'
        }
        failure {
            echo '❌ Échec du pipeline. Consultez les logs.'
        }
    }
}
