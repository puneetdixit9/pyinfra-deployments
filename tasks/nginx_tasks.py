import os

from dotenv import load_dotenv
from pyinfra import config
from pyinfra.operations import files, server

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

SERVER_PASSWORD = os.environ.get("SSH_PASSWORD")
config.USE_SUDO_PASSWORD = SERVER_PASSWORD

server.shell(
    name="Remove current server.conf",
    commands=["rm -rf /etc/nginx/sites-available/server.conf"],
    _sudo=True,
    _ignore_errors=True,
)


files.put(
    name="Uploading nginx config template file",
    src="./templates/server.conf",
    dest="/etc/nginx/sites-available/server.conf",
    _sudo=True,
)

server.shell(
    name="Remove nginx default files",
    commands=[
        "rm -rf /etc/nginx/sites-enabled/default /etc/nginx/sites-available/default /usr/share/nginx/html/index.html"
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
