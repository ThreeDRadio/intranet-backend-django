# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7
ARG DJANGO_ENV=staging
ARG PYTHON_VERSION=3.9.25
FROM python:${PYTHON_VERSION}-slim AS base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install requirements for building psycopg2
RUN apt-get update \
 && apt-get -y install libpq-dev \
 && apt-get -y install gcc \
 && apt-get -y install apache2 \
 && apt-get -y install apache2-dev \
 && apt-get -y install w3m

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN mkdir /home/appuser

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python3 -m pip install -r requirements.txt

# Do mod_wsgi setup
ARG MOD_WSGI_VERSION=4.8.0
ADD https://github.com/GrahamDumpleton/mod_wsgi/archive/refs/tags/${MOD_WSGI_VERSION}.tar.gz /tmp/${MOD_WSGI_VERSION}.tar.gz
RUN tar xvfz /tmp/${MOD_WSGI_VERSION}.tar.gz -C /tmp
WORKDIR /tmp/mod_wsgi-${MOD_WSGI_VERSION}
RUN ./configure --with-python=/usr/local/bin/python3
RUN make install
RUN mkdir /etc/apache2/modules
RUN cp /usr/lib/apache2/modules/mod_wsgi.so /etc/apache2/modules/mod_wsgi.so
WORKDIR /app

# Add the logging dir
RUN mkdir -p /var/log/apache2 && \
    mkdir -p /var/lib/apache2 && \
    mkdir -p /var/run/apache2 && \
    mkdir -p /var/lock/apache2 && \
    chown -R appuser:appuser /var/log/apache2 && \
    chown -R appuser:appuser /var/lib/apache2 && \
    chown -R appuser:appuser /var/run/apache2 && \
    chown -R appuser:appuser /var/lock/apache2 && \
    chmod -R 777 /etc/apache2 && \
    chmod -R 777 /app && \
    chmod -R 777 /home/appuser && \
    chmod 1777 /var/run/apache2

# Add server config
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN echo "WSGIPythonPath /usr/local/bin/python3" >> /etc/apache2/apache2.conf
RUN echo "LoadModule wsgi_module modules/mod_wsgi.so" >> /etc/apache2/apache2.conf
RUN echo "LogLevel debug" >> /etc/apache2/apache2.conf

# copy the backend configuration to the container's sites list.
COPY ./intranet-backend.conf /etc/apache2/sites-available/intranet-backend.conf

FROM base AS django-staging
COPY /html/admin/base_site.staging.html /app/templates/admin/base_site.html
COPY /html/admin/custom_admin.staging.css /app/static/admin/css/custom_admin.css

FROM base AS django-production
# Switch to the non-privileged user to run the application.
# IF YOU RUN INTO PERMISSIONS ISSUES
# See UID above, it's 10001
# DO chown 10001 <path-to-cert> 
# DO chown 10001 <path-to-key>

# Copy the source code into the container.
FROM django-${DJANGO_ENV} AS final
COPY --exclude=/html . .
RUN python3 /app/manage.py collectstatic --noinput
# Enable mods as root
RUN a2enmod status && a2enmod lbmethod_byrequests && a2enmod ssl && a2enmod rewrite
RUN a2dissite 000-default.conf 
RUN a2ensite intranet-backend.conf
#USER appuser

# Expose the port that the application listens on.
EXPOSE 8001

# Run the Apache2 instance.
CMD ["/usr/sbin/apache2ctl", "-DFOREGROUND"]