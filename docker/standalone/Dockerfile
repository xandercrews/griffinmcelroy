FROM debian:wheezy
MAINTAINER noone

VOLUME /src

RUN echo "deb-src http://http.debian.net/debian wheezy main" >> /etc/apt/sources.list && \
    echo "deb-src http://http.debian.net/debian wheezy-updates main" >> /etc/apt/sources.list

RUN apt-get update -y && \
    apt-get install -y python2.7 python-pip build-essential && \
    apt-get build-dep -y python-psycopg2

RUN apt-get update -y && \
    apt-get install -y wget ca-certificates

RUN wget https://bootstrap.pypa.io/ez_setup.py -O - | python

RUN apt-get update -y && \
    apt-get install -y vim

ADD bootstrap.sh /bin/
ADD griffin-develop.sh /bin/
ADD griffin-standalone.conf /conf/

RUN chmod 644 /bin/*.sh

CMD [ "python2.7", "/src/bin/gatherer_standalone.py", "/conf/griffin-standalone.conf" ]
