import os 
import redis

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm
from redis.commands.search.field import (
    TextField,
    VectorField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

# helpers
def text_to_embedding(text):
  return model.encode(text).astype(np.float32).tobytes()

def load_dataframe(redis, df, key_prefix="tweet", id_column="id", pipe_size=100):
    records = df.to_dict(orient="records")
    pipe = redis.pipeline()
    i=1
    for record in tqdm(records):
        i=i+1
        key = f"{key_prefix}:{record[id_column]}"
        pipe.hset(key, mapping=record)
        if (i+1) % pipe_size == 0:
          res=pipe.execute()
    pipe.execute()

def create_redis_index(redis, idxname="tweet:idx"):
  try:
    redis.ft(idxname).dropindex()
  except:
    print("no index found")

  # Create an index
  indexDefinition = IndexDefinition(
      prefix=["tweet:"],
      index_type=IndexType.HASH,
  )

  redis.ft(idxname).create_index(
      (
          TextField("full_text", no_stem=False, sortable=False),
          VectorField("text_embedding", "HNSW", {  "TYPE": "FLOAT32", 
                                                    "DIM": 384, 
                                                    "DISTANCE_METRIC": "COSINE",
                                                  })
      ),
      definition=indexDefinition
  )



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


tqdm.pandas()

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')



# READ DATA 
df = pd.read_csv('Labelled_Tweets.csv').drop(columns=['created_at','score'])
#df=df.head(3000) #trim dataframe to fit results into 30MB Redis database

#generate vector embeddings
df["text_embedding"] = df["full_text"].progress_apply(text_to_embedding)
# df.head()

redis.flushdb()

# create Index
create_redis_index(redis)

# load data from Dataframe to Redis HASH
load_dataframe(redis,df,key_prefix="tweet", pipe_size=100)
