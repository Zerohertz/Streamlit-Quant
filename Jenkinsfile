void setBuildStatus(String message, String state, String context) {
    step([
        $class: "GitHubCommitStatusSetter",
        reposSource: [$class: "ManuallyEnteredRepositorySource", url: "https://github.com/Zerohertz/streamlit-quant"],
        contextSource: [$class: "ManuallyEnteredCommitContextSource", context: context],
        errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
        statusResultSource: [ $class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]] ]
    ]);
}

pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins/agent-type: kaniko
spec:
  containers:
    - name: jnlp
      image: jenkins/inbound-agent:latest
      resources:
        requests:
          memory: "512Mi"
          cpu: "500m"
        limits:
          memory: "1024Mi"
          cpu: "1000m"
    - name: ubuntu
      image: ubuntu:latest
      command:
        - sleep
      args:
        - "infinity"
      resources:
        requests:
          memory: "512Mi"
          cpu: "500m"
        limits:
          memory: "1024Mi"
          cpu: "1000m"
    - name: kaniko
      image: gcr.io/kaniko-project/executor:debug
      command:
        - /busybox/cat
      tty: true
      resources:
        requests:
          memory: "2048Mi"
          cpu: "2000m"
        limits:
          memory: "4096Mi"
          cpu: "4000m"
      volumeMounts:
        - name: docker-config
          mountPath: /kaniko/.docker/
  volumes:
    - name: docker-config
      secret:
        secretName: docker-config
            """
        }
    }
    environment {
        DOCKERHUB_USERNAME = "zerohertzkr"
        DEFAULT_TAG = "v1.0.0"
    }
    stages {
        stage("Check for Python Changes") {
            steps {
                script {
                    def status = sh(script: "git diff HEAD HEAD~ --name-only | grep -E '\\.py|Dockerfile'", returnStdout: true, returnStatus: true)
                    if (status == 0) {
                        env.hasPyChanges = "true"
                    } else {
                        env.hasPyChanges = "false"
                    }
                }
            }
        }
        stage("Kaniko") {
            when {
                expression { env.hasPyChanges == "true" }
            }
            steps {
                script {
                    container("ubuntu") {
                        sh """
                            apt-get update
                            apt-get install -y curl jq
                        """
                    }
                    def imageName = "streamlit-quant"
                    newTag = ""
                    container("ubuntu") {
                        def apiResponse = sh(script: """
                            curl -s "https://hub.docker.com/v2/repositories/${DOCKERHUB_USERNAME}/${imageName}/tags/?page_size=100"
                        """, returnStdout: true).trim()
                        echo "Docker Hub API Response: ${apiResponse}"
                        if (apiResponse.contains("httperror 404")) {
                            newTag = env.DEFAULT_TAG
                        } else {
                            def currentTag = sh(script: "echo '${apiResponse}' | jq -r '.results[].name' | sort -V | grep v | tail -n 1", returnStdout: true).trim()
                            echo "Current Tag: ${currentTag}"
                            def version = currentTag.replaceAll("[^0-9.]", "")
                            def (major, minor, patch) = version.tokenize(".").collect { it.toInteger() }
                            newTag = "v${major}.${minor}.${patch + 1}"
                        }
                        echo "New Tag: ${newTag}"
                    }
                    container("kaniko") {
                        script {
                            try {
                                setBuildStatus("Build...", "PENDING", "${DOCKERHUB_USERNAME}/${imageName}:${newTag}")
                                sh "/kaniko/executor --context ./ --dockerfile ./Dockerfile --destination ${DOCKERHUB_USERNAME}/${imageName}:latest --cleanup && mkdir -p /workspace"
                                sh "/kaniko/executor --context ./ --dockerfile ./Dockerfile --destination ${DOCKERHUB_USERNAME}/${imageName}:${newTag} --cleanup && mkdir -p /workspace"
                                setBuildStatus("Success", "SUCCESS", "${DOCKERHUB_USERNAME}/${imageName}:${newTag}")
                                slackSend(color: "good", message: ":+1:  <${env.BUILD_URL}|[${env.JOB_NAME}: ${STAGE_NAME}]> SUCCESS\nBRANCH NAME: ${env.BRANCH_NAME}\nIMAGE: <https://hub.docker.com/repository/docker/zerohertzkr/${imageName}/general|${DOCKERHUB_USERNAME}/${imageName}:${newTag}>")
                            } catch (Exception e) {
                                def STAGE_ERROR_MESSAGE = e.getMessage().split("\n")[0]
                                setBuildStatus(STAGE_ERROR_MESSAGE, "FAILURE", "${DOCKERHUB_USERNAME}/${imageName}:${newTag}")
                                slackSend(color: "danger", message: ":-1:  <${env.BUILD_URL}|[${env.JOB_NAME}: ${STAGE_NAME}]> FAIL\nBRANCH NAME: ${env.BRANCH_NAME}\nIMAGE: ${DOCKERHUB_USERNAME}/${imageName}:${newTag}\nError Message: ${STAGE_ERROR_MESSAGE}")
                                throw e
                            }
                        }
                    }
                }
            }
        }
        stage("Update Kubernetes Manifest and Push") {
            when {
                expression { env.hasPyChanges == "true" }
            }
            steps {
                script {
                    sh """
                        sed -i 's|zerohertzkr/streamlit-quant:v[0-9.]*|zerohertzkr/streamlit-quant:${newTag}|' k8s/deploy.yaml
                    """
                    withCredentials([usernamePassword(credentialsId: "GitHub", usernameVariable: "GIT_USERNAME", passwordVariable: "GIT_PASSWORD")]) {
                        sh '''
                        git config --global user.email "ohg3417@gmail.com"
                        git config --global user.name "${GIT_USERNAME}"
                        git config --global credential.helper "!f() { echo username=${GIT_USERNAME}; echo password=${GIT_PASSWORD}; }; f"
                        '''
                        sh """
                        git checkout main
                        git add k8s/deploy.yaml
                        git commit -m ":hammer: Update: ${newTag}"
                        git push origin main
                        """
                    }
                }
            }
        }
    }
}
