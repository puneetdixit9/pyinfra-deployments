import os

from pyinfra.operations import server, git, apt
from dotenv import load_dotenv

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)


APPLICATION_PATH = os.environ.get("APPLICATION_PATH")
NODE_VERSION = os.environ.get("NODE_VERSION")
SSH_USER = os.environ.get("SSH_USER")
REPO_BRANCH = os.environ.get("REPO_BRANCH")

nvm_dir = f'/home/{SSH_USER}/.nvm'

apt.update(
    name='Update package lists',
    _sudo=True
    )

apt.upgrade(
    name="Upgrade package lists",
    _sudo=True
)

apt.packages(
    name="Ensuring the git package",
    packages=['git']
)

apt.packages(
    name="Ensuring the curl package",
    packages=['curl'],
)

git.repo(
    name="Clone or Pull repo",
    src=os.environ.get('REPO_URL'),
    dest=APPLICATION_PATH,
    pull=True,
    branch=REPO_BRANCH,
)


server.shell(
    name='Install NVM',
    commands=['curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash'],
)


server.shell(
    name='Configure NVM and Install Node.js and Create build',
    commands=[
        f"export NVM_DIR='{nvm_dir}' && [ -s $NVM_DIR/nvm.sh ] && . $NVM_DIR/nvm.sh && nvm install {NODE_VERSION} && "
        f"nvm use {NODE_VERSION} && cd {APPLICATION_PATH} && npm install && npm run build",
    ]
)

server.shell(
    name="Copying build files to /usr/share/nginx/html",
    commands=[
        f"cp -R {APPLICATION_PATH}/build/* /usr/share/nginx/html",
        "systemctl restart nginx"
    ],
    _sudo=True
)
