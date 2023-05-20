import praw
from azure.data.tables import TableClient



reddit = praw.Reddit(
    client_id="Zh6i1cNyql4l0EsG9_vLfw",
    client_secret="IEHHOuWv9MR7A9qv8NOwyPClhha8Mw",
    user_agent="RedditFlairGuy",
    password="WorseWorld100",
    username="tankmanlol",
)
#print("me", reddit.user.me())
subreddit = reddit.subreddit('TestFlairAPI')

connection_string = "DefaultEndpointsProtocol=https;AccountName=flair20;AccountKey=xZcfxarFvfFV9JvZmFB6gx7r6W4pSo0CFtLluhuvZLcNhI4IbEJb3uFConvLirKCjfvKjS6N6JSy+AStgn0P0w==;EndpointSuffix=core.windows.net"
table_client = TableClient.from_connection_string(connection_string, table_name="SchoolSummoner")

entity = table_client.get_entity(partition_key="pkey", row_key="rkey")
entities = table_client.query_entities(query_filter="")

# Iterate over the retrieved entities
for entity in entities:
    league = entity.get("League")
    tier = entity.get("Tier")
    redditname = entity.get("RedditName")
    print(league, tier)
    subreddit.flair.set(redditname, text=league + " " + tier)