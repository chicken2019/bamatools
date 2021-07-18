import os
import json
import datetime
import web3
import dxsnipeabi

from web3 import Web3
from web3.middleware import geth_poa_middleware

wb3 = web3.Web3(web3.Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
wb3.middleware_onion.inject(geth_poa_middleware, layer=0)

abi_folder = 'abis'

class Bama3:
    pancakelp_abi = json.load(open(os.path.join(abi_folder, 'pancakelp.abi')))
    pancakefactory_abi = json.load(open(os.path.join(abi_folder, 'pancakefactory.abi')))
    pancakerouter_abi = json.load(open(os.path.join(abi_folder, 'pancakerouter.abi')))
    erc20_abi = json.load(open(os.path.join(abi_folder, 'erc20.abi')))

    @staticmethod
    def contract(contract_address, abi):
        _abi = abi 
        if _abi:
            contract_instance = wb3.eth.contract(
                address=web3.Web3.toChecksumAddress(contract_address),
                abi=_abi)
            return contract_instance


class Contract(object):
    def __init__(self, contract_address, abi=''):
        self._contract_address = contract_address
        self._contract_instance = Bama3.contract(contract_address, abi or '')
        self._abi = self.contract_instance.abi

    @property
    def contract_address(self):
        return Web3.toChecksumAddress(self._contract_address)

    @contract_address.setter
    def contract_address(self, contract_address: str) -> None:
        self._contract_address = contract_address

    @property
    def contract_instance(self):
        return self._contract_instance

    @property
    def ca(self):
        return self._contract_address

    @property
    def abi(self):
        return self._abi

    def __repr__(self):
        return f'Contract({self._contract_address})'

    def __str__(self):
        return f'{self._contract_address})'


class Token(Contract):
    def __init__(self, contract_address='', **kwargs):
        super().__init__(contract_address, kwargs.get('abi') or Bama3.erc20_abi)
        # if kwargs.get('load'):
        self._load()

    def _load(self):
        print('_loading_token_info ..')
        self._name = self.contract_instance.functions.name().call()
        self._symbol = self.contract_instance.functions.symbol().call()
        self._decimals = self.contract_instance.functions.decimals().call()
        self._supply = self.contract_instance.functions.totalSupply().call()

    # def __bool__(self):
    #   return self._is_token

    def __repr__(self):
        return f'Token( {self._contract_address} )'

    def __eq__(self, other):
        return self.contract_address == other.contract_address

    def balance(self, account):
        return self.contract_instance.functions.balanceOf(account).call()

    @property
    def symbol(self):
        return self._symbol

    @property
    def name(self):
        return self._name

    @property
    def decimals(self):
        return self._decimals

    @property
    def total_supply(self):
        return self._supply


class DxPresale(Contract):
    def __init__(self, address, w3=None):
        super().__init__(address, dxsnipeabi.abi)
        assert w3 != None
        self._w3 = w3
        self._token_address = ''
        self._presale_address = web3.Web3.toChecksumAddress(address)
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


    def snipe(self, amount_in_bnb, private_key):
        '''
        This basically just sends bnb to the contract 
        @amount_in_bnb gat be in ether
        @private_key must be loaded
        '''
        # derive users address from imported account 
        account = self._w3.eth.account.from_key(private_key)
        wallet_address = web3.Web3.toChecksumAddress(account.address)
    
        nonce = self._w3.eth.get_transaction_count(wallet_address)
        txn = {
            'from': wallet_address, 
            'value': self._w3.toWei(amount_in_bnb, 'ether'), 
            'gas': 100000, 
            'gasPrice': self._w3.eth.gas_price,
            'nonce': nonce,
            'to': self._presale_address
        }
        print(f'(info) Signing transaction ..  ')
        signed_txn = self._w3.eth.account.sign_transaction(txn, private_key=private_key)
        # while True:
        try:
            print('(info) Broadcasting transaction')
            tx_token = self._w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        except ValueError as ex:
            print(f'(err) {ex}')
            input('Tap <enter> to rebroadcast transaction .. ')
            # continue
        # else:
        #     break

        tx_hash = self._w3.toHex(tx_token)
        print(f'Transaction Hash: {tx_hash}')
        return tx_token

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
        print(f'Presale address: {self._presale_address}')
        print(f'Minimum Contribution: {self.min_contribution} BNB')
        print(f'Maximum Contribution: {self.max_contribution} BNB')
        print(f'Soft Cap: {self.goal} BNB')
        print(f'Hard Cap: {self.cap} BNB')
        print(f'Start Time: {self.start_time}')
        print(f'End Time: {self.end_time}')
        print(f'Raised: {self.raised} BNB')
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
