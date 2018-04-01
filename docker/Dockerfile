FROM ubuntu:xenial
MAINTAINER Lexman <tuttle@lexman.org>
RUN apt-get update && apt-get install -y python python-psycopg2 postgresql-client python-pip libcurl4-openssl-dev unixodbc-dev libssl-dev
RUN pip install --upgrade pip
RUN pip install https://github.com/lexman/tuttle/archive/master.zip
RUN chmod +x /usr/local/bin/tuttle*
VOLUME ["/project"]
WORKDIR /project