pipeline {
    agent any

    environment {
        DOCKER_ID = "salioudiedhiou"
        DOCKER_IMAGE = "jenkins_examen"
        DOCKER_TAG = "v.${BUILD_ID}.0"
        KUBE_CONFIG_DIR = "${WORKSPACE}/.kube"
    }

    stages {
        stage('Nettoyage préliminaire') {
            steps {
                script {
                    sh 'docker rm -f jenkins || true'
                }
            }
        }

        stage('Construction Docker') {
            steps {
                sh "docker build -t ${DOCKER_ID}/${DOCKER_IMAGE}:${DOCKER_TAG} ."
            }
        }

        stage('Exécution du conteneur') {
            steps {
                sh """
                    docker run -d -p 80:80 --name jenkins ${DOCKER_ID}/${DOCKER_IMAGE}:${DOCKER_TAG}
                    sleep 10
                """
            }
        }

        stage('Test de validation') {
            steps {
                sh "curl -f localhost || (echo 'Le test a échoué' && exit 1)"
            }
        }

        stage('Envoi sur Docker Hub') {
            environment {
                DOCKER_PASS = credentials("Pass_Examen_Jenkins")
            }
            steps {
                sh """
                    echo "${DOCKER_PASS}" | docker login -u ${DOCKER_ID} --password-stdin
                    docker push ${DOCKER_ID}/${DOCKER_IMAGE}:${DOCKER_TAG}
                """
            }
        }

        stage('Déploiement en dev') {
            environment {
                KUBECONFIG_CRED = credentials("config")
            }
            steps {
                script {
                    deployToEnvironment("dev", DOCKER_TAG, KUBECONFIG_CRED)
                }
            }
        }

        stage('Déploiement en qa') {
            environment {
                KUBECONFIG_CRED = credentials("config")
            }
            steps {
                script {
                    deployToEnvironment("qa", DOCKER_TAG, KUBECONFIG_CRED)
                }
            }
        }

        stage('Déploiement en staging') {
            environment {
                KUBECONFIG_CRED = credentials("config")
            }
            steps {
                script {
                    deployToEnvironment("staging", DOCKER_TAG, KUBECONFIG_CRED)
                }
            }
        }

        stage('Déploiement en production') {
            environment {
                KUBECONFIG_CRED = credentials("config")
            }
            steps {
                timeout(time: 15, unit: "MINUTES") {
                    input message: "Confirmez le déploiement en production ?", ok: "Déployer"
                }

                script {
                    sh """
                        mkdir -p ${KUBE_CONFIG_DIR}
                        cp ${KUBECONFIG_CRED} ${KUBE_CONFIG_DIR}/config
                        chmod 600 ${KUBE_CONFIG_DIR}/config

                        cp helm/values.yaml values-prod.yml
                        sed -i "s+tag.*+tag: ${DOCKER_TAG}+g" values-prod.yml

                        helm upgrade --install app helm \
                            --values=values-prod.yml \
                            --namespace=prod \
                            --kubeconfig=${KUBE_CONFIG_DIR}/config
                    """
                }
            }
        }
    }

    post {
        always {
            sh 'docker rm -f jenkins || true'
            sh "rm -rf ${KUBE_CONFIG_DIR} || true"
        }
        success {
            echo 'Pipeline exécuté avec succès!'
        }
        failure {
            echo 'Le pipeline a échoué. Veuillez vérifier les logs.'
        }
    }
}

// Fonction helper corrigée
def deployToEnvironment(String envName, String dockerTag, String kubeConfigFile) {
    def configPath = "${env.KUBE_CONFIG_DIR}/config"
    sh """
        mkdir -p ${env.KUBE_CONFIG_DIR}
        cp ${kubeConfigFile} ${configPath}
        chmod 600 ${configPath}

        cp helm/values.yaml values-${envName}.yml
        sed -i "s+tag.*+tag: ${dockerTag}+g" values-${envName}.yml

        helm upgrade --install app helm \
            --values=values-${envName}.yml \
            --namespace=${envName} \
            --kubeconfig=${configPath}
    """
}
