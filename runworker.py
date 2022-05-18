import os
import sys

from saq.worker import start


def main():
    sys.path.insert(0, os.getcwd())
    settings = sys.argv[1]
    start(settings)


if __name__ == "__main__":
    main()