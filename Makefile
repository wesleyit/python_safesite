ifndef VERBOSE
MAKEFLAGS += --no-print-directory
endif
SHELL := /bin/bash
TEST_PATH=./
.DEFAULT_GOAL := help


help:
	@ echo "Use one of the following targets:"
	@ tail -n +8 Makefile |\
	egrep "^[a-z]+[\ :]" |\
	tr -d : |\
	tr " " "/" |\
	sed "s/^/ - /g"
	@ echo "Read the Makefile for further details"

venv:
	@ echo "Creating a new virtualenv..."
	@ rm -rf env || true
	@ python3 -m venv env
	@ echo "Done, now you need to activate it. Run:"
	@ echo "source env/bin/activate"

pip:
	@ if [ -z "${VIRTUAL_ENV}" ]; then \
		echo "Not inside a virtualenv."; \
		exit 1; \
	fi
	@ echo "Upgrading pip..."
	@ pip install --upgrade pip
	@ echo "Updating pip packages:"
	@ pip install -r "requirements.txt"

reset:
	@ echo "Removing env and cache..."
	@ rm -rf .pytest_cache
	@ rm -rf .tox
	@ rm -rf dist
	@ rm -rf build
	@ rm -rf tests/__pycache__
	@ rm -rf *.egg-info
	@ rm -rf env
	@ echo "All done!"

clean:
	@ echo "Cleaning cache..."
	@ rm -rf .pytest_cache
	@ rm -rf .tox
	@ rm -rf dist
	@ rm -rf build
	@ rm -rf tests/__pycache__
	@ rm -rf *.egg-info
	@ echo "All done!"

lint:
	@ echo "Running flake8 and isort..."
	@ flake8 --exclude=.tox
	@ isort --skip-glob=.tox --recursive .
	@ echo "All done!"

run:
	@ python app.py

build:
	@ echo "Building Docker image..."
	@ docker build --rm -t python_safesite:latest .
	@ echo "All done!"

start:
	@ echo "Starting the container..."
	@ docker run --rm -ti -p 8000:8000 python_safesite:latest
