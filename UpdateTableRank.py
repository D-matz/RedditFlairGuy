from azure.data.tables import TableClient, UpdateMode
import requests

riot_api_key = "RGAPI-40d9ab03-b4ff-4656-be46-775d45b2eaed"

def riot_wrapper(req):
    url = req + "?api_key=" + riot_api_key
    print(url)
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    else:
        return None

connection_string = "DefaultEndpointsProtocol=https;AccountName=flair20;AccountKey=xZcfxarFvfFV9JvZmFB6gx7r6W4pSo0CFtLluhuvZLcNhI4IbEJb3uFConvLirKCjfvKjS6N6JSy+AStgn0P0w==;EndpointSuffix=core.windows.net"
table_client = TableClient.from_connection_string(connection_string, table_name="SchoolSummoner")

entity = table_client.get_entity(partition_key="pkey", row_key="rkey")
entities = table_client.query_entities(query_filter="")

for entity in entities:
    summonerid = entity.get("SummonerID")
    print(summonerid)
    league_info = riot_wrapper("https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/" + summonerid)
    for queue_info in league_info:
        if queue_info['queueType'] == "RANKED_SOLO_5x5":
            rank = queue_info['rank']
            tier = queue_info['tier']
            entity["Rank"] = rank
            entity["Tier"] = tier
            table_client.update_entity(entity, mode=UpdateMode.MERGE)
