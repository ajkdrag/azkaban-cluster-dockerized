FROM openjdk:8

ENV DEBIAN_FRONTEND noninteractive
ARG AZK_VERSION=3.90.0
ARG FOLDER=azkaban
ARG AZK_REPO=https://github.com/azkaban/azkaban.git
RUN apt-get update -yqq \
    && apt-get install -yqq curl git

RUN git clone ${AZK_REPO} --branch ${AZK_VERSION} ${FOLDER}

RUN cd ${FOLDER}/azkaban-exec-server; \
    ../gradlew clean build -x test; \
    cd build/distributions; \
    tar -zxf azkaban-exec-server-${AZK_VERSION}.tar.gz;

RUN mv ${FOLDER}/azkaban-exec-server/build/distributions/azkaban-exec-server-${AZK_VERSION}/ .

WORKDIR azkaban-exec-server-${AZK_VERSION}
RUN curl -L -O https://cdn.mysql.com//Downloads/Connector-J/mysql-connector-j-8.0.31.tar.gz; \
    tar -zxf mysql-connector-j-8.0.31.tar.gz; \
    rm lib/mysql-connector*.jar; \
    cp mysql-connector-j-8.0.31/mysql-connector*.jar lib/

RUN echo '$(dirname $0)'"/internal/internal-start-executor.sh " \
            '"$@"' \
            " > exec_server_log.out; " \
            "sleep 5 && curl -G " \
            '"localhost:46050/executor?action=activate"' \
            " && echo;" \
            "tail -f exec_server_log.out" > bin/start-exec-server.sh

COPY conf/azkaban.properties conf/azkaban.properties
COPY conf/commonprivate.properties plugins/jobtypes/commonprivate.properties

EXPOSE 46050

RUN chmod +x bin/start-exec-server.sh
ENTRYPOINT ["/bin/sh", "-c", "bin/start-exec-server.sh"]
