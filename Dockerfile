# Using the latest Ubuntu LTS
FROM ubuntu:18.04

# Ensuring we are using the latest software
RUN apt update
RUN apt upgrade -y

# This app needs some stuff to work
RUN apt install -y \
        python3 \
        python3-dev \
        python3-venv \
        make \
        git

# Add the software to the container
ADD . /app
WORKDIR /app

# We like Virtual Environments :)
RUN make venv
ENV VIRTUAL_ENV=/app/env
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN make pip

# Do we need some TPC ports?
EXPOSE 8000

# Time to run!
CMD make run
