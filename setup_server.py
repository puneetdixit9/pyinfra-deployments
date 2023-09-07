import os

from dotenv import load_dotenv
from pyinfra import config, local
from pyinfra.operations import files, git, pip, python, server

from nginx_configure import update_backend_server_config

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

APPLICATION_PATH = os.environ.get("APPLICATION_PATH")
SERVER_PORT = os.environ.get("SERVER_PORT")
APPLICATION_ENV_FILE_PATH_ON_LOCAL = os.environ.get("APPLICATION_ENV_FILE_PATH_ON_LOCAL")
APP_NAME = os.environ.get("APP_NAME")
SERVER_PASSWORD = os.environ.get("SSH_PASSWORD")
HTTP_PROXY = os.environ.get("HTTP_PROXY")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY")
config.USE_SUDO_PASSWORD = SERVER_PASSWORD
REPO_URL = os.environ.get("REPO_URL")
REPO_BRANCH = os.environ.get("REPO_BRANCH")


USE_PROXY = int(os.environ.get("FLAG_USE_PROXY", 0))
UPGRADE_APT_AND_INSTALL_COMMON_PACKAGES = int(os.environ.get("FLAG_UPGRADE_APT_AND_INSTALL_COMMON_PACKAGES", 0))
GIT_PULL_OR_CLONE = int(os.environ.get("FLAG_GIT_PULL_OR_CLONE", 0))
UPDATE_NGINX_CONF = int(os.environ.get("FLAG_UPDATE_NGINX_CONF", 0))
INSTALL_PYTHON = int(os.environ.get("FLAG_INSTALL_PYTHON", 0))
INSTALL_PACKAGE_USING_SUDO_SU = int(os.environ.get("FLAG_INSTALL_PACKAGE_USING_SUDO_SU", 0))


if GIT_PULL_OR_CLONE:
    git.repo(
        name="Clone or Pull git repo",
        src=REPO_URL,
        dest=APPLICATION_PATH,
        pull=True,
        branch=REPO_BRANCH,
    )


if UPGRADE_APT_AND_INSTALL_COMMON_PACKAGES:
    local.include("./tasks/common_tasks.py")

if INSTALL_PYTHON:
    if INSTALL_PACKAGE_USING_SUDO_SU:
        commands = (
            f"""
        su - -c'
            export http_proxy={HTTP_PROXY}
            export https_proxy={HTTPS_PROXY}
            apt-get install -y python3.10 python3.10-venv
        '
        """
            if USE_PROXY
            else """
        su - -c'
            apt-get install -y python3.10 python3.10-venv
        '
        """
        )
    else:
        commands = "apt-get install -y python3.10 python3.10-venv"

    server.shell(name="Ensuring Python3.10 and Virtual Environment", commands=[commands], _sudo=True)

pip.venv(
    name="Creating Virtual Environment",
    path=f"{APPLICATION_PATH}/venv",
    python="python3",
)

if USE_PROXY:
    commands = f"""
        export http_proxy={HTTP_PROXY} &&
        export https_proxy={HTTPS_PROXY} &&
        cd {APPLICATION_PATH} &&
        {APPLICATION_PATH}/venv/bin/python -m pip install -r requirements.txt
    """
else:
    commands = f"""
        cd {APPLICATION_PATH} &&
        {APPLICATION_PATH}/venv/bin/python -m pip install -r requirements.txt
    """

server.shell(
    name="Installing requirements.txt",
    commands=[commands],
)

server.shell(
    name=f"Killing the existing process on Port: {SERVER_PORT}",
    commands=[f"kill -9 $(lsof -t -i:{SERVER_PORT})"],
    _sudo=True,
    _ignore_errors=True,
)

files.put(name="Copy env file to the server", src=APPLICATION_ENV_FILE_PATH_ON_LOCAL, dest=f"{APPLICATION_PATH}/.env")


server.shell(
    name="Running Server",
    commands=[
        f"cd {APPLICATION_PATH} && {APPLICATION_PATH}/venv/bin/python -m flask run --host 0.0.0.0 --port {SERVER_PORT} "
        f"> /dev/null 2>&1 &"
    ],
)

if UPDATE_NGINX_CONF:
    files.get(
        name="Downloading nginx current config file",
        src="/etc/nginx/sites-available/server.conf",
        dest="./templates/current_server.conf",
        _sudo=True,
        _ignore_errors=True,
    )

    python.call(name="Updating Nginx Configuration", function=update_backend_server_config)

local.include("./tasks/nginx_tasks.py")
