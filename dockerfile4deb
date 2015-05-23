FROM debian:jessie

LABEL Description="This image is used to build a debian package of tuttle" Version="0.1"

RUN mkdir project_tuttle mkdir project_tuttle/tuttle && apt-get update && apt-get install -y python python-pip python-virtualenv dh-virtualenv debhelper

ADD tuttle project_tuttle/tuttle/tuttle/
ADD bin project_tuttle/tuttle/bin/
ADD debian project_tuttle/tuttle/debian/
ADD setup.py requirements.txt project_tuttle/tuttle/

WORKDIR project_tuttle/tuttle/

RUN virtualenv env_tuttle && . env_tuttle/bin/activate && pip install -r requirements.txt

VOLUME ["/result"]

CMD . env_tuttle/bin/activate && dpkg-buildpackage -us -uc && ls && ls .. && cp ../* /result