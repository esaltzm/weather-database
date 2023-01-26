FROM public.ecr.aws/lambda/python@sha256:e1948dc355b1d65f11ffe48d15c46b4e4aad0ea77851b63914f67bcaa678567f
RUN yum -y install  \
    gcc \
    jasper-devel \
    jasper-libs \
    openjpeg2-tools \
    openjpeg2-devel \ 
    openjpeg2 \
    gzip \
    tar \
    gcc \
    make \
    cmake \
    wget \
    && yum clean all
ENV ECCODES_URL=https://confluence.ecmwf.int/download/attachments/45757960/eccodes-2.10.0-Source.tar.gz?api=v2 \
    ECCODES_VERSION=eccodes-2.10.0-Source
RUN cd /tmp && wget --output-document=${ECCODES_VERSION}.tar.gz ${ECCODES_URL} && tar -zxvf ${ECCODES_VERSION}.tar.gz
RUN ls
RUN cd /tmp/${ECCODES_VERSION} && mkdir build && cd build && \
    cmake -DENABLE_FORTRAN=false -DPYTHON_LIBRARY_DIR=/usr/lib64/python3.6 -DPYTHON_INCLUDE_DIR=/usr/include/python3.6m -DPYTHON_EXECUTABLE=/usr/bin/python3  .. \
    && make -j2 && make install
RUN pip install pandas xarray boto3 mysql.connector cfgrib eccodes
RUN mkdir -p /tmp/
COPY main.py ./
CMD [ "main.handler" ]