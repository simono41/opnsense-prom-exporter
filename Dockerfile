FROM python:latest

#WORKDIR /usr/app/src

# Install package
WORKDIR /code
COPY . .

#COPY prometheus-ssh-exporter.py ./
#COPY requirements.txt ./

RUN pip3 install -r requirements.txt

RUN python -u setup.py install

# Set this to the port you want to expose
EXPOSE 8000

# Set the -p option to the port you exposed above, defaults to 8000
#CMD ["python", "-u", "opnsense-exporter"]
#CMD ["sleep", "60"]
CMD ["opnsense-exporter"]
