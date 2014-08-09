FROM sequenceiq/hadoop-docker
MAINTAINER noone

# replace SSH keys
RUN yes | ssh-keygen -q -N "" -t dsa -f /etc/ssh/ssh_host_dsa_key && \
    yes | ssh-keygen -q -N "" -t rsa -f /etc/ssh/ssh_host_rsa_key && \
    yes | ssh-keygen -q -N "" -t rsa -f /root/.ssh/id_rsa && \
    cp /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys

# configure hdfs for webhdfs
ADD hdfs-site.xml /usr/local/hadoop/etc/hadoop/

CMD ["/etc/bootstrap.sh", "-d"]

EXPOSE 50020 50090 50070 50010 50075 8031 8032 8033 8040 8042 49707 22 8088 8030
