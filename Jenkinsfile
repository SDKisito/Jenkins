pipeline {
    agent any

    stages {
        stage('Docker Build') {
            steps {
                script {
                    def DOCKER_ID = "salioudiedhiou"
                    def DOCKER_IMAGE = "jenkins_examen"
                    def DOCKER_TAG = "v.${env.BUILD_ID}.0"
                    sh """
                        docker rm -f jenkins || true
                        docker build -t ${DOCKER_ID}/${DOCKER_IMAGE}:${DOCKER_TAG} .
                    """
                }
            }
        }

        stage('Docker Run') {
            steps {
                script {
                    def DOCKER_ID = "salioudiedhiou"
                    def DOCKER_IMAGE = "jenkins_examen"
                    def DOCKER_TAG = "v.${env.BUILD_ID}.0"
                    sh """
                        docker run -d -p 80:80 --name jenkins ${DOCKER_ID}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        sleep 10
                    """
                }
            }
        }

        stage('Test Acceptance') {
            steps {
                sh 'curl localhost'
            }
        }

        stage('Docker Push') {
            steps {
                script {
                    def DOCKER_ID = "salioudiedhiou"
                    def DOCKER_IMAGE = "jenkins_examen"
                    def DOCKER_TAG = "v.${env.BUILD_ID}.0"
                    withCredentials([string(credentialsId: 'Pass_Examen_Jenkins', variable: 'DOCKER_PASS')]) {
                        sh """
                            echo \$DOCKER_PASS | docker login -u ${DOCKER_ID} --password-stdin
                            docker push ${DOCKER_ID}/${DOCKER_IMAGE}:${DOCKER_TAG}
                        """
                    }
                }
            }
        }

        stage('Deploy to dev') {
            steps {
                script {
                    def DOCKER_TAG = "v.${env.BUILD_ID}.0"
                    withCredentials([file(credentialsId: 'config', variable: 'KUBECONFIG_FILE')]) {
                        sh """
                            rm -rf ~/.kube
                            mkdir -p ~/.kube
                            cat \$KUBECONFIG_FILE > ~/.kube/config
                            chmod 600 ~/.kube/config

                            cp helm/values.yaml values.yml
                            sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml

                            kubectl create namespace dev --dry-run=client -o yaml | kubectl apply -f -
                            helm upgrade --install app helm --values=values.yml --namespace dev
                        """
                    }
                }
            }
        }

        stage('Deploy to qa') {
            steps {
                script {
                    def DOCKER_TAG = "v.${env.BUILD_ID}.0"
                    withCredentials([file(credentialsId: 'config', variable: 'KUBECONFIG_FILE')]) {
                        sh """
                            rm -rf ~/.kube
                            mkdir -p ~/.kube
                            cat \$KUBECONFIG_FILE > ~/.kube/config
                            chmod 600 ~/.kube/config

                            cp helm/values.yaml values.yml
                            sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml

                            kubectl create namespace qa --dry-run=client -o yaml | kubectl apply -f -
                            helm upgrade --install app helm --values=values.yml --namespace qa
                        """
                    }
                }
            }
        }

        stage('Deploy to staging') {
            steps {
                script {
                    def DOCKER_TAG = "v.${env.BUILD_ID}.0"
                    withCredentials([file(credentialsId: 'config', variable: 'KUBECONFIG_FILE')]) {
                        sh """
                            rm -rf ~/.kube
                            mkdir -p ~/.kube
                            cat \$KUBECONFIG_FILE > ~/.kube/config
                            chmod 600 ~/.kube/config

                            cp helm/values.yaml values.yml
                            sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml

                            kubectl create namespace staging --dry-run=client -o yaml | kubectl apply -f -
                            helm upgrade --install app helm --values=values.yml --namespace staging
                        """
                    }
                }
            }
        }

        stage('Deploy to prod') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    input message: '🚨 Déploiement en production ?', ok: 'Oui, déployer'
                }
                script {
                    def DOCKER_TAG = "v.${env.BUILD_ID}.0"
                    withCredentials([file(credentialsId: 'config', variable: 'KUBECONFIG_FILE')]) {
                        sh """
                            rm -rf ~/.kube
                            mkdir -p ~/.kube
                            cat \$KUBECONFIG_FILE > ~/.kube/config
                            chmod 600 ~/.kube/config

                            cp helm/values.yaml values.yml
                            sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml

                            kubectl create namespace prod --dry-run=client -o yaml | kubectl apply -f -
                            helm upgrade --install app helm --values=values.yml --namespace prod
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            sh 'docker rm -f jenkins || true'
        }
    }
}
