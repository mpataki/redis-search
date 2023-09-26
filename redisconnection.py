import os
import redis

# CONNECT TO REDIS
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

#shortcut for redis-cli $REDIS_CONN command
if REDIS_PASSWORD!="":
  os.environ["REDIS_CONN"]=f"-h {REDIS_HOST} -p {REDIS_PORT} -a {REDIS_PASSWORD} --no-auth-warning"
else:
  os.environ["REDIS_CONN"]=f"-h {REDIS_HOST} -p {REDIS_PORT}"
redis = redis.Redis(
  host=REDIS_HOST,
  port=REDIS_PORT,
  password=REDIS_PASSWORD)
redis.ping()
