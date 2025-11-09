FROM python:3.13-slim-bookworm

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y unzip curl
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/bin

COPY . /usr/src/app

RUN pip install django psycopg[binary] hypercorn djrealtime

EXPOSE 8085

CMD ["task", "container_init"]
