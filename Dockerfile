FROM python:3.11.3
ENV PYTHONDONTWRITEBITECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get upgrade -y
RUN apt-get install certbot -y
RUN apt-get install python3-certbot-nginx -y
WORKDIR /django
COPY . .
RUN chmod +x ./start
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
CMD ["certbot", "--nginx", "-d", "aufrutten.com", "-d", "www.aufrutten.com"]
