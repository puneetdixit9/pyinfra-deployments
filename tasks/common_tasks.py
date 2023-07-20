import os

from dotenv import load_dotenv
from pyinfra.operations import apt, git

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

APPLICATION_PATH = os.environ.get("APPLICATION_PATH")
REPO_BRANCH = os.environ.get("REPO_BRANCH")


apt.update(name="Update package lists", _sudo=True)

apt.upgrade(name="Upgrade package lists", _sudo=True)

apt.packages(name="Ensuring the git package", packages=["git"], _sudo=True)

apt.packages(name="Ensuring the curl package", packages=["curl"], _sudo=True)

apt.packages(name="Ensuring the unzip package", packages=["unzip"], _sudo=True)

git.repo(
    name="Clone or Pull repo",
    src=os.environ.get("REPO_URL"),
    dest=APPLICATION_PATH,
    pull=True,
    branch=REPO_BRANCH,
)
