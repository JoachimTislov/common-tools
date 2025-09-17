# FTP script documentation

Important to set the `cwd` to `common-tools/ftp` before running the test with `Make`

## Run tests

```bash
make test
```

View the [Makefile](Makefile) for details about the cmd.

## Usage

### CLI - command line interface

```bash
CLI: python ftp.py <local_directory> <remote_dist> [--js-bundle]
```

#### With environment Variables:

- HOST: FTP hostname - server address, can include port (e.g. ftp.example.com:21)
- USERNAME: FTP username
- PASSWORD: FTP password

### GitHub Workflow

Environment variables needs to be set as secrets in either the repository or the organization
- DEPLOY_HOST
- DEPLOY_USERNAME
- DEPLOY_PASSWORD
```yaml
- name: Set up Python
uses: actions/setup-python@v5
with:
# Note that '3.x' is not a valid version, specify a specific version like 3.11
python-version: ${{ matrix.python-version OR '3.x' }}

- name: Setup Python environment and install ftpretty
run: |
python -m venv venv
venv/bin/pip install ftpretty argparse

- name: Fetch deployment script
run: curl -O https://raw.githubusercontent.com/JoachimTislov/common-tools/main/ftp/ftp_client.py

- name: Deploy with FTP
run: |
python ftp_client.py [LOCAL_DIRECTORY_PATH] [REMOTE_DIRECTORY_PATH] ([--js-bundle] - if you want to delete existing assets folder for JS bundles, see lines 81 to 97)
env:
HOST: ${{ secrets.DEPLOY_HOST }}
USERNAME: ${{ secrets.DEPLOY_USERNAME }}
PASSWORD: ${{ secrets.DEPLOY_PASSWORD }}
```
