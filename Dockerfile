FROM python:3.11-slim
WORKDIR /ansible
COPY requirements.txt /ansible/
RUN pip install pip --upgrade && \
  pip install -r requirements.txt
RUN apt-get update -y && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  git \
  sshpass
