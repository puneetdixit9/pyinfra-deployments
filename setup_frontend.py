import os

from dotenv import load_dotenv
from pyinfra import config, local
from pyinfra.operations import files, git, python, server

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
REPO_URL = os.environ.get("REPO_URL")
REPO_BRANCH = os.environ.get("REPO_BRANCH")

USE_PROXY = int(os.environ.get("FLAG_USE_PROXY", 0))
UPGRADE_APT_AND_INSTALL_COMMON_PACKAGES = int(os.environ.get("FLAG_UPGRADE_APT_AND_INSTALL_COMMON_PACKAGES", 0))
GIT_PULL_OR_CLONE = int(os.environ.get("FLAG_GIT_PULL_OR_CLONE", 0))
INSTALL_NODE = int(os.environ.get("FLAG_INSTALL_NODE", 0))
DEPLOY_BUILD = int(os.environ.get("FLAG_DEPLOY_BUILD", 0))
UPDATE_NGINX_CONF = int(os.environ.get("FLAG_UPDATE_NGINX_CONF", 0))
CREATE_BUILD = int(os.environ.get("FLAG_CREATE_BUILD", 0))
INSTALL_PACKAGE_USING_SUDO_SU = int(os.environ.get("FLAG_INSTALL_PACKAGE_USING_SUDO_SU", 0))

nvm_dir = f"/home/{SSH_USER}/.nvm"


if UPGRADE_APT_AND_INSTALL_COMMON_PACKAGES:
    local.include("./tasks/common_tasks.py")


if GIT_PULL_OR_CLONE:
    git.repo(
        name="Clone or Pull git repo",
        src=REPO_URL,
        dest=APPLICATION_PATH,
        pull=True,
        branch=REPO_BRANCH,
    )

if INSTALL_NODE and CREATE_BUILD:
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
elif INSTALL_NODE:
    commands = f"""
        curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash &&
        export NVM_DIR='{nvm_dir}' &&
        [ -s $NVM_DIR/nvm.sh ] &&
        . $NVM_DIR/nvm.sh &&
        nvm install {NODE_VERSION} &&
        nvm use {NODE_VERSION}
    """

if INSTALL_NODE:
    server.shell(name=f"Ensuring Node {NODE_VERSION}", commands=[commands], _sudo=True)  # noqa


if DEPLOY_BUILD:
    files.put(name="Putting build to server", src=f"{BUILD_PATH}", dest=f"{APPLICATION_PATH}")

    server.shell(
        name="Unzip build",
        commands=[f"rm -rf {APPLICATION_PATH}/build", f"unzip {APPLICATION_PATH}/build.zip -d {APPLICATION_PATH}"],
    )

if CREATE_BUILD or DEPLOY_BUILD:
    server.shell(
        name="Create directory for build files",
        commands=[f"mkdir /usr/share/nginx/html/{APP_NAME}"],
        _sudo=True,
        _ignore_errors=True,
    )

    server.shell(
        name=f"Copying build files to /usr/share/nginx/html/{APP_NAME}",
        commands=[f"cp -R {APPLICATION_PATH}/build/* /usr/share/nginx/html/{APP_NAME}"],
        _sudo=True,
    )

if UPDATE_NGINX_CONF:
    files.get(
        name="Downloading nginx current config file",
        src="/etc/nginx/sites-available/server.conf",
        dest="./templates/current_server.conf",
        _sudo=True,
        _ignore_errors=True,
    )

    python.call(name="Updating Nginx Configuration", function=update_frontend_app_config)

local.include("./tasks/nginx_tasks.py")
