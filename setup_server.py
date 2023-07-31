import os

from dotenv import load_dotenv
from pyinfra import config, local
from pyinfra.operations import files, pip, python, server

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

local.include("./tasks/common_tasks.py")

commands = f"""
su - -c'
    export http_proxy={HTTP_PROXY}
    export https_proxy={HTTPS_PROXY}
    apt-get install -y python3.10 python3.10-venv
'
"""
server.shell(name="Ensuring Python3.10 and Virtual Environment", commands=[commands], _sudo=True)

pip.venv(
    name="Creating Virtual Environment",
    path=f"{APPLICATION_PATH}/venv",
    python="python3",
)

server.shell(
    name="Installing requirements.txt",
    commands=[
        f"export http_proxy={HTTP_PROXY} && export https_proxy={HTTPS_PROXY} && cd {APPLICATION_PATH} && source "
        f"venv/bin/activate && pip install -r requirements.txt"
    ],
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

files.get(
    name="Downloading nginx current config file",
    src="/etc/nginx/sites-available/server.conf",
    dest="./templates/current_server.conf",
    _sudo=True,
    _ignore_errors=True,
)

python.call(name="Updating Nginx Configuration", function=update_backend_server_config)

local.include("./tasks/nginx_tasks.py")
