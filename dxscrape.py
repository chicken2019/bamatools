import json
import requests
import time 

import web3

import dxsale

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

class DxPresaleScraper(object):
    CONTRACT_DEPLOYER = web3.Web3.toChecksumAddress('0xbacebad5993a19c7188db1cc8d0f748c9af1689a')

    def __init__(self, w3=None, block=0):
        self._w3 = w3
        self._last_tx = ''
        self._explorer = BlockExplorer()
        self._last_block = block


    def get_presale_deploy_transactions(self):
        # fetch the deployer transactions
        result = self._explorer.get_account_transactions(self.CONTRACT_DEPLOYER, self._last_block)
        print('(debug) result count: ', len(result))
        
        # set the latest block 
        self._last_block = int(result[-1]['blockNumber'])
        print('(debug) last block : ', self._last_block)

        # only take in transactions with 2 receipt 
        filtered_result = list(filter(lambda x: x['input'].startswith('0x0eed262f'), result))
        print('(debug) filtered result count: ', len(filtered_result))

        # more confirmartion using receipt 
        for tx in filtered_result:
            address = self.get_presale_address_from_transaction(tx['hash'])
            if address:
                presale = dxsale.DxPresale(address, self._w3)
                presale.display()


    def get_presale_address_from_transaction(self, tx):
        receipt = self._w3.eth.get_transaction_receipt(tx)
        log_count = len(receipt.logs)
        if log_count == 2:
            return receipt.logs[1].address
        print(receipt)
        # input('ERR: Please look into this unknown !')
