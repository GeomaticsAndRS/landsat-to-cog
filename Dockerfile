FROM osgeo/gdal

RUN apt-get update && apt-get install -y python3 python3-pip

RUN pip3 install click boto3 rasterio

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ADD process_landsat.py cogeo.py /opt/

WORKDIR /opt
RUN mkdir -p /opt/data/download && \
    mkdir -p /opt/data/out

CMD /opt/process_landsat.py
