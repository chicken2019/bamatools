import os,sys
import datetime
import time
import json
import web3
import requests
import bama3
from contract import Contract
from token3 import Token 
import dxsnipeabi

# http://api.bscscan.com/api?module=account&action=txlist&address=0xbacebad5993a19c7188db1cc8d0f748c9af1689a&startblock=0&endblock=99999999&sort=asc&apikey=IPE8TYXKRW4JVE72IND9WDSJQ8NQGRM783

class BlockExplorer(object):
    API_KEY = 'IPE8TYXKRW4JVE72IND9WDSJQ8NQGRM783'
    def __init__(self):
        super().__init__()

    def get_account_transactions(self, address, fromblock=0):
        address = web3.Web3.toChecksumAddress('0xbacebad5993a19c7188db1cc8d0f748c9af1689a')
        _U = f'http://api.bscscan.com/api?module=account&action=txlist&address={address}&startblock={fromblock}&endblock=99999999&sort=asc&apikey={self.API_KEY}'
        r = requests.get(_U, timeout=60)
        if r.status_code == requests.codes.ok:
            result = json.loads(r.text).get('result')
            # set the last block 
            return result


class DxPresale(Contract):
    def __init__(self, address):
        super().__init__(address, dxsnipeabi.abi)
        self._token_address = ''
        self._token = None
        self._min = 0
        self._max = 0
        self._goal = 0
        self._cap = 0
        self._start_time = 0
        self._end_time = 0
        self._called_init = False
        self._raised = 0
        self._init()


    def _init(self):
        '''
        This is suppose to make all required contract call 
        including token address
        '''
        # lets get the token address for a start : please rem to rm this 
        self._called_init = True
        self._token_address = self._contract_instance.functions.token().call()
        self._min = self._contract_instance.functions.minEthContribution().call()
        self._max = self._contract_instance.functions.maxEthContribution().call()
        self._goal = self._contract_instance.functions.goal().call()
        self._cap = self._contract_instance.functions.cap().call()
        self._start_time = self._contract_instance.functions.presaleStartTime().call()
        self._end_time = self._contract_instance.functions.presaleEndTime().call()
        self._raised = self._contract_instance.functions.CheckTotalEthRaised().call()


    def display(self):
        '''
        Displays all possible info that can be known 
        about the presale . including the token info 
        in a sweet format 
        '''
        assert self._called_init == True

        print('\n'*2)
        print('_'*70)
        print('Token Info: ')
        print(f'Name: {self.token.name}')
        print(f'Symbol: {self.token.symbol}')
        print(f'Address: {self.token.ca}')
        print('_'*30)
        print(f'Minimum Contribution: {self.min_contribution} BNB')
        print(f'Maximum Contribution: {self.max_contribution} BNB')
        print(f'Soft Cap: {self.goal} BNB')
        print(f'Hard Cap: {self.cap} BNB')
        print(f'Start Time: {self.start_time}')
        print(f'End Time: {self.end_time}')
        print(f'Raised: {self.raised}')
        print(f'Started: {self.started}')
        print(f'Ended: {self.ended}')
        print('_'*30)


    @property
    def token(self):
        '''
        constructs a token contract from the token address
        of the contract 
        '''
        assert self._called_init == True
        if not self._token:
            self._token = Token(self._token_address)
        
        return self._token

    @property
    def start_time(self):
        if isinstance(self._start_time, int):
            self._start_time = datetime.datetime.fromtimestamp(self._start_time)
        return self._start_time

    @property
    def end_time(self):
        if isinstance(self._end_time, int):
            self._end_time = datetime.datetime.fromtimestamp(self._end_time)
        return self._end_time

    @property
    def goal(self):
        return round(self._goal/10**18, 2)

    @property
    def cap(self):
        return round(self._cap/10**18, 2)

    @property
    def min_contribution(self):
        return self._min/10**18

    @property
    def max_contribution(self):
        return self._max/10**18

    @property
    def raised(self):
        return self._raised/10**18

    @property
    def ended(self):
        '''
        returns True if presale is ended
        '''
        return datetime.datetime.now() > self.end_time 

    @property
    def started(self):
        return datetime.datetime.now() > self.start_time



class DxPresaleScraper(object):
    CONTRACT_DEPLOYER = '0xbacebad5993a19c7188db1cc8d0f748c9af1689a'
    def __init__(self, block=0):
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
                presale = DxPresale(address)
                presale.display()


    def get_presale_address_from_transaction(self, tx):
        receipt = bama3.wb3.eth.get_transaction_receipt(tx)
        log_count = len(receipt.logs)
        if log_count == 2:
            return receipt.logs[1].address
        print(receipt)
        input('ERR: Please look into this unknown !')


if __name__ == '__main__':
    # presale = DxPresale('0xF1838e59e54967c3a41f45eA9C5ab7432b8A9B30')
    # presale.display()
    dxscraper = DxPresaleScraper(9235036)
    while True:
        dxscraper.get_presale_deploy_transactions()
        time.sleep(60)

    # print(dxscraper.__dict__)