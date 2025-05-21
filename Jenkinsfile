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
                    sh '''
                        docker rm -f jenkins || true
                        docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG .
                    '''
                }
            }
        }

        stage('Docker Run') {
            steps {
                script {
                    sh '''
                        docker run -d -p 80:80 --name jenkins $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                    '''
                }
            }
        }

        stage('Test Acceptance') {
            steps {
                script {
                    sh '''
                        echo "⏳ Attente du démarrage de l'application..."
                        sleep 5
                        echo "✅ Test de l'application avec curl:"
                        curl -f localhost || (echo "❌ Échec du test. Logs du conteneur:" && docker logs jenkins && exit 1)
                    '''
                }
            }
        }

        stage('Docker Push') {
            environment {
                DOCKER_PASS = credentials("Pass_Examen_Jenkins")
            }
            steps {
                script {
                    sh '''
                        echo "🔐 Connexion à Docker Hub..."
                        docker login -u $DOCKER_ID -p $DOCKER_PASS
                        docker push $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG
                    '''
                }
            }
        }

        stage('Deploy to dev') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    deployWithHelm("dev", "helm")
                }
            }
        }

        stage('Deploy to qa') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    deployWithHelm("qa", "helm")
                }
            }
        }

        stage('Deploy to staging') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    deployWithHelm("staging", "helm")
                }
            }
        }

        stage('Deploy to prod') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    input message: '🚨 Déploiement en production ?', ok: 'Oui, déployer'
                }
                script {
                    deployWithHelm("prod", "helm")
                }
            }
        }
    }
}

def deployWithHelm(namespace, chartPath) {
    sh """
        mkdir -p .kube
        cp \$KUBECONFIG .kube/config

        cp ${chartPath}/values.yaml values.yml
        sed -i "s+tag:.*+tag: ${env.DOCKER_TAG}+g" values.yml

        kubectl create namespace ${namespace} --dry-run=client -o yaml | kubectl apply -f -
        helm upgrade --install app-${namespace} ${chartPath} --values=values.yml --namespace ${namespace}
    """
}
