import os

from dotenv import load_dotenv
from pyinfra.operations import apt, files, git, python, server

from nginx_configure import update_frontend_app_config

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)


APPLICATION_PATH = os.environ.get("APPLICATION_PATH")
NODE_VERSION = os.environ.get("NODE_VERSION")
SSH_USER = os.environ.get("SSH_USER")
REPO_BRANCH = os.environ.get("REPO_BRANCH")
APP_NAME = os.environ.get("APP_NAME")


nvm_dir = f"/home/{SSH_USER}/.nvm"

apt.update(name="Update package lists", _sudo=True)

apt.upgrade(name="Upgrade package lists", _sudo=True)

apt.packages(name="Ensuring the git package", packages=["git"])

apt.packages(
    name="Ensuring the curl package",
    packages=["curl"],
)

git.repo(
    name="Clone or Pull repo",
    src=os.environ.get("REPO_URL"),
    dest=APPLICATION_PATH,
    pull=True,
    branch=REPO_BRANCH,
)


server.shell(
    name="Install NVM",
    commands=["curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash"],
)


server.shell(
    name="Configure NVM and Install Node.js and Create build",
    commands=[
        f"export NVM_DIR='{nvm_dir}' && [ -s $NVM_DIR/nvm.sh ] && . $NVM_DIR/nvm.sh && nvm install {NODE_VERSION} && "
        f"nvm use {NODE_VERSION} && cd {APPLICATION_PATH} && npm install && npm run build",
    ],
)

# server.shell(
#     name="Configure NVM and Install Node.js and Create build",
#     commands=[
#         f"export NVM_DIR='{nvm_dir}' && [ -s $NVM_DIR/nvm.sh ] && . $NVM_DIR/nvm.sh && nvm install {NODE_VERSION} && "
#         f"nvm use {NODE_VERSION}",
#     ],
# )

apt.packages(
    name="Ensuring the nginx",
    packages=["nginx"],
)

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


files.get(
    name="Downloading nginx current config file",
    src="/etc/nginx/sites-available/server.conf",
    dest="./templates/current_server.conf",
    _sudo=True,
    _ignore_errors=True,
)


python.call(name="Updating Nginx Configuration", function=update_frontend_app_config)

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
