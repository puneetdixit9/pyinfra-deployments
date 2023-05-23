import os

from pyinfra import host
from pyinfra.operations import server, files, git, apt, pkg
from pyinfra import local
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.expanduser("~"), "pyinfra.env")
load_dotenv(dotenv_path)




CONTAINER_NAME=os.environ.get("CONTAINER_NAME")
DOCKER_IMAGE=os.environ.get("DOCKER_IMAGE")
DOCKER_TAG=os.environ.get("DOCKER_TAG")
APP_NAME = os.environ.get("APP_NAME")




repo_url = "https://github.com/puneetdixitstatusneo/pyinfra-test-app.git"
remote_path = f"/opt/apps/{APP_NAME}"

apt.update(
    name='Update package lists',
    _sudo=True
    )

apt.upgrade(
    name="Upgrade package lists",
    _sudo=True
)

apt.packages(
    name="Ensuring the required packages",
    packages=['git'],
    _sudo=True
)

server.shell(
    name='Setting /opt/apps/pyinfra-test-app to safe directory',
    commands=[
        'git config --global --add safe.directory /opt/apps/pyinfra-test-app'
    ],
    _sudo=True
)

git.repo(
    name=f"Clone or Pull repo {os.environ.get('REPO')}",
    src=os.environ.get('REPO_URL'),
    dest=remote_path,
    pull=True,
    branch="main",
    _sudo=True,
)

local.include('tasks/install_docker.py')
local.include('tasks/install_nginx.py')

server.shell(
    name='Build and run docker image ',
    commands=[
        f"cd /opt/apps/{APP_NAME}/ && sudo docker image build --rm -t {DOCKER_IMAGE}:{DOCKER_TAG} -f Dockerfile .",
        f"docker stop {CONTAINER_NAME} || true && docker rm {CONTAINER_NAME} || true",
        f"sudo docker run --name {CONTAINER_NAME} -p 5000:5000 -d --restart unless-stopped {DOCKER_IMAGE}:{DOCKER_TAG}"
        ],
    _get_pty=True,
    _sudo=True
)

files.put(
    name='Copy nginx conf from host to remote',
    src='./templates/nginx.conf',
    dest='/etc/nginx/sites-available/app.conf',
    _sudo=True,
)

server.shell(
    name='Restart on remote machine the nginx server with the new configuration',
    commands=[
        "sudo ln -s /etc/nginx/sites-available/app.conf /etc/nginx/sites-enabled/ || true",
        "sudo systemctl restart nginx",
        ],
    _sudo=True
)
