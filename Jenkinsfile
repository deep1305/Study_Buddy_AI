pipeline {
    agent any

    environment {
        // Git (align with your actual repo)
        GIT_REPO_URL = "https://github.com/deep1305/Study_Buddy_AI.git"
        GIT_BRANCH = "main"
        GITHUB_CREDENTIALS_ID = "github-token"

        // Docker
        DOCKER_HUB_REPO = "deep1305/studybuddy"
        DOCKER_HUB_CREDENTIALS_ID = "dockerhub-token"
        IMAGE_TAG = "v${BUILD_NUMBER}"

        // Kubernetes / ArgoCD (adjust as needed)
        KUBE_CREDENTIALS_ID = "kubeconfig"
        KUBE_SERVER_URL = "https://192.168.49.2:8443"
        ARGOCD_SERVER = "136.116.77.133:31704/"
        ARGOCD_APP_NAME = "study"
    }

    stages {
        stage('Checkout GitHub') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scmGit(
                    branches: [[name: "*/${GIT_BRANCH}"]],
                    extensions: [],
                    userRemoteConfigs: [[credentialsId: "${GITHUB_CREDENTIALS_ID}", url: "${GIT_REPO_URL}"]]
                )
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image...'
                    dockerImage = docker.build("${DOCKER_HUB_REPO}:${IMAGE_TAG}")
                }
            }
        }

        stage('Push Image to DockerHub') {
            steps {
                script {
                    echo 'Pushing Docker image to DockerHub...'
                    // DockerHub registry endpoint for docker.withRegistry
                    docker.withRegistry('https://index.docker.io/v1/', "${DOCKER_HUB_CREDENTIALS_ID}") {
                        dockerImage.push("${IMAGE_TAG}")
                    }
                }
            }
        }

        stage('Update Deployment YAML with New Tag') {
            steps {
                sh """
                set -euo pipefail
                sed -i "s|image: ${DOCKER_HUB_REPO}:.*|image: ${DOCKER_HUB_REPO}:${IMAGE_TAG}|" manifests/deployment.yaml
                """
            }
        }

        stage('Commit Updated YAML') {
            steps {
                script {
                    // Expect "Username with password" where password is a GitHub PAT
                    withCredentials([usernamePassword(credentialsId: "${GITHUB_CREDENTIALS_ID}", usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PASS')]) {
                        sh """
                        set -euo pipefail
                        git config user.name "jenkins"
                        git config user.email "jenkins@local"
                        git add manifests/deployment.yaml
                        git commit -m "chore: update image tag to ${IMAGE_TAG}" || echo "No changes to commit"
                        git push https://${GIT_USER}:${GIT_PASS}@github.com/deep1305/Study_Buddy_AI.git HEAD:${GIT_BRANCH}
                        """
                    }
                }
            }
        }

        stage('Install kubectl & ArgoCD CLI (if missing)') {
            steps {
                sh '''
                set -euo pipefail
                echo "Installing kubectl/argocd locally (no sudo)..."

                mkdir -p ./.bin

                if ! command -v kubectl >/dev/null 2>&1; then
                  curl -sSLo ./.bin/kubectl "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                  chmod +x ./.bin/kubectl
                fi

                if ! command -v argocd >/dev/null 2>&1; then
                  curl -sSLo ./.bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
                  chmod +x ./.bin/argocd
                fi
                '''
            }
        }

        stage('Sync ArgoCD App') {
            steps {
                script {
                    // Requires Jenkins Kubernetes CLI plugin (withKubeConfig step)
                    withKubeConfig(credentialsId: "${KUBE_CREDENTIALS_ID}", serverUrl: "${KUBE_SERVER_URL}") {
                        sh '''
                        set -euo pipefail
                        export PATH="$PWD/.bin:$PATH"

                        argocd login "${ARGOCD_SERVER}" --username admin --password "$(kubectl get secret -n argocd argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)" --insecure
                        argocd app sync "${ARGOCD_APP_NAME}"
                        '''
                    }
                }
            }
        }    }
}