import json
import requests


class BlockExplorer(object):
    API_KEY = 'IPE8TYXKRW4JVE72IND9WDSJQ8NQGRM783'

    def __init__(self) -> None:
        super().__init__()

    # Todo: this doesn't look right
    def get_abi(self, ca: str) -> str:
        url = f'https://api.bscscan.com/api?module=contract&action=getabi&address={ca}&apikey={self.API_KEY}'
        r = requests.get(url, timeout=60)
        if r.status_code == requests.codes.ok:
            result = json.loads(r.text).get('result')
            if not 'source code not verified' in result:
                return result
