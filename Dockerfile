FROM python:3.11.11-bullseye

# Working dir is app
WORKDIR /app

COPY . .

RUN pip install --upgrade pip

RUN SYSTEM_VERSION_COMPAT=0 pip install --no-cache-dir onnxruntime pysqlite3-binary

# Dependencies installation
RUN pip install -r deployment.txt --no-cache-dir

# 5555 port expose
EXPOSE 5555

# Entrypoint command
ENTRYPOINT ["python", "main.py", "--host=0.0.0.0", "--port=5555", "--reload=0", "--workers=1", \
    "--backlog=5000", "--log_level=debug", "--use_colors=1", "--limit_concurrency=10000", \
    "--limit_max_requests=10000", "--web_socket_time=0.01", "--model_temp=0.1", "--prod=True", \
    "--ssl_keyfile=/etc/nginx/ssl/private.pem", "--ssl_certfile=/etc/nginx/ssl/cert.pem"]