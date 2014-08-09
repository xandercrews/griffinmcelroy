FROM debian:wheezy
MAINTAINER noone

RUN apt-get update -y && apt-get install -y wget ca-certificates
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ wheezy-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN wget -O- https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
RUN apt-get update -y && apt-get upgrade && apt-get install -y postgresql-9.3 pgadmin3
RUN echo "host    all             all             0.0.0.0/0                 md5" >> /etc/postgresql/9.3/main/pg_hba.conf
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf

USER postgres

RUN /etc/init.d/postgresql start && \
	psql --command "CREATE USER test WITH SUPERUSER PASSWORD 'test';" && \
	createdb -O test test

EXPOSE 5432

CMD ["/usr/lib/postgresql/9.3/bin/postgres", "-D", "/var/lib/postgresql/9.3/main", "-c", "config_file=/etc/postgresql/9.3/main/postgresql.conf"]
