import os

from dotenv import load_dotenv
from pyinfra import local
from pyinfra.operations import apt, files, python, server

from nginx_configure import update_frontend_app_config

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

APPLICATION_PATH = os.environ.get("APPLICATION_PATH")
NODE_VERSION = os.environ.get("NODE_VERSION")
SSH_USER = os.environ.get("SSH_USER")
APP_NAME = os.environ.get("APP_NAME")
BUILD_PATH = os.environ.get("BUILD_PATH")

nvm_dir = f"/home/{SSH_USER}/.nvm"

local.include("./tasks/common_tasks.py")


server.shell(
    name="Install NVM",
    commands=["curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash"],
)


# server.shell(
#     name="Configure NVM and Install Node.js and Create build",
#     commands=[
#         f"export NVM_DIR='{nvm_dir}' && [ -s $NVM_DIR/nvm.sh ] && . $NVM_DIR/nvm.sh && nvm install {NODE_VERSION} && "
#         f"nvm use {NODE_VERSION} && cd {APPLICATION_PATH} && npm install && npm run build",
#     ],
# )

server.shell(
    name="Configure NVM and Install Node.js",
    commands=[
        f"export NVM_DIR='{nvm_dir}' && [ -s $NVM_DIR/nvm.sh ] && . $NVM_DIR/nvm.sh && nvm install {NODE_VERSION} && "
        f"nvm use {NODE_VERSION}",
    ],
)

apt.packages(name="Ensuring the nginx", packages=["nginx"], _sudo=True)

server.shell(
    name="Create directory for build files",
    commands=[f"mkdir /usr/share/nginx/html/{APP_NAME}"],
    _sudo=True,
    _ignore_errors=True,
)

files.put(name="Putting build to server", src=f"{BUILD_PATH}", dest=f"{APPLICATION_PATH}")

server.shell(
    name="Unzip build",
    commands=[f"rm -rf {APPLICATION_PATH}/build", f"unzip {APPLICATION_PATH}/build.zip -d {APPLICATION_PATH}"],
)

server.shell(
    name=f"Copying build files to /usr/share/nginx/html/{APP_NAME}",
    commands=[f"cp -R {APPLICATION_PATH}/build/* /usr/share/nginx/html/{APP_NAME}"],
    _sudo=True,
)

files.get(
    name="Downloading nginx current config file",
    src="/etc/nginx/sites-available/server.conf",
    dest="./templates/current_server.conf",
    _sudo=True,
    _ignore_errors=True,
)

python.call(name="Updating Nginx Configuration", function=update_frontend_app_config)

local.include("./tasks/nginx_tasks.py")
