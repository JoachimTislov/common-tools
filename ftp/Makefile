test:
	@if [ ! -d "venv" ]; then \
		echo "Creating virtual environment..."; \
		python -m venv venv; \
		echo "Installing dependencies..."; \
		venv/bin/pip install ftpretty argparse; \
	else \
		echo "Virtual environment already exists. Skipping setup."; \
	fi
	@venv/bin/python test_ftp_client.py
