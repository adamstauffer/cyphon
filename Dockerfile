############################################################
# Dockerfile to run a Django-based web application
# Based on a Python 3.5 image
#
# Copyright 2017 Dunbar Security Solutions, Inc.
#
# This file is part of Cyphon Engine.
#
# Cyphon Engine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Cyphon Engine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cyphon Engine. If not, see <http://www.gnu.org/licenses/>.
#
############################################################

FROM python:3.5

MAINTAINER Leila Hadj-Chikh <leila.hadj-chikh@dunbarsecured.com>

ENV CYPHON_HOME /usr/src/app
ENV LOG_DIR     /var/log/cyphon
ENV PATH        $PATH:$CYPHON_HOME

# update the list of available packages and their versions
# and install postgis and its dependencies
RUN apt-get update && apt-get install -y \
      binutils \
      gdal-bin \
      libproj-dev \
      postgis \
      sendmail

# create unprivileged user
RUN groupadd -r cyphon && useradd -r -g cyphon cyphon

# create application subdirectories
RUN mkdir -p $CYPHON_HOME \
             $CYPHON_HOME/media \
             $CYPHON_HOME/static \
             $LOG_DIR

# copy project to the image
COPY cyphon $CYPHON_HOME/cyphon

# copy entrypoint scripts to the image
COPY entrypoints $CYPHON_HOME/entrypoints

# copy requirements.txt to the image
COPY requirements.txt $CYPHON_HOME/requirements.txt

# install python dependencies
RUN pip install -r $CYPHON_HOME/requirements.txt

COPY cyphon/cyphon/settings/base.example.py cyphon/cyphon/settings/base.py
COPY cyphon/cyphon/settings/conf.example.py cyphon/cyphon/settings/conf.py
COPY cyphon/cyphon/settings/dev.example.py cyphon/cyphon/settings/dev.py
COPY cyphon/cyphon/settings/prod.example.py cyphon/cyphon/settings/prod.py

# set owner:group and permissions
RUN chown -R cyphon:cyphon $CYPHON_HOME \
 && chmod -R 775 $CYPHON_HOME \
 && chown -R cyphon:cyphon $LOG_DIR \
 && chmod -R 775 $LOG_DIR

WORKDIR $CYPHON_HOME/cyphon

VOLUME ["$CYPHON_HOME/keys", "$CYPHON_HOME/media", "$CYPHON_HOME/static"]

EXPOSE 8000

CMD $CYPHON_HOME/entrypoints/run.sh
