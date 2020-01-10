# Using the latest Ubuntu LTS
FROM ubuntu:18.04

# Ensuring we are using the latest software
RUN apt update
RUN apt upgrade -y

# This app needs some stuff to work
RUN apt install -y \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        make \
        git \
        curl \
        locales \
        psmisc \
        software-properties-common \
        wget

## Configuring the locales and language settings to UTF-8.
RUN echo 'LC_ALL=en_US.UTF-8' > /etc/default/locale
RUN locale-gen en_US.UTF-8
RUN dpkg-reconfigure -f noninteractive locales
RUN localedef -i en_US -f UTF-8 en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# Add the software to the container
ADD . /app
WORKDIR /app

# We like Virtual Environments :)
RUN make venv
ENV VIRTUAL_ENV=/app/env
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN make pip

# Do we need some TPC ports?
EXPOSE 8080

# Time to run!
CMD make run
