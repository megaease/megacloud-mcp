import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from megacloud_mcp import server


def main():
    server.run()


if __name__ == "__main__":
    main()
