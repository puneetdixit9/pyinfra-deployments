import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))


dotenv_path = os.path.join(os.path.dirname(basedir), ".env")
load_dotenv(dotenv_path)

app_servers = os.environ.get("APP_SERVERS", "").split(",")
