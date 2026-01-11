import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
bind = "0.0.0.0:8000"
timeout = 120
graceful_timeout = 20
keepalive = 5
loglevel = "info"
accesslog = "-"
errorlog = "-"
worker_class = "uvicorn.workers.UvicornWorker"
