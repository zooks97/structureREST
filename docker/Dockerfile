# specific version for reproducibilty

FROM phusion/passenger-customizable:0.9.19

LABEL maintainer Austin Zadoks <austin.zadoks@epfl.ch>

ENV HOME /root

############
### init ###
############
CMD ["/sbin/my_init"]

########################
### passeneger setup ###
########################
# buildessentials and git
RUN /pd_build/utilities.sh \
    # python 2.7 and 3.5.x
    && /pd_build/python.sh
# # enable Nginx in passenger
# && rm -f /etc/service/ngnix/down

########################
### Root environment ###
########################
RUN cp /etc/skel/.bash* /etc/skel/.profile /root/
RUN echo "PS1='docker:\W$ '" >> /root/.bashrc

################
### programs ###
################
RUN apt-get update && \
    apt-get -y install \
    python-pip \
    gfortran \
    liblapack-dev \
    libblas-dev \
    libnetcdf-dev \
    netcdf-bin \
    curl \
    apache2 \
    libapache2-mod-xsendfile \
    libapache2-mod-wsgi \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean all

##############
### python ###
##############
RUN pip install --upgrade pip
RUN pip install --no-cache-dir \
    ipython \
    numpy \
    scipy \
    pandas \
    pymatgen \
    ase \
    spglib \
    flask_restful \
    tqdm \
    psutil

#####################
### QUIP + quippy ###
#####################
ENV QUIP_ROOT /opt/QUIP_ROOT
# get QUIP
RUN git clone --recursive https://github.com/libAtoms/QUIP.git ${QUIP_ROOT}
WORKDIR ${QUIP_ROOT}
# for reproducibility 05-07-2018
RUN git checkout 531330f
# add GAP files
ADD ./GAP.tar.gz ./src/
# RUN rm -rf GAP-filler/
# do install GAP (necessary for descriptors in quippy)
ENV BUILD GAP
ADD . ${QUIP_ROOT}
# QUIP for general use is the OpenMP version.
# Installs with no suffix, e.g. quip
# Also installs quippy
ENV QUIP_ARCH linux_x86_64_gfortran_openmp
RUN cd ${QUIP_ROOT} \
    && mkdir -p build/${QUIP_ARCH} \
    && cp docker/arch/${BUILD}_Makefile.${QUIP_ARCH}.inc build/${QUIP_ARCH}/Makefile.inc \
    && make > /dev/null \
    && QUIP_INSTALLDIR=${QUIP_ROOT}/bin make install \
    && make install-quippy > /dev/null \
    && find build/${QUIP_ARCH} -type f ! \( -name '*.a' -o -name 'Makefile.inc' \) -delete

################
### app user ###
################
USER app
WORKDIR /home/app
ENV HOME /home/app

#######################
### SOAP REST Setup ###
#######################
RUN echo "b"
RUN git clone https://github.com/cosmo-epfl/glosim2
RUN git clone https://github.com/zooks97/aiida-fingerprint
RUN mkdir webservice
RUN cp aiida-fingerprint/aiida_fingerprint/soaprest.py webservice/soaprest.py
RUN cp aiida-fingerprint/aiida_fingerprint/atoms_utils.py webservice/atoms_utils.py

# #############
# ### Nginx ###
# #############
# RUN mkdir webservice/public
# ENV SP_WSGI_FILE=webservice/soaprest_nginx.py
# RUN echo "import sys" > $SP_WSGI_FILE \
#     && echo "sys.path.insert(0, '/home/app/webservice')" >> $SP_WSGI_FILE \ 
#     && echo "from soaprest import app as application" >> $SP_WSGI_FILE 

##############
### Apache ###
##############
ENV SP_WSGI_FILE=webservice/soaprest_app.wsgi
RUN echo "import sys" > $SP_WSGI_FILE && \
    echo "sys.path.insert(0, '/home/app/webservice')" >> $SP_WSGI_FILE && \
    echo "from soaprest import app as application" >> $SP_WSGI_FILE 

#################
### root user ###
#################
USER root
WORKDIR /home/app

##############
### Apache ###
##############
RUN cp aiida-fingerprint/docker/conf/soaprest-apache.conf /etc/apache2/sites-available/soaprest.conf
RUN a2enmod wsgi && a2enmod xsendfile && \
    a2dissite 000-default && a2ensite soaprest
# RUN mkdir /etc/service/apache
# RUN cp /home/app/aiida-fingerprint/docker/conf/apache_run.sh /etc/service/apache/run
# RUN chmod +x /etc/service/apache/run
# RUN echo "ServerName localhost:80" >> /etc/apache2/apache2.conf

# #############
# ### Nginx ###
# #############
# RUN rm /etc/nginx/sites-enabled/default
# ADD conf/soaprest-nginx.conf /etc/nginx/sites-enabled/soaprest.conf

############
### init ###
############
RUN mkdir -p /etc/my_init.d

###############
### startup ###
###############
# webserver
EXPOSE 80

###############
### Cleanup ###
###############
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
