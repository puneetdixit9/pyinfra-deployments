import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))


dotenv_path = os.path.join(os.path.dirname(basedir), ".env")
load_dotenv(dotenv_path)


ssh_port = os.environ.get("SSH_PORT", 22)
ssh_user = os.environ.get("SSH_USER")
ssh_password = os.environ.get("SSH_PASSWORD")
