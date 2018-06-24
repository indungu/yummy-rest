pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        echo 'Building..'
        sh 'pip install -r reqiurements.txt'
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