FROM python:3.6

ENV PYTHONUNBUFFERED 1

# Install packages
RUN apt-get -y update
RUN apt-get -y install libgdal-dev gdal-bin cron

# Install certbot
RUN echo 'deb http://ftp.debian.org/debian jessie-backports main' | tee /etc/apt/sources.list.d/backports.list
RUN apt-get -y update
RUN apt-get -y install certbot -t jessie-backports

# Setup certbot cron
ADD infra/app/certbot_renew.sh /etc/cron.weekly/

# Create app root
RUN mkdir -p /code
WORKDIR /code

# Install Python dependencies
ADD requirements.txt /code
RUN pip install --no-cache-dir -r requirements.txt

# Install GDAL 1.10, to be compatible with the C++ library installed via apt-get
ENV CPLUS_INCLUDE_PATH /usr/include/gdal
ENV C_INCLUDE_PATH /usr/include/gdal
RUN pip install GDAL==1.10