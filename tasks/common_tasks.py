import os

from dotenv import load_dotenv
from pyinfra import config
from pyinfra.operations import server

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

APPLICATION_PATH = os.environ.get("APPLICATION_PATH")
REPO_BRANCH = os.environ.get("REPO_BRANCH")
SERVER_PASSWORD = os.environ.get("SSH_PASSWORD")
HTTP_PROXY = os.environ.get("HTTP_PROXY")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY")
USE_PROXY = int(os.environ.get("FLAG_USE_PROXY", 0))
INSTALL_PACKAGE_USING_SUDO_SU = int(os.environ.get("FLAG_INSTALL_PACKAGE_USING_SUDO_SU", 0))
config.USE_SUDO_PASSWORD = SERVER_PASSWORD

if INSTALL_PACKAGE_USING_SUDO_SU:
    commands = (
        f"""
    su - -c'
        export http_proxy={HTTP_PROXY}
        export https_proxy={HTTPS_PROXY}
        apt update -y
        apt upgrade -y
        apt install -y git curl nginx unzip
    '
    """
        if USE_PROXY
        else """
    su - -c'
        apt update -y
        apt upgrade -y
        apt install -y git curl nginx unzip
    '
    """
    )
else:
    commands = "apt update -y && apt upgrade -y && apt install -y git curl nginx unzip"

server.shell(name="Updating APT packages and ensuring git and curl", commands=[commands], _sudo=True)
