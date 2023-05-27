print("test 1")
from flask import Flask, request
from DependencyList import oauth_client_secret, oauth_client_id, riot_api_key, connection_string
import requests
import json
from azure.data.tables import TableClient, UpdateMode

def riot_wrapper(req, region):
    url = "https://" + region + ".api.riotgames.com/" + req + "?api_key=" + riot_api_key
    print(url)
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json()
    else:
        return None

table_client = TableClient.from_connection_string(connection_string, table_name="SchoolSummoner")

app = Flask(__name__)
print("rso endpoint")

@app.route('/account/connect/riotgames/oauth-callback')
def index():
    if "code" not in request.args:
        return "no access code"
    access_code = request.args["code"]
    print(access_code)

    if "state" not in request.args:
        return "no state in riot response (should have reddit name and secret)"

    state = request.args["state"]
    redditSecret = state[:9]
    redditName = state[9:]
    print("reddit secret/name", redditSecret, redditName)

    my_filter = "RedditName eq '" + redditName + "' and RedditSecret eq '" + redditSecret + "'"
    entities = table_client.query_entities(my_filter)
    for entity in entities:
        print("table entity", entity)

        app_callback_url = "https://www.legendsofleague.gg/account/connect/riotgames/oauth-callback"
        provider = "https://auth.riotgames.com"
        token_url = provider + "/token"
        auth_=(oauth_client_id, oauth_client_secret)
        data_={
                "grant_type": "authorization_code",
                "code": access_code,
                "redirect_uri": app_callback_url
        }

        print(requests.Request("POST", token_url, auth=auth_, data=data_).prepare().body, "headers", requests.Request("POST", token_url, auth=auth_, data=data_).prepare().headers)
        response = requests.post(token_url, auth=auth_, data=data_)
        if not response.ok:
            return "post to riot not good, code " + access_code

        payload = json.loads(response.content)

        if 'access_token' not in payload:
            return "no access token in response from riot"


        access_token = payload['access_token']
        accinfo_api = "https://americas.api.riotgames.com/riot/account/v1/accounts/me"
        access_header = {'Authorization': 'Bearer ' + access_token }
        account_info = requests.get(accinfo_api, headers=access_header)
        accountInfo = json.loads(account_info.content)
        print("accountInfo", accountInfo)
        if 'puuid' not in accountInfo:
            return "no puuid in accountInfo from riot"

        puuid = accountInfo['puuid']
        summonername = accountInfo['gameName']

        #to get region
        userinfo_url = provider + "/userinfo"
        userinfo_resp = requests.get(userinfo_url,  headers=access_header)
        userInfo = json.loads(userinfo_resp.content)

        print("userinfo response", userinfo_resp)
        if "cpid" not in userInfo:
            return "didn't get region from userinfo"

        region = userInfo["cpid"]
        print("player region/name/puuid:", region, summonername, puuid)

        summonerInfo = riot_wrapper("lol/summoner/v4/summoners/by-puuid/" + puuid, region)
        if summonerInfo == None:
            return "no summonerinfo for puuid"

        print("finally, summonerinfo!!", summonerInfo)
        entity["PUUID"] = summonerInfo['puuid']
        entity["SummonerID"] = summonerInfo['id']
        entity["Region"] = region
        table_client.update_entity(entity, mode=UpdateMode.MERGE)
        return "updated entity " + redditName + "/" + redditSecret

    return "didn't find any entity matching " + redditName + "/" + redditSecret

