FROM geographica/gdal2:2.3.2

RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip3 install click

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /opt
