FROM python:3.11.3
ENV PYTHONDONTWRITEBITECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get upgrade -y
WORKDIR /django
COPY . .
RUN chmod +x ./start
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
CMD ["./start"]
