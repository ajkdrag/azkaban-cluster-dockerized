ARG AZK_VERSION=3.90.0
ARG FOLDER=azkaban

FROM openjdk:8 as builder

ENV DEBIAN_FRONTEND noninteractive
ARG AZK_VERSION
ARG FOLDER
ARG AZK_REPO=https://github.com/azkaban/azkaban.git

RUN apt-get update -yqq \
    && apt-get install -yqq curl git

RUN git clone ${AZK_REPO} --branch ${AZK_VERSION} ${FOLDER}

RUN cd ${FOLDER}/azkaban-db; \
	../gradlew build installDist; \
	cd build/distributions; \
	tar -zxf azkaban-db-${AZK_VERSION}.tar.gz;

FROM mysql:8.0.17 
MAINTAINER ajkdrag

ARG AZK_VERSION
ARG FOLDER

ENV MYSQL_DATABASE=azkaban \
    MYSQL_ROOT_PASSWORD=root

COPY --from=builder ${FOLDER}/azkaban-db/build/distributions/azkaban-db-${AZK_VERSION}/create-all-sql*.sql /docker-entrypoint-initdb.d/01.sql

COPY scripts/privileges.sql /docker-entrypoint-initdb.d/00.sql

EXPOSE 3306
