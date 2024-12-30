FROM python:3.11.11-bullseye

# Working dir is app
WORKDIR /app

COPY . .

RUN pip install --upgrade pip

RUN SYSTEM_VERSION_COMPAT=0 pip install --no-cache-dir onnxruntime pysqlite3-binary

# Dependencies installation
RUN pip install -r deployment.txt --no-cache-dir

# Remove no use packages 
RUN pip uninstall -y nvidia-cuda-nvrtc-cu12 nvidia-cuda-runtime-cu12 nvidia-cuda-cupti-cu12 \
    nvidia-cudnn-cu12 nvidia-cublas-cu12 nvidia-cufft-cu12 nvidia-curand-cu12 nvidia-cusolver-cu12 \
    nvidia-cusparse-cu12 nvidia-nccl-cu12 nvidia-nvtx-cu12 nvidia-nvjitlink-cu12 triton

RUN pip uninstall -y nvidia_cublas_cu12 nvidia_cuda_cupti_cu12 nvidia_cuda_nvrtc_cu12 \
    nvidia_cuda_runtime_cu12 nvidia_cudnn_cu12 nvidia_cufft_cu12nvidia_curand_cu12 \
    nvidia_cusolver_cu12 nvidia_cusparse_cu12 nvidia_nccl_cu12 \
    nvidia_nvtx_cu12 nvidia_nvjitlink_cu12

# 5555 port expose
EXPOSE 5555

# Entrypoint command
ENTRYPOINT ["python", "main.py", "--host=0.0.0.0", "--port=5555", "--reload=0", "--workers=1", \
    "--backlog=5000", "--log_level=debug", "--use_colors=1", "--limit_concurrency=10000", \
    "--limit_max_requests=10000", "--web_socket_time=0.01", "--model_temp=0.1", "--prod=True", \
    "--ssl_keyfile=/etc/nginx/ssl/private.pem", "--ssl_certfile=/etc/nginx/ssl/cert.pem"]