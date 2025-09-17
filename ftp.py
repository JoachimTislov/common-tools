import argparse
from ftpretty import ftpretty
import os

"""
Usage:
    CLI: python ftp.py <local_dist> <remote_dist> [--js-bundle]
    with environment Variables:
        HOST: FTP server hostname
        USERNAME: FTP username
        PASSWORD: FTP password

    GitHub Workflow

    Environment variables need to be set as secrets in the repository, organization, user or enterprise.

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        # Note 3.x is not a valid version, specify a specific version like 3.11
        python-version: ${{ matrix.python-version OR '3.x' }}

    - name: Setup Python environment and install ftpretty
      run: |
        python -m venv venv
        source venv/bin/activate
        pip install ftpretty argparse

    - name: Deploy with FTP
      run: |
        python ftp.py <local_dist> <remote_dist> [--js-bundle]
      env:
        HOST: ${{ secrets.DEPLOY_HOST }}
        USERNAME: ${{ secrets.DEPLOY_USERNAME }}
        PASSWORD: ${{ secrets.DEPLOY_PASSWORD }}
"""


def main():
    args = parse_flags()

    f = ftpretty(
        host=os.environ["HOST"],
        user=os.environ["USERNAME"],
        password=os.environ["PASSWORD"],
        secure=True,
        port=21,
    )

    if args.js_bundle:
        delete_remote_directory(f, args.remote_dist + "/assets")

    upload_dir(f, args.local_dist, args.remote_dist)
    f.close()


# Uploads a local directory to a remote directory via FTP.
# f - ftpretty instance
# local_directory - path to the local directory to upload
# remote_directory - path to the remote directory to upload to
def upload_dir(f, local_directory, remote_directory):
    for file in os.listdir(local_directory):
        local_file_path = os.path.join(local_directory, file)
        if os.path.isfile(local_file_path):
            print(f"Uploading file: {local_file_path} to {remote_directory}")
            f.put(local_file_path, remote_directory)
        elif os.path.isdir(local_file_path):
            new_remote_directory = f"{remote_directory}{file}/"
            print(
                f"Child directory remotely: {new_remote_directory}, and locally: {local_file_path}"
            )
            upload_dir(f, local_file_path, new_remote_directory)


# Parses command-line flags.
# Returns:
#     argparse.Namespace: Parsed command-line arguments.
# Flags:
#     local_dist (str): Local distribution directory.
#     remote_dist (str): Remote distribution directory.
#     --js-bundle (bool): If set, deletes existing assets folder for JavaScript bundles.
def parse_flags():
    parser = argparse.ArgumentParser(description="Upload files via FTP")
    parser.add_argument("local_dist", help="Local distribution directory")
    parser.add_argument("remote_dist", help="Remote distribution directory")
    parser.add_argument(
        "--js-bundle",
        action="store_true",
        help="Delete existing assets folder for JavaScript bundles",
    )
    return parser.parse_args()


# Recursive deletion of a remote directory
# f - ftpretty instance
# remote_directory - path to the remote directory to delete
def delete_remote_directory(f, remote_directory):
    """Delete a remote directory and all its contents recursively."""
    try:
        print(f"Attempting to delete directory: {remote_directory}")
        files = f.list(remote_directory)
        for file_info in files:
            file_path = f"{remote_directory}/{file_info}"
            try:
                f.delete(file_path)
                print(f"Deleted file: {file_path}")
            except:
                delete_remote_directory(f, file_path)
        f.delete(remote_directory)
        print(f"Deleted directory: {remote_directory}")
    except Exception as e:
        print(f"Could not delete directory {remote_directory}: {e}")


if __name__ == "__main__":
    main()
