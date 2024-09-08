pipeline {
    environment {
        FEATURE_NAME        = BRANCH_NAME.replaceAll('[\\(\\)_/]','-').toLowerCase()
        BUILD_VERSION       = "${FEATURE_NAME}-${GIT_COMMIT.substring(0, 6)}"
        APP_NAME            = "baseball-stats-dashboard"
        GIT_LAST_AUTHOR     = sh(script: 'git --no-pager show -s --format=\'%an\' $GIT_COMMIT', returnStdout: true).trim()
        GIT_LAST_COMMIT     = sh(script: 'git log -1 --pretty=\'%B\'', returnStdout: true).trim()
        GIT_URL_COMMIT      = "${GIT_URL}/commit/${GIT_COMMIT}".replaceAll("baseball-stats-dashboard.git", "baseball-stats-dashboard")
        DATABASE            = "${APP_NAME}-${FEATURE_NAME}"
    }
    agent any
    stages {
        stage('image-build/push') {
            when{
                expression { env.BRANCH_NAME == 'main' || env.BRANCH_NAME.contains('develop') || env.BRANCH_NAME.contains('release') || env.BRANCH_NAME.contains('PR-') || env.BRANCH_NAME.contains('feat-') }
            }
            steps {
                script {
                    // Set CONTAINER_TAG based on the branch name
                    if (env.BRANCH_NAME == 'main') {
                        env.CONTAINER_TAG = 'latest'
                    } else {
                        env.CONTAINER_TAG = env.FEATURE_NAME
                    }
                }
                script {
                    withCredentials([string(credentialsId: 'gitea-url', variable: 'REGISTRY')]) {
                        // Login to registry
                        docker.withRegistry("${REGISTRY}", "gitea-credentials") {
                            def app = docker.build("${APP_NAME}:${CONTAINER_TAG}", ".")
                            app.push()
                        }
                    }
                }
            }
        }
    }
    post{
        always{
            script {
                def cardConfig = readJSON file: 'google_chat_build_notification.json'

                googlechatnotification url: 'id:286fa71f-78d5-4189-9480-b7a0146e9d4d',
                messageFormat: 'card',
                message: cardConfig.toString().replaceAll('GIT_LAST_AUTHOR', "${GIT_LAST_AUTHOR}").replaceAll('GIT_LAST_COMMIT', "${GIT_LAST_COMMIT}").replaceAll('GIT_URL_COMMIT', "${GIT_URL_COMMIT}")
            }
            deleteDir()
        }
    }
}