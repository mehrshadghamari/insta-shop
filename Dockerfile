FROM python:3.10-alpine

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /app

WORKDIR /app

COPY ./entrypoint.sh /

RUN chmod +x /entrypoint.sh

# ENTRYPOINT [ "sh","/entrypoint.sh" ]
