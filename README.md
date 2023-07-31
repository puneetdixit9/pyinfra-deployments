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
PREFIX_WORD=<PREFIX_OF_APP_PATHS_SERVER_APIS>
HTTP_PROXY=<URL_OF_HTTP_PROXY>
HTTPS_PROXY=<URL_OF_HTTPS_PROXY>
```
###### Note :- For product attribute labelling frontend PREFIX_WORD can be 'pal' and for backend server PREFIX can be 'pal-api' but it should match with your Api's and Paths.

* If deploying frontend application then add these details also in .env file.
```commandline
NODE_VERSION=<NODE_VERSION>
APP_NAME=<YOUR_APP_NAME>
```
* And if deploying backend server then add these details in .env file.
```commandline
APPLICATION_ENV_FILE_PATH_ON_LOCAL=<YOUR APPLICATION ENV VARIABLES>
SERVER_PORT=<SERVER_PORT>
```
* Deploy your app or server on remote machine using the below command.
###### To deploy a Backend Server
```commandline
pyinfra inventories/staging.py setup_server.py
```
###### To deploy a Frontend Application
```commandline
pyinfra inventories/staging.py setup_frontend.py
```
