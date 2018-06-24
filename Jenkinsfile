pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        echo 'Building..'
        sh '''python3 -m venv venv
source venv/bin/activate
pip install -r reqiurements.txt'''
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