pipeline {
    agent any

    environment {
        registry = 'dinhln03/quote-generator'
        registryCredential = 'dockerhub'
    }

    stages {
        stage('Check for Changes') {
            steps {
                script {
                    // Check if there are changes in the 'app' folder
                    def changes = sh(script: "git diff --name-only HEAD~1..HEAD", returnStdout: true).trim()
                    echo "Changes: ${changes}"
                    // Check if any changes are in the 'app' folder
                    def changesInAppFolder = changes.split("\n").any { it.startsWith('app/') }

                    if (changesInAppFolder) {
                        currentBuild.description = "App folder changes detected"
                    } else {
                        currentBuild.description = "No changes in app folder"
                    }
                }
            }
        }

        stage('Build') {
            when {
                expression {
                    // Run build only if on main branch anh app folder changes are detected
                    return currentBuild.description == "App folder changes detected" && env.GIT_BRANCH.startsWith('origin/main')
                }
            }
            steps {
                script {
                    echo 'Building image for deployment..'
                    dockerImage = docker.build("${registry}:${BUILD_NUMBER}")
                    echo 'Pushing image to DockerHub..'
                    docker.withRegistry('', registryCredential) {
                        dockerImage.push()
                        dockerImage.push('latest') // Tagging as 'latest'
                    }
                }
            }
        }

        stage('Test') {
            when {
                expression {
                    // Proceed to test stage if there are changes in 'app' folder or not deploying to main branch
                    return currentBuild.description == "App folder changes detected" || !env.GIT_BRANCH.startsWith('origin/main')
                }
            }
            steps {
                echo 'Running tests...'
                // Add your test steps here
            }
        }

        stage('Deploy') {
            when {
                branch 'main' // Only deploy if the branch is 'main'
                expression {
                    // Only proceed with deployment if 'app' folder has changed
                    return currentBuild.description == "App folder changes detected"
                }
            }
            agent {
                kubernetes {
                    containerTemplate {
                        name 'helm' // Name of the container to be used for helm upgrade
                        image 'dinhln03/jenkins:lts' // The image containing helm
                        alwaysPullImage true // Always pull image in case of using the same tag
                    }
                }
            }
            steps {
                script {
                    container('helm') {
                        sh("helm upgrade --install hpp ./helm-charts/hpp --namespace model-serving")
                    }
                }
            }
        }

        stage('Do Nothing') {
            when {
                expression {
                    // If there are no changes in 'app' folder and not on main branch, do nothing
                    return currentBuild.description == "No changes in app folder" && !env.GIT_BRANCH.startsWith('origin/main')
                }
            }
            steps {
                echo 'No changes detected in app folder, skipping deployment and tests.'
            }
        }
    }
}
