import os

from dotenv import load_dotenv
from pyinfra.operations import apt, files, git, pip, python, server

from nginx_configure import update_backend_server_config

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

APPLICATION_PATH = os.environ.get("APPLICATION_PATH")
SERVER_PORT = os.environ.get("SERVER_PORT")
APPLICATION_ENV_FILE_PATH_ON_LOCAL = os.environ.get("APPLICATION_ENV_FILE_PATH_ON_LOCAL")
REPO_BRANCH = os.environ.get("REPO_BRANCH")
APP_NAME = os.environ.get("APP_NAME")


apt.update(name="Update package lists", _sudo=True)

apt.upgrade(name="Upgrade package lists", _sudo=True)

apt.packages(
    name="Ensuring git is installed",
    packages=["git"],
)

git.repo(
    name="Clone or Pull repo",
    src=os.environ.get("REPO_URL"),
    dest=APPLICATION_PATH,
    pull=True,
    branch=REPO_BRANCH,
)

apt.packages(
    name="Ensure python3.10 and python3.10-venv is Installed", packages=["python3.10", "python3.10-venv"], _sudo=True
)

pip.venv(
    name="Creating Virtual Environment",
    path=f"{APPLICATION_PATH}/venv",
    python="python3",
)

pip.packages(
    name="Installing requirements.txt",
    virtualenv=f"{APPLICATION_PATH}/venv",
    requirements=f"{APPLICATION_PATH}/requirements.txt",
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

apt.packages(name="Ensuring the nginx", packages=["nginx"], _sudo=True)


files.get(
    name="Downloading nginx current config file",
    src="/etc/nginx/sites-available/server.conf",
    dest="./templates/current_server.conf",
    _sudo=True,
    _ignore_errors=True,
)

python.call(name="Updating Nginx Configuration", function=update_backend_server_config)

files.put(
    name="Uploading nginx config template file",
    src="./templates/server.conf",
    dest="/etc/nginx/sites-available/server.conf",
    _sudo=True,
)

server.shell(
    name="Remove nginx default files",
    commands=[
        "cd /etc/nginx/sites-enabled && rm -rf default",
        "cd /etc/nginx/sites-available && rm -rf default",
        "cd /usr/share/nginx/html && rm -rf index.html",
    ],
    _sudo=True,
    _ignore_errors=True,
)

server.shell(
    name="Symlink server.conf file",
    commands=[
        "cd /etc/nginx/sites-enabled && ln -s /etc/nginx/sites-available/server.conf .",
    ],
    _sudo=True,
    _ignore_errors=True,
)

server.shell(
    name="Restart NGINX",
    commands=[
        "systemctl restart nginx",
    ],
    _sudo=True,
    _ignore_errors=True,
)
