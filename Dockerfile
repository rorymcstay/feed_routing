FROM python:3.6-alpine

RUN mkdir -p /home

WORKDIR /home

ADD requirements.txt ./requirements.txt
RUN python -m pip install pip
RUN python -m pip install --upgrade pip
# Installing packages
RUN pip install -r ./requirements.txt

# Copying over necessary files
COPY settings.py ./settings.py
COPY routing.py ./app.py
COPY src ./src

# Entrypoint
CMD ["python", "./app.py" ]
