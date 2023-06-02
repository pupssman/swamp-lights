FROM python:3.9.16-alpine

WORKDIR /test
# deps
COPY requirements.txt /test
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# runtime
COPY . /test
CMD py.test