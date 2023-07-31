import os

from dotenv import load_dotenv
from pyinfra import config
from pyinfra.operations import git, server

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

APPLICATION_PATH = os.environ.get("APPLICATION_PATH")
REPO_BRANCH = os.environ.get("REPO_BRANCH")
SERVER_PASSWORD = os.environ.get("SSH_PASSWORD")
HTTP_PROXY = os.environ.get("HTTP_PROXY")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY")
config.USE_SUDO_PASSWORD = SERVER_PASSWORD

commands = f"""
su - -c'
    export http_proxy={HTTP_PROXY}
    export https_proxy={HTTPS_PROXY}
    add-apt-repository universe -y
    apt update -y
    apt upgrade -y
    apt-get install -y git curl nginx
'
"""
server.shell(name="Updating APT packages and ensuring git and curl", commands=[commands], _sudo=True)

git.repo(
    name="Clone or Pull repo",
    src=os.environ.get("REPO_URL"),
    dest=APPLICATION_PATH,
    pull=True,
    branch=REPO_BRANCH,
)
