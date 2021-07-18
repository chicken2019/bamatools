import json
import requests
import time 
  
class BlockExplorer(object):
    API_KEY = 'IPE8TYXKRW4JVE72IND9WDSJQ8NQGRM783'
    def __init__(self):
        super().__init__()

    def get_contract_abi(self, ca: str) -> str:
        url = f'https://api.bscscan.com/api?module=contract&action=getabi&address={ca}&apikey={self.API_KEY}'
        r = requests.get(url, timeout=60)
        if r.status_code == requests.codes.ok:
            result = json.loads(r.text).get('result')
            if not 'source code not verified' in result:
                return result

    def get_account_transactions(self, address, fromblock=0):
        _U = f'http://api.bscscan.com/api?module=account&action=txlist&address={address}&startblock={fromblock}&endblock=99999999&sort=asc&apikey={self.API_KEY}'
        while True:
            try:
                r = requests.get(_U, timeout=60)
                if r.status_code == requests.codes.ok:
                    result = json.loads(r.text).get('result')
                    # set the last block 
                    return result
            except Exception as ex:
                print(f'Exception): {ex}')
                time.sleep(10)
