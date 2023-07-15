import os

from pyinfra.operations import git, apt, pip, server, files
from dotenv import load_dotenv


dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

APPLICATION_PATH = os.environ.get("APPLICATION_PATH")
SERVER_PORT = os.environ.get("SERVER_PORT")
APPLICATION_ENV_FILE_PATH_ON_LOCAL = os.environ.get("APPLICATION_ENV_FILE_PATH_ON_LOCAL")
REPO_BRANCH = os.environ.get("REPO_BRANCH")


apt.update(
    name='Update package lists',
    _sudo=True
)

apt.upgrade(
    name="Upgrade package lists",
    _sudo=True
)

apt.packages(
    name="Ensuring git is installed",
    packages=['git'],
)

git.repo(
    name="Clone or Pull repo",
    src=os.environ.get('REPO_URL'),
    dest=APPLICATION_PATH,
    pull=True,
    branch=REPO_BRANCH,
)

apt.packages(
    name='Ensure python3.10 and python3.10-venv is Installed',
    packages=['python3.10', 'python3.10-venv'],
)

pip.venv(
    name="Creating Virtual Environment",
    path=f'{APPLICATION_PATH}/venv',
    python="python3",
)

pip.packages(
    name="Installing requirements.txt",
    virtualenv=f'{APPLICATION_PATH}/venv',
    requirements=f'{APPLICATION_PATH}/requirements.txt',
)

server.shell(
    name="Killing the existing process on Port: {SERVER_PORT}",
    commands=[f'kill -9 $(lsof -t -i:{SERVER_PORT})'],
    _sudo=True,
    _ignore_errors=True
)

files.put(
    name="Copy env file to the server",
    src=APPLICATION_ENV_FILE_PATH_ON_LOCAL,
    dest=f'{APPLICATION_PATH}/.env'
)

server.shell(
    name="Running Server...",
    commands=[
        f'cd {APPLICATION_PATH} && {APPLICATION_PATH}/venv/bin/python -m flask run --host 0.0.0.0 --port {SERVER_PORT} '
        f'> /dev/null 2>&1 &'
    ]
)

