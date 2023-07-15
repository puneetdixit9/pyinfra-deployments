# Pyinfra-deployments

## Project Setup
* Create and activate a virtualenv.
* Install all dependency using below command.
```commandline
pip install -r requirements.txt
```
* Create a file on root folder with name .env with below values.
```commandline
REPO_URL=<REPO_URL_WITH_ACCESS_TOKEN>
REPO_BRANCH=<BRANCH_NAME>
APPLICATION_PATH=<APPLICATION_PATH_ON_REMOTE_MACHINE>
SSH_USER=<SSH_USERNAME>
SSH_PASSWORD=<SSH_USER_PASSWORD>
APP_SERVERS=<SERVER_IP_OR_DOMAIN_1,SERVER_IP_OR_DOMAIN_2>
```
* If deploying frontend application then add these details also in .env file.
```commandline
NODE_VERSION=<NODE_VERSION>
```
* And if deploying backend server then add these details in .env file.
```commandline
APPLICATION_ENV_FILE_PATH_ON_LOCAL=<YOUR APPLICATION ENV VARIABLES>
SERVER_PORT=<SERVER_PORT>
```
* Deploy your app on remote machine using the below command.
###### To deploy a Backend Server
```commandline
pyinfra inventories/staging.py setup_server.py    
```
###### To deploy a Frontend Application
```commandline
pyinfra inventories/staging.py setup_frontend.py    
```