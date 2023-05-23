# Pyinfra-deployments

## Project Setup
* Create and activate a virtualenv.
* Install all dependency using below command.
```commandline
pip install -r requirements.txt
```
* Create a file on home path with name pyinfra.env with these keys.
```commandline
REPO=repo_url
REPO_URL=repo url with access token if repo is private
APP_NAME=pyinfra-test-app
CONTAINER_NAME=awsome_app
DOCKER_IMAGE=my_py_app
DOCKER_TAG=0.0.0
```
* Add server ip in inventories/staging.py in app_servers list.
* Change your ssh credentials in group_data/app_servers.py file.
* Deploy your app on remote machine using the below command.
```commandline
pyinfra inventories\staging.py setup_server.py    
```