FROM python:3.7-slim-buster

COPY ./docker/shared_requirements.txt /shared_requirements.txt
RUN pip install --no-cache -r /shared_requirements.txt && rm /shared_requirements.txt

RUN apt-get -y update && apt-get install -y --no-install-recommends nginx \
&& rm -rf /var/lib/apt/lists/*

COPY ./docker/nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log

COPY collabovid-shared/ /collabovid-shared
RUN (cd collabovid-shared; python setup.py sdist) && pip install --no-cache /collabovid-shared/dist/collabovid-shared-0.1.tar.gz && rm -rf /collabovid-shared
