# Dockerfile
FROM ubuntu:latest
RUN apt update && apt install -y python3 python3-pip iputils-ping net-tools curl
WORKDIR /app
COPY . /app
CMD ["bash"]