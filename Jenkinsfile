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
                    // Fetch the latest commits
                    sh 'git fetch --all'

                    // Check if there are changes in the 'app' folder
                    def changes = sh(script: "git diff --name-only HEAD~1..HEAD", returnStdout: true).trim()
                    echo "Changes: ${changes}"

                    // Check if any changes are in the 'app' folder
                    def changesInAppFolder = changes.split('\n').any { it.startsWith('app/') }

                    // Determine if on main branch
                    def onMainBranch = env.GIT_BRANCH == 'origin/main' || env.GIT_BRANCH == 'main'

                    // Set action based on conditions
                    def action = ''
                    if (changesInAppFolder) {
                        if (onMainBranch) {
                            action = 'RunTestBuildDeploy'
                        } else {
                            action = 'RunTestOnly'
                        }
                    } else {
                        action = 'DoNothing'
                    }

                    echo "Action: ${action}"
                    currentBuild.description = action
                }
            }
        }

        stage('Test') {
            when {
                expression {
                    // Run if action is 'RunTestBuildDeploy' or 'RunTestOnly'
                    currentBuild.description == 'RunTestBuildDeploy' || currentBuild.description == 'RunTestOnly'
                }
            }
            steps {
                echo 'Running tests...'
                // Add your test steps here
            }
        }

        stage('Build') {
            when {
                expression {
                    // Run only if action is 'RunTestBuildDeploy'
                    currentBuild.description == 'RunTestBuildDeploy'
                }
            }
            steps {
                script {
                    echo 'Building image for deployment...'
                    dockerImage = docker.build("${registry}:${BUILD_NUMBER}")
                    echo 'Pushing image to DockerHub...'
                    docker.withRegistry('', registryCredential) {
                        dockerImage.push()
                        dockerImage.push('latest') // Tagging as 'latest'
                    }
                }
            }
        }

        stage('Deploy') {
            when {
                expression {
                    // Run only if action is 'RunTestBuildDeploy'
                    currentBuild.description == 'RunTestBuildDeploy'
                }
            }
            agent {
                kubernetes {
                    containerTemplate {
                        name 'helm'
                        image 'dinhln03/jenkins:lts'
                        alwaysPullImage true
                    }
                }
            }
            steps {
                script {
                    container('helm') {
                        sh("helm upgrade --install quote-generator ./helm/quote_gen_chart --namespace quote-gen ")
                    }
                }
            }
        }

        stage('Do Nothing') {
            when {
                expression {
                    // Run only if action is 'DoNothing'
                    currentBuild.description == 'DoNothing'
                }
            }
            steps {
                echo 'No changes detected in app folder, skipping tests, build, and deployment.'
            }
        }
    }
}