# Python SafeSite

This application was developed for the purpose of training your penetration testing skills.
It is a simple site that can be explored in many different ways.
It was developed in Python with Flask and SQLite.

## Running inside Docker

To run inside Docker, have Docker installed,
GNU Make and Git.

```bash
git clone https://github.com/wesleyit/python_safesite.git
cd python_safesite
make build
make start
```

Then, visit `http://localhost:8000`.

## Running straight on the machine

For the brave ones, it is possible to run without a container.
This requires Python3, Venv, PIP, Git and GNU Make.
The app has been tested only on Linux, we don't know if it works directly on Mac OS or Windows, OK?

```bash
git clone https://github.com/wesleyit/python_safesite.git
cd python_safesite
make venv
source env/bin/activate
make pip
make run
```

## Disclaimer

> This application comes with security breaches and may compromise the server where it is installed. Watch out and be careful.
