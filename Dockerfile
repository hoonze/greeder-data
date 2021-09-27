FROM python:3.6.8

COPY . .

RUN pip install --upgrade pip

RUN pip install wheel

RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata g++ git curl

# installing java jdk and java jre
RUN apt-get install -y default-jdk default-jre

# installing python3 and pip3
RUN apt-get install -y python3-pip python3-dev

RUN pip install jpype1-py3 konlpy

RUN pip install -r requirements.txt

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

EXPOSE 8000