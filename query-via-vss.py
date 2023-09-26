import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
from redis.commands.search.query import Query
from redisconnection import redis

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def text_to_embedding(text):
  return model.encode(text).astype(np.float32).tobytes()

user_query = "animal"

#using Vector Similarity Index
query_vector = text_to_embedding(user_query)
q = Query("*=>[KNN 10 @text_embedding $vector AS result_score]")\
                .return_fields("result_score","full_text")\
                .dialect(2)\
                .sort_by("result_score", True)
res = redis.ft("tweet:idx").search(q, query_params={"vector": query_vector})
#print(res)
res_df = pd.DataFrame([t.__dict__ for t in res.docs ]).drop(columns=["payload"])
pd.set_option('display.max_colwidth', None)
print(res_df)
