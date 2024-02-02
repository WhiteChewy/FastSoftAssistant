FROM python:3.11.70slim-bullseye
RUN mkdir -p /fs_assistant
WORKDIR /fs_assistant
ENV PYTHONPATH "${PYTHONPATH}:/"
EXPOSE 8080

RUN apt-get update && \
    apt-get install -y locales --no-install-recommends tzdata && \
    apt-get install -y python3-dev libldap2-dev libsasl2-dev libssl-dev && \
    echo ru_RU.UTF-8 UTF-8 >> /etc/locale.gen && \
    locale-gen
ENV TZ Europe/Moscow
RUN  apt-get update \
  && apt-get install -y wget curl \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /fs_assistant/
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /fs_assistant/

RUN chmod +x main.py

CMD ["python3.11", "main.py"]
