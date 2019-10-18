FROM debian:buster-slim
RUN \
    apt-get update && \
    apt-get install -y --no-install-recommends python3-minimal python3-pip && \
    pip3 install setuptools && \
    apt-get clean
ENV LC_ALL C.UTF-8
ADD . /app
ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN pip3 install -e /app
ENV CONFIG=/app/config.ini
CMD /docker-entrypoint.sh estore
