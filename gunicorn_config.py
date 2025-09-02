"""
Gunicorn configuration for Render deployment
"""
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 1  # Keep it at 1 for free tier to avoid memory issues
worker_class = 'sync'
worker_connections = 100
timeout = 120
keepalive = 2

# Restart workers after this many requests to prevent memory leaks
max_requests = 100
max_requests_jitter = 20

# Preload the application before forking worker processes
preload_app = True

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'w-manual-bot'

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# SSL
keyfile = None
certfile = None

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def on_exit(server):
    server.log.info("Server is shutting down")