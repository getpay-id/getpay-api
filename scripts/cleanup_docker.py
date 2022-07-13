import shlex
import subprocess


def main():
    subprocess.run("docker image prune -f".split())
    subprocess.run("docker container prune -f".split())
    output = subprocess.check_output(
        shlex.split('docker images -f "dangling=true" -q'), stderr=subprocess.STDOUT
    ).decode()
    if output:
        subprocess.run("docker rmi -f {}".format(output).split())

    subprocess.run("docker builder prune -a -f".split())


if __name__ == "__main__":
    main()
