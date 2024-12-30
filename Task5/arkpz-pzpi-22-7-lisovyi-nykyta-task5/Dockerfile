FROM python:3.10
LABEL authors="Nikita Lisovyi"

WORKDIR /app

# Установка необходимых зависимостей с правами root
RUN apt-get update && apt-get install -y \
    sudo \
    unixodbc-dev \
    curl \
    gnupg2 \
    lsb-release \
    apt-transport-https \
    && apt-get clean

# Добавляем ключи репозиториев
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Добавляем репозиторий для SQL Server
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-server.list

# Удаляем возможный дублирующийся файл
RUN rm -f /etc/apt/sources.list.d/mssql-tools.list

# Удаляем старые версии конфликтующих библиотек
RUN apt-get remove -y libodbc2 libodbcinst2 unixodbc-common

# Выполняем установку с правами root
USER root

# Устанавливаем переменные для принятия лицензионного соглашения
ENV ACCEPT_EULA=Y

# Обновление списка пакетов и установка ODBC драйвера и инструментов SQL Server
RUN apt-get update && apt-get install -y msodbcsql17 mssql-tools

# Создание пользователя mssql (если не существует)
RUN useradd -ms /bin/bash mssql

# Устанавливаем зависимости с помощью pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Возвращаемся к пользователю mssql
USER mssql

COPY . .

ENV FLASK_APP=run.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"]
