pipeline {
    agent any

    environment {
        DOCKER_ID = "salioudiedhiou"                  // Identifiant Docker Hub
        DOCKER_IMAGE = "jenkins_examen"              // Nom de l'image Docker
        DOCKER_TAG = "v.${BUILD_ID}.0"               // Tag de version basé sur l'ID de build Jenkins
    }

    stages {

        stage('Docker Build') {
            steps {
                script {
                    sh '''
                        docker rm -f jenkins || true                        # Supprimer l'ancien conteneur s'il existe
                        docker build -t $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG .   # Construire l'image Docker
                    '''
                }
            }
        }

        stage('Docker Run') {
            steps {
                script {
                    sh '''
                        docker run -d -p 80:80 --name jenkins $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG   # Lancer le conteneur
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
                        curl -f localhost || (echo "❌ Échec du test. Logs du conteneur:" && docker logs jenkins && exit 1)   # Test de l'app
                    '''
                }
            }
        }

        stage('Docker Push') {
            environment {
                DOCKER_PASS = credentials("Pass_Examen_Jenkins")   // Mot de passe Docker Hub stocké dans les credentials Jenkins
            }
            steps {
                script {
                    sh '''
                        echo "🔐 Connexion à Docker Hub..."
                        docker login -u $DOCKER_ID -p $DOCKER_PASS     # Connexion Docker
                        docker push $DOCKER_ID/$DOCKER_IMAGE:$DOCKER_TAG   # Push de l'image
                    '''
                }
            }
        }

        stage('Deploy to dev') {
            environment {
                KUBECONFIG = credentials("config")   // Fichier de config Kubernetes stocké dans Jenkins
            }
            steps {
                script {
                    sh '''
                        mkdir -p .kube
                        chmod 700 .kube
                        cp $KUBECONFIG .kube/config
                        chmod 600 .kube/config

                        cp helm/values.yaml values.yml
                        sed -i "s+tag:.*+tag: ${DOCKER_TAG}+g" values.yml   # Mise à jour du tag dans Helm values

                        kubectl create namespace dev --dry-run=client -o yaml | kubectl apply -f -
                        helm upgrade --install app-dev helm --values=values.yml --namespace dev   # Déploiement Helm
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
                        mkdir -p .kube
                        cp $KUBECONFIG .kube/config

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
                        mkdir -p .kube
                        cp $KUBECONFIG .kube/config

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
                    input message: '🚨 Déploiement en production ?', ok: 'Oui, déployer'   // Validation manuelle
                }
                script {
                    sh '''
                        mkdir -p .kube
                        cp $KUBECONFIG .kube/config

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
