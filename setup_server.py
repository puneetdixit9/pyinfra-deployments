import os

from dotenv import load_dotenv
from pyinfra import local, config
from pyinfra.operations import apt, files, pip, python, server

from nginx_configure import update_backend_server_config

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

APPLICATION_PATH = os.environ.get("APPLICATION_PATH")
SERVER_PORT = os.environ.get("SERVER_PORT")
APPLICATION_ENV_FILE_PATH_ON_LOCAL = os.environ.get("APPLICATION_ENV_FILE_PATH_ON_LOCAL")
APP_NAME = os.environ.get("APP_NAME")
SERVER_PASSWORD = os.environ.get('SSH_PASSWORD')
config.USE_SUDO_PASSWORD = SERVER_PASSWORD

# local.include("./tasks/common_tasks.py")
#

# apt.packages(
#     name="Ensure python3.10 and python3.10-venv is Installed", packages=["python3.10", "python3.10-venv"], _sudo=True
# )


commands_as_root = f"""
su - -c'
    add-apt-repository universe -y
    apt update -y
    apt upgrade -y
    apt install -y python3.11 python3.11-venv
'
"""

server.shell(
    name=f"Executing sudo su operations",
    commands=[commands_as_root],
    _sudo=True
)


# pip.venv(
#     name="Creating Virtual Environment",
#     path=f"{APPLICATION_PATH}/venv",
#     python="python3",
# )

# pip.packages(
#     name="Installing requirements.txt",
#     virtualenv=f"{APPLICATION_PATH}/venv",
#     requirements=f"{APPLICATION_PATH}/requirements.txt",
# )

# server.shell(
#     name=f"Killing the existing process on Port: {SERVER_PORT}",
#     commands=[f"kill -9 $(lsof -t -i:{SERVER_PORT})"],
#     _sudo=True,
#     _ignore_errors=True,
# )

# files.put(name="Copy env file to the server", src=APPLICATION_ENV_FILE_PATH_ON_LOCAL, dest=f"{APPLICATION_PATH}/.env")


# server.shell(
#     name="Running Server",
#     commands=[
#         f"cd {APPLICATION_PATH} && {APPLICATION_PATH}/venv/bin/python -m flask run --host 0.0.0.0 --port {SERVER_PORT} "
#         f"> /dev/null 2>&1 &"
#     ],
# )

# apt.packages(name="Ensuring the nginx", packages=["nginx"], _su_user=True)
# server.shell(
# name="Installing Nginx",
# su_user='root',
# commands=[f"apt install nginx -y "],
# )

# files.get(
#     name="Downloading nginx current config file",
#     src="/etc/nginx/sites-available/server.conf",
#     dest="./templates/current_server.conf",
#     _sudo=True,
#     _ignore_errors=True,
# )

# python.call(name="Updating Nginx Configuration", function=update_backend_server_config)

# local.include("./tasks/nginx_tasks.py")
