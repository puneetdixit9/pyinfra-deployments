from pyinfra.operations import apt
from pyinfra.operations import server


def install_docker_with_key():
    # Add key
    server.shell(
        name='Add Docker key',
        commands=[
            "sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys EB3E94ADBE1229CF"
        ],
        _sudo=True
    )

    # Install Docker
    server.shell(
        name='Install Docker',
        commands=[
            "sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release -y",
            "curl -fsSL https://download.docker.com/linux/ubuntu/gpg > gpgkey",
            "sudo apt-key add gpgkey",
            "echo 'deb https://download.docker.com/linux/ubuntu bionic stable' | sudo tee /etc/apt/sources.list.d/docker.list",
            "sudo apt-get update",
            "sudo apt-get install docker-ce -y"
        ],
        _get_pty=True,
        _sudo=True
    )

install_docker_with_key()
