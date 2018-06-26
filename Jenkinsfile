pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        echo 'Building..'
        sh 'echo "Building images"'
      }
    }
    stage('Test') {
      steps {
        echo 'Testing..'
        sh 'pytest'
      }
    }
    stage('Deploy') {
      steps {
        echo 'Deploying....'
      }
    }
  }
}