from pyinfra.operations import files, server

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
