// Build alerts via homelab ntfy (#50). Credential: ntfy-homelab-writer-token.
// Topic ACL: /Docker/scripts/ntfy-topic-add.sh baseball-stats-ci
def notifyNtfy = { String result, String durationMs = '' ->
    withCredentials([string(credentialsId: 'ntfy-homelab-writer-token', variable: 'NTFY_TOKEN')]) {
        sh """#!/usr/bin/env bash
            set +e
            docker run --rm \\
              -v /Docker:/Docker:ro \\
              -v "\${WORKSPACE}:/ws:ro" \\
              --add-host host.docker.internal:host-gateway \\
              -e BUILD_RESULT='${result}' \\
              -e BUILD_DURATION_MS='${durationMs}' \\
              -e DOCKER_ROOT=/ws \\
              -e GITHUB_REPO=adamneighbors/baseball-stats-dashboard \\
              -e JENKINS_GIT_SHA="\${GIT_COMMIT}" \\
              -e NTFY_TOPIC="\${NTFY_TOPIC}" \\
              -e NTFY_BASE_URL="\${NTFY_BASE_URL}" \\
              -e NTFY_TOKEN="\${NTFY_TOKEN}" \\
              -e NTFY_TAGS="jenkins,baseball-stats" \\
              -e JOB_NAME="\${JOB_NAME}" \\
              -e BUILD_NUMBER="\${BUILD_NUMBER}" \\
              -e BUILD_URL="\${BUILD_URL}" \\
              alpine:3.20 sh -ec 'command -v curl >/dev/null || apk add --no-cache curl bash git >/dev/null; bash /Docker/scripts/jenkins-notify-ntfy.sh'
            ec=\$?
            if [[ \$ec -ne 0 ]]; then
              echo "WARN: ntfy notify failed (exit \$ec)" >&2
            fi
        """
    }
}

pipeline {
    environment {
        FEATURE_NAME        = BRANCH_NAME.replaceAll('[\\(\\)_/]','-').toLowerCase()
        BUILD_VERSION       = "${FEATURE_NAME}-${GIT_COMMIT.substring(0, 6)}"
        APP_NAME            = "baseball-stats-dashboard"
        GIT_LAST_AUTHOR     = sh(script: 'git --no-pager show -s --format=\'%an\' $GIT_COMMIT', returnStdout: true).trim()
        GIT_LAST_COMMIT     = sh(script: 'git log -1 --pretty=\'%B\'', returnStdout: true).trim()
        GIT_URL_COMMIT      = "${GIT_URL}/commit/${GIT_COMMIT}".replaceAll("baseball-stats-dashboard.git", "baseball-stats-dashboard")
        DATABASE            = "${APP_NAME}-${FEATURE_NAME}"
        NTFY_TOPIC          = 'baseball-stats-ci'
        NTFY_BASE_URL       = 'http://host.docker.internal:2586'
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
                    withCredentials([string(credentialsId: 'gitea-url', variable: 'REGISTRY'), string(credentialsId: 'baseball-owner', variable: 'OWNER')]) {
                        // Login to registry
                        docker.withRegistry("${REGISTRY}", "gitea-credentials") {
                            def app = docker.build("${OWNER}/${APP_NAME}:${CONTAINER_TAG}", ".")
                            app.push()
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                def result = currentBuild.currentResult ?: 'UNKNOWN'
                notifyNtfy(result, "${currentBuild.duration ?: ''}")
            }
            deleteDir()
        }
    }
}