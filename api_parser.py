import json

import requests

# from pprint import pprint

mph_url = "https://miningpoolhub.com/index.php?page=api&action="
profit_str = "getminingandprofitsstatistics"
switch_str = "getautoswitchingandprofitsstatistics"


class ApiParser:
    def __init__(self, url, name="ApiParser"):
        print("{msg} initialized".format(msg=name))
        self.url = url
        print("URL:", self.url)

    def get_response(self):
        return requests.get(self.url)

    def get_json(self):
        r = self.get_response()
        coins = json.loads(r.text)['return']
        for coin in coins:
            coin["coin_name"], coin["algo"] = coin["coin_name"].lower(), coin["algo"].lower()
            if coin["algo"] == "lyra2re2":
                coin["algo"] = "lyra2v2"
            if coin["algo"] == "myriad-groestl":
                coin["algo"] = "myr-gr"
        return coins

    def load_json_offline(self):
        try:
            j = self.get_json()
            with open("api_offline.txt", "w") as outfile:
                json.dump(j, outfile)
            return True
        except requests.ConnectionError:
            return False

    @staticmethod
    def get_json_offline():
        with open("api_offline.txt") as infile:
            return json.load(infile)


class MPHProfitApi(ApiParser):
    def __init__(self):
        self.url = mph_url + profit_str
        super().__init__(self.url, "MiningPoolHubProfitApi")


class MPHSwitchApi(ApiParser):
    def __init__(self):
        self.url = mph_url + switch_str
        super().__init__(self.url, "MiningPoolHubSwitchApi")


if __name__ == "__main__":
    m_api = ApiParser(mph_url + profit_str)
    a_api = ApiParser(mph_url + switch_str)

    # coins = m_api.get_json()
    # algorithms = a_api.get_json()
    #
    # # for coin in coins:
    # #     print(coin['coin_name'])
    #
    # for algo in algorithms:
    #     print(algo['algo'].lower())
