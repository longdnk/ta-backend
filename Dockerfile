FROM python:3.11.11-alpine

# Đặt thư mục làm việc là /app
WORKDIR /app

# Copy toàn bộ nội dung từ thư mục cha vào /app trong container
COPY . .

# Cài đặt các dependencies
RUN pip install -r requirements.txt

# Mở port 5555
EXPOSE 5555

# Đặt entrypoint
ENTRYPOINT ["python", "main.py", "--host=0.0.0.0", "--port=5555", "--reload=0", "--workers=4", \
    "--backlog=5000", "--log_level=debug", "--use_colors=1", "--limit_concurrency=10000", \
    "--limit_max_requests=10000", "--web_socket_time=0.01", "--model_temp=0.1"]