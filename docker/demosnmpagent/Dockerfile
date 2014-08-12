FROM debian:wheezy
MAINTAINER noone

RUN echo "deb http://http.debian.net/debian/ wheezy contrib non-free" >> /etc/apt/sources.list

RUN apt-get update -y && \
    apt-get install -y snmpd snmp-mibs-downloader

RUN sed -i 's/^agentAddress/#\0/' /etc/snmp/snmpd.conf && \
    echo "agentAddress udp:161" >> /etc/snmp/snmpd.conf && \
    echo "rocommunity rosecret 0.0.0.0/0" >> /etc/snmp/snmpd.conf

CMD [ "/usr/sbin/snmpd", "-Le", "-Lf", "/dev/null", "-f" ]

EXPOSE 161/udp