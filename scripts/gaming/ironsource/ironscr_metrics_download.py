import requests
import json
from datetime import datetime, timedelta

def get_bearer_token(secretkey, refreshtoken):
    """https://developers.ironsrc.com/ironsource-mobile/air/authentication/#step-1"""
    url = 'https://platform.ironsrc.com/partners/publisher/auth'
    headers = {'secretkey': secretkey,
           'refreshToken': refreshtoken}

    response = requests.get(url, headers=headers)
    #print(response.text)
    return response.text

def get_ironsrc_appkeys(token_):
    """https://developers.ironsrc.com/ironsource-mobile/air/application-api/#step-1"""
    #not needed if you already have your appkeys
    #print(token_)
    headers = {'Authorization': 'Bearer ' + token_.replace('"', '')}

    url_request = "https://platform.ironsrc.com/partners/publisher/applications/v5?"

    resp = requests.get(url_request, headers=headers)
    #print(resp.text)
    data = json.loads(resp.text)
    appkeys = [row.get('appKey') for row in data]

    return appkeys


def get_ironsrc_metrics(token_):
    url_request = "https://api.ironsrc.com/advertisers/v2/reports?breakdowns=day,campaign,country,deviceType&metrics=impressions,clicks,completions,spend&format=json&count=100&startDate=2020-10-25&endDate=2020-10-30"
    headers = {'Authorization': 'Bearer ' + token_.replace('"', '')}

    print(url_request)
    resp = requests.get(url_request, headers=headers)
    data = json.loads(resp.text)
    #print(resp, resp.text)
    #print(urls)
    return data


def get_ironsrc_data_url(token_, appkey, date = None):
    """https://developers.ironsrc.com/ironsource-mobile/air/user-ad-revenue-v2/#step-1"""

    headers = {'Authorization': 'Bearer ' + token_.replace('"', '')}

    url_request = f"https://platform.ironsrc.com/partners/userAdRevenue/v3?appKey={appkey}&date={date}&reportType=1"
    #url_request = f'http://platform.ironsrc.com/partners/adRevenueMeasurements/v1?appKey={appkey}&date={date}'
    print(url_request)
    resp = requests.get(url_request, headers=headers)
    urls = json.loads(resp.text).get('urls')
    #print(resp, resp.text)
    #print(urls)
    return urls


def download_ironsrc_data(secretkey, refreshtoken, appkey, date = None):
    """ returns file name so you can pass this to your loading function"""
    token = get_bearer_token(secretkey, refreshtoken)

    if date is None:
        from datetime import datetime
        yesterday = datetime.now()  - timedelta(days=1)
        date = yesterday.strftime('%Y-%m-%d')

    urls = get_ironsrc_data_url(token, appkey, date= date)
    filenames = []
    if urls is not None:
        for idx in range(0, len(urls)):
            url = urls[idx]
            filename = f'ironsource_revenue_{date}_{appkey}_part{idx}.gz'
            filedata = requests.get(url)
            with open(filename, 'wb') as f:
                f.write(filedata.content)
                filenames.append(filename)
    return filenames

def download_ironscr_data_all_games(secretkey, refreshtoken):
    token = get_bearer_token(secretkey, refreshtoken)
    # get game ids
    appkeys = get_ironsrc_appkeys(token)
    # for each game download files
    files = []
    for appkey in appkeys:
        fns = download_ironsrc_data(secretkey, refreshtoken, appkey)
        files += fns

    return files


if __name__ == "__main__":
    import os
    secretkey = os.environ.get('sc1')
    refreshtoken = os.environ.get('sc2')
    #get auth token
    token = get_bearer_token(secretkey, refreshtoken)
    #get game ids

    metrics = get_ironsrc_metrics(token+'fsa')
    print(metrics)
    #do loading logic
    #print(filename)
