FROM python:3.11-alpine

WORKDIR /app

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt --no-cache-dir

EXPOSE 5555

ENTRYPOINT ["python", "main.py", "--host=0.0.0.0", "--port=5555", "--reload=0", "--workers=1", \
    "--backlog=5000", "--log_level=debug", "--use_colors=1", "--limit_concurrency=10000", \
    "--limit_max_requests=10000", "--web_socket_time=0.01", "--model_temp=0.01", "--prod=True", \
    "--ssl_keyfile=/etc/nginx/ssl/private.pem", "--ssl_certfile=/etc/nginx/ssl/cert.pem"]