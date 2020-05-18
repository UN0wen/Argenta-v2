FROM postgres:latest 

ADD ./backups/argenta.sql /docker-entrypoint-initdb.d