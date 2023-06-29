FROM python:3.9.16-slim
WORKDIR /hub
# binary deps
RUN apt-get update; \
	apt-get install -y --no-install-recommends libpulse0
  
# deps
COPY requirements.txt /hub
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# runtime
COPY . /hub
EXPOSE 5000
CMD python main.py