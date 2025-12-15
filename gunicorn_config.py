workers = 4
bind = "127.0.0.1:8000"
accesslog = "/var/log/dle_app/access.log"
errorlog = "/var/log/dle_app/error.log"
loglevel = "info"
worker_class = "sync"
timeout = 120
