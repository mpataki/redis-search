import pandas as pd
from redis.commands.search.query import Query
from redisconnection import redis

user_query = "animal"

#using Full Text Index
q = Query(user_query)\
  .return_fields("full_text")

res = redis.ft("tweet:idx").search(q)

if res.total==0:
  print("No matches found")
else:
  res_df = pd.DataFrame([t.__dict__ for t in res.docs ]).drop(columns=["payload"])
  pd.set_option('display.max_colwidth', None)
  print(res_df)

