pipeline {
    agent any

    environment {
        DOCKER_ID = "salioudiedhiou"
        DOCKER_IMAGE = "jenkins_examen"
        DOCKER_TAG = "v.${BUILD_ID}.0"
    }

    stages {

        stage('Docker Build') {
            steps {
                script {
                    sh """
                    docker rm -f jenkins || true
                    docker build -t \$DOCKER_ID/\$DOCKER_IMAGE:\$DOCKER_TAG .
                    sleep 6
                    """
                }
            }
        }

        stage('Docker Run') {
            steps {
                script {
                    sh """
                    docker run -d -p 80:80 --name jenkins \$DOCKER_ID/\$DOCKER_IMAGE:\$DOCKER_TAG
                    sleep 10
                    """
                }
            }
        }

        stage('Test Acceptance') {
            steps {
                script {
                    sh """
                    curl -f http://localhost || { echo "Test échoué"; exit 1; }
                    """
                }
            }
        }

        stage('Docker Push') {
            environment {
                DOCKER_PASS = credentials("Pass_Examen_Jenkins")
            }
            steps {
                script {
                    sh """
                    echo \$DOCKER_PASS | docker login -u \$DOCKER_ID --password-stdin
                    docker push \$DOCKER_ID/\$DOCKER_IMAGE:\$DOCKER_TAG
                    """
                }
            }
        }

        stage('Déploiement en dev') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    sh """
                    rm -rf .kube
                    mkdir -p .kube
                    echo "$KUBECONFIG" > .kube/config
                    chmod 600 .kube/config
                    cp helm/values.yaml values.yml
                    sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml
                    helm upgrade --install app helm --values=values.yml --namespace dev --kubeconfig=.kube/config
                    """
                }
            }
        }

        stage('Déploiement en qa') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    sh """
                    rm -rf .kube
                    mkdir -p .kube
                    echo "\$KUBECONFIG" > .kube/config
                    chmod 600 .kube/config
                    cp helm/values.yaml values.yml
                    sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml
                    helm upgrade --install app helm --values=values.yml --namespace qa --kubeconfig=.kube/config
                    """
                }
            }
        }

        stage('Déploiement en staging') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    sh """
                    rm -rf .kube
                    mkdir -p .kube
                    echo "\$KUBECONFIG" > .kube/config
                    chmod 600 .kube/config
                    cp helm/values.yaml values.yml
                    sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml
                    helm upgrade --install app helm --values=values.yml --namespace staging --kubeconfig=.kube/config
                    """
                }
            }
        }

        stage('Déploiement en prod') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    input message: 'Souhaitez-vous déployer en production ?', ok: 'Déployer'
                }

                script {
                    sh """
                    rm -rf .kube
                    mkdir -p .kube
                    echo "\$KUBECONFIG" > .kube/config
                    chmod 600 .kube/config
                    cp helm/values.yaml values.yml
                    sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml
                    helm upgrade --install app helm --values=values.yml --namespace prod --kubeconfig=.kube/config
                    """
                }
            }
        }
    }

    post {
        always {
            script {
                sh 'docker rm -f jenkins || true'
                sh 'rm -rf .kube || true'
            }
        }
        success {
            echo '✅ Pipeline exécuté avec succès !'
        }
        failure {
            echo '❌ Échec du pipeline. Consultez les logs.'
        }
    }
}
