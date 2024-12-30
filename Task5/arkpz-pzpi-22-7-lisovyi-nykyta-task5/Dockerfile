FROM python:3.10
LABEL authors="Nikita Lisovyi"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    sudo \
    unixodbc-dev \
    curl \
    gnupg2 \
    lsb-release \
    apt-transport-https \
    && apt-get clean

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-server.list

RUN rm -f /etc/apt/sources.list.d/mssql-tools.list

RUN apt-get remove -y libodbc2 libodbcinst2 unixodbc-common

USER root

ENV ACCEPT_EULA=Y

RUN apt-get update && apt-get install -y msodbcsql17 mssql-tools

RUN useradd -ms /bin/bash mssql

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

USER mssql

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"]
