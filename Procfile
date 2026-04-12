web: gunicorn src.main:app --bind 0.0.0.0:${PORT:-10100} --workers 2 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --graceful-timeout 30 --access-logfile - --error-logfile -
