import time
import requests
import json

INTERESTED_COINS = ["MILK", "MIN", "LQ"]
INTERESTED_PAIRS = ["MILK/ADA", "MIN/ADA", "LQ/ADA"]
def get_price_mswap():
    url = "https://monorepo-mainnet-prod.minswap.org/graphql"

    payload = json.dumps({
      "query": "\n    query TopPools($assetName: String, $offset: Int, $limit: Int) {\n  topPools(assetName: $assetName, offset: $offset, limit: $limit) {\n    assetA {\n      currencySymbol\n      tokenName\n      ...allMetadata\n    }\n    assetB {\n      currencySymbol\n      tokenName\n      ...allMetadata\n    }\n    reserveA\n    reserveB\n    lpAsset {\n      currencySymbol\n      tokenName\n    }\n    totalLiquidity\n    reserveADA\n    volumeADAByDay\n    volumeADAByWeek\n    pendingOrders\n    tradingFeeARP\n  }\n}\n    \n    fragment allMetadata on Asset {\n  metadata {\n    name\n    ticker\n    url\n    decimals\n  }\n}\n    ",
      "variables": {
        "assetName": None,
        "offset": 0,
        "limit": 20
      }
    })
    headers = {
      'authority': 'monorepo-mainnet-prod.minswap.org',
      'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
      'sec-ch-ua-mobile': '?0',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
      'sec-ch-ua-platform': '"Windows"',
      'content-type': 'application/json',
      'accept': '/',
      'origin': 'https://app.minswap.org/',
      'sec-fetch-site': 'same-site',
      'sec-fetch-mode': 'cors',
      'sec-fetch-dest': 'empty',
      'referer': 'https://app.minswap.org/',
      'accept-language': 'en-US,en;q=0.9'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = {}
    for entry in response.json()["data"]["topPools"]:
        token = entry["assetB"]["metadata"]
        if (not token):
            continue
        pair = token["ticker"]
        if (token["decimals"] != 0):
            price = entry["reserveA"]/entry["reserveB"]
        else:
            price = (entry["reserveA"] / 1000000) / entry["reserveB"]
        price = round(price, 3)
        if (pair in INTERESTED_COINS):
            data[pair + "/ADA"] = price
        
    
    return (data)

def get_price_sswap():
    data = {}
    with open("endpoints.json", "r") as f:
        endpoints = json.loads(f.read())
        f.close()
    for pair in endpoints:
        if (pair not in INTERESTED_PAIRS):
            continue
        url = endpoints[pair]
        r = requests.get(url)
        r_dic = json.loads(r.content)
        price = r_dic["rollup"]["open"]
        if (price > 10000):
            price = price / 1000000
        data[pair] = round(price, 3)
    return (data)

def init():
    while True:
        lst = []
        s_prices = get_price_sswap()
        m_prices = get_price_mswap()
        for pair, m_price in m_prices.items():
            s_price = s_prices[pair]
            difference = round(abs(100 / m_price * s_price - 100), 2)
            lst.append({"pair":pair, "mPrice":m_price, "sPrice":s_price, "difference": difference})
        jsn = json.dumps(lst)
        with open("../prices.json", "w") as f:
            f.write(jsn)
            f.close()
        time.sleep(20)
