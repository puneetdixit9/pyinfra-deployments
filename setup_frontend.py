import os

from dotenv import load_dotenv
from pyinfra import config, local
from pyinfra.operations import files, python, server

from nginx_configure import update_frontend_app_config

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

APPLICATION_PATH = os.environ.get("APPLICATION_PATH")
NODE_VERSION = os.environ.get("NODE_VERSION")
SSH_USER = os.environ.get("SSH_USER")
APP_NAME = os.environ.get("APP_NAME")
BUILD_PATH = os.environ.get("BUILD_PATH")
SERVER_PASSWORD = os.environ.get("SSH_PASSWORD")
HTTP_PROXY = os.environ.get("HTTP_PROXY")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY")
config.USE_SUDO_PASSWORD = SERVER_PASSWORD
USE_PROXY = int(os.environ.get("USE_PROXY", 0))
INSTALL_PACKAGE_USING_SUDO_SU = int(os.environ.get("INSTALL_PACKAGE_USING_SUDO_SU", 0))

nvm_dir = f"/home/{SSH_USER}/.nvm"

local.include("./tasks/common_tasks.py")


if INSTALL_PACKAGE_USING_SUDO_SU:
    commands = (
        f"""
    su - -c'
        export http_proxy={HTTP_PROXY}
        export https_proxy={HTTPS_PROXY}
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
        export NVM_DIR='{nvm_dir}'
        [ -s $NVM_DIR/nvm.sh ]
        . $NVM_DIR/nvm.sh
        nvm install {NODE_VERSION}
        nvm use {NODE_VERSION}
        cd {APPLICATION_PATH}
        npm install
        npm run build
    '
    """
        if USE_PROXY
        else f"""
    su - -c'
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
        export NVM_DIR='{nvm_dir}'
        [ -s $NVM_DIR/nvm.sh ]
        . $NVM_DIR/nvm.sh
        nvm install {NODE_VERSION}
        nvm use {NODE_VERSION}
        cd {APPLICATION_PATH}
        npm install
        npm run build
    '
    """
    )
else:
    commands = f"""
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash &&
        export NVM_DIR='{nvm_dir}' &&
        [ -s $NVM_DIR/nvm.sh ] &&
        . $NVM_DIR/nvm.sh &&
        nvm install {NODE_VERSION} &&
        nvm use {NODE_VERSION} &&
        cd {APPLICATION_PATH} &&
        npm install &&
        npm run build
    """

# commands = f"""
#     curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash &&
#     export NVM_DIR='{nvm_dir}' &&
#     [ -s $NVM_DIR/nvm.sh ] &&
#     . $NVM_DIR/nvm.sh &&
#     nvm install {NODE_VERSION} &&
#     nvm use {NODE_VERSION}
# """

server.shell(name=f"Ensuring Node {NODE_VERSION}", commands=[commands], _sudo=True)

server.shell(
    name="Create directory for build files",
    commands=[f"mkdir /usr/share/nginx/html/{APP_NAME}"],
    _sudo=True,
    _ignore_errors=True,
)


# files.put(name="Putting build to server", src=f"{BUILD_PATH}", dest=f"{APPLICATION_PATH}")

# server.shell(
#     name="Unzip build",
#     commands=[f"rm -rf {APPLICATION_PATH}/build", f"unzip {APPLICATION_PATH}/build.zip -d {APPLICATION_PATH}"],
# )

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
