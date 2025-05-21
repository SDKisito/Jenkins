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
                    sh '''
                        rm -rf .kube
                        mkdir -p .kube
                        chmod 700 .kube
                        cp $KUBECONFIG .kube/config
                        chmod 600 .kube/config

                        cp helm/values.yaml values.yml
                        sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml

                        kubectl create namespace dev --dry-run=client -o yaml | kubectl apply -f -
                        helm upgrade --install app-dev helm --values=values.yml --namespace dev
                    '''
                }
            }
        }

        stage('Deploy to qa') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    sh '''
                        rm -rf .kube
                        mkdir -p .kube
                        chmod 700 .kube
                        cp $KUBECONFIG .kube/config
                        chmod 600 .kube/config

                        cp helm/values.yaml values.yml
                        sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml

                        kubectl create namespace qa --dry-run=client -o yaml | kubectl apply -f -
                        helm upgrade --install app-qa helm --values=values.yml --namespace qa
                    '''
                }
            }
        }

        stage('Deploy to staging') {
            environment {
                KUBECONFIG = credentials("config")
            }
            steps {
                script {
                    sh '''
                        rm -rf .kube
                        mkdir -p .kube
                        chmod 700 .kube
                        cp $KUBECONFIG .kube/config
                        chmod 600 .kube/config

                        cp helm/values.yaml values.yml
                        sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml

                        kubectl create namespace staging --dry-run=client -o yaml | kubectl apply -f -
                        helm upgrade --install app-staging helm --values=values.yml --namespace staging
                    '''
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
                    sh '''
                        rm -rf .kube
                        mkdir -p .kube
                        chmod 700 .kube
                        cp $KUBECONFIG .kube/config
                        chmod 600 .kube/config

                        cp helm/values.yaml values.yml
                        sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml

                        kubectl create namespace prod --dry-run=client -o yaml | kubectl apply -f -
                        helm upgrade --install app-prod helm --values=values.yml --namespace prod
                    '''
                }
            }
        }
    }
}
