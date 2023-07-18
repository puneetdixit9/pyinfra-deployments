import os

import nginx
from dotenv import load_dotenv

dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)

PREFIX_WORD = os.environ.get("PREFIX_WORD")
SERVER_PORT = os.environ.get("SERVER_PORT")
APP_NAME = os.environ.get("APP_NAME")


def update_backend_server_config():
    try:
        current_config = nginx.loadf("./templates/current_server.conf")
    except FileNotFoundError:
        current_config = nginx.loadf("./templates/default_server.conf")

    current_locations = [list(location.as_dict.keys())[0] for location in current_config.server.locations]
    if f"location /{PREFIX_WORD}" not in current_locations:
        current_config.server.add(
            nginx.Location(f"/{PREFIX_WORD}", nginx.Key("proxy_pass", f"http://localhost:{SERVER_PORT}"))
        )
    nginx.dumpf(current_config, "./templates/server.conf")


def update_frontend_app_config():
    try:
        current_config = nginx.loadf("./templates/current_server.conf")
    except FileNotFoundError:
        current_config = nginx.loadf("./templates/default_server.conf")

    current_locations = [list(location.as_dict.keys())[0] for location in current_config.server.locations]
    if f"location /{PREFIX_WORD}" not in current_locations:
        current_config.server.add(
            nginx.Location(f"/{PREFIX_WORD}", nginx.Key("try_files", f"$uri $uri/ /{APP_NAME}/index.html"))
        )
        print(current_config.filter(name="/static"))
        for child in current_config.server.children:
            if isinstance(child, nginx.Location) and child.value == "/static":
                if APP_NAME not in child.keys[0].value:
                    child.keys[0].value += f" /{APP_NAME}$uri"
                print(child.keys[0].value)
    nginx.dumpf(current_config, "./templates/server.conf")
