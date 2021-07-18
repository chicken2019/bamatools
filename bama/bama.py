from queue import Queue
import threading
import json
import time, datetime
import requests
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware

from . import abis, addresses

wb3 = web3.Web3(web3.Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
wb3.middleware_onion.inject(geth_poa_middleware, layer=0)

class W3Util(object):
	def __init__(self, w3):
		self._w3 = w3

	def contract(self, contract_address, abi):
		_abi = abi 
		if _abi:
			contract_instance = self._w3.eth.contract(
				address=web3.Web3.toChecksumAddress(contract_address),
				abi=_abi)
			return contract_instance


	@staticmethod
	def get_ca_from_input(txi):
		# function length = 10, address length = 40
		return ''.join(['0x', txi[10:10+64][64-40:]])

	def private_key_from_mnemonics(self, mnemonics):
		return self._w3.eth.account.from_mnemonic(mnemonics).privateKey.hex()

	
	def is_approve(self, token_address, spender_address):
		token_contract = self.contract(token_address, abis.erc20_abi)
		allowance = token_contract.functions.allowance(
			wallet_address, 
			web3.Web3.toChecksumAddress(spender_address)
		).call()
		allowance = allowance/10**18
		return allowance > 1


	def approve(self, token_address, wallet_address, spender_address, private_key=''):
		
		# confirm the private key passed 
		if not private_key:
			return 

		# make a contract object from the token address 
		token_contract = self.contract(token_address, abis.erc20_abi)
		allowance = token_contract.functions.allowance(
			wallet_address, 
			web3.Web3.toChecksumAddress(spender_address)
		).call()
		allowance = allowance/10**18

		print('(debug) allowance: ', allowance)
		if allowance > 1:
			print('(info) Approval Allowance confirmed . ')
			return allowance

		nonce = self._w3.eth.get_transaction_count(wallet_address)
		tx = token_contract.functions.approve(spender_address, self._w3.toWei(2**64-1,'ether')
		).buildTransaction({
			'from': wallet_address,
			'nonce': nonce
		})
		
		# signed the transaction
		signed_txn = self._w3.eth.account.sign_transaction(tx, private_key)

		# broadcase the signed transaction 
		tx_hash = self._w3.eth.send_raw_transaction(signed_txn.rawTransaction)
		return tx_hash


bama_utils = W3Util(wb3)

class Contract(object):
	def __init__(self, contract_address, abi=''):
		self._contract_address = contract_address
		self._contract_instance = bama_utils.contract(contract_address, abi or explorer.get_contract_abi(contract_address))
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
		super().__init__(contract_address, kwargs.get('abi') or abis.erc20)
		# if kwargs.get('load'):
		self._load()

	def _load(self):
		print('_loading_token_info ..')
		self._name = self.contract_instance.functions.name().call()
		self._symbol = self.contract_instance.functions.symbol().call()
		self._decimals = self.contract_instance.functions.decimals().call()
		self._supply = self.contract_instance.functions.totalSupply().call()

	# def __bool__(self):
	# 	return self._is_token

	def __repr__(self):
		return f'Token( {self._contract_address} )'

	def __eq__(self, other):
		return self.contract_address == other.contract_address

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


class ERC20Token(Token):
	def __init__(self, contract_address, *args, **kwargs):
		super().__init__(ca, abi=abis.erc20, load=True)


class WalletToken(Token):
    def __init__(self, contract_address='', address=''):
        super().__init__(contract_address)
        self._balance = 0
        self._address = address
        # update the balance if need be 
        if address:
            self.update_balance()

    @property
    def balance(self):
        return self._balance/10**self._decimals

    @balance.setter
    def balance(self, balance: float) -> None:
        self._balance = balance

    @property
    def address(self) -> str:
        return self._address

    @address.setter
    def address(self, address: str) -> None:
        self._address = address

    def __repr__(self):
        return f'WalletToken({self._contract_address})'


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


class LiquidityTransaction(object):
	'''
		What does this even do . 
		This is a object that's supposed to represent 
		a transaction involving adding liquidity 
		as well as helper functions to help filter and figure
		such transaction 
	'''
	LIQUIDTY_FUNCTION_IDENT = '0xf305d719'

	
	def __init__(self, txh):
		self._tx = None
		self._tx_hash = txh # the transaction hash itself
		self._block = 0
		self._logs_count = 0
		self._initiator = ''
		self._pair_address = ''
		self._token_address = ''
		self._minted = 0
		self._receipt = None
		self._init()


	def _init(self):
		'''
		'''
		self._tx = wb3.eth.get_transaction(self._tx_hash)
		self._extract_data()


	@staticmethod
	def is_liquidity_transaction(self):
		'''
		Returns True if transaction is one involving liquidity
		'''
		return self._tx.input.startswith(self.LIQUIDTY_FUNCTION_IDENT)

		

	def is_first_liquidity(self):
		'''
		Returns True if liquidity added is a first one 
		'''
		if self._logs_count > 8:
			return True
		else:
			_pair_s = self._pair_token.total_supply/10**18
			return round(float((self._minted/pair_s)*100), 4) > 98
	

	@property
	def receipt(self):
		if not self._receipt:
			self._receipt = wb3.eth.get_transaction_receipt(self._tx_hash)
		return self._receipt


	@classmethod
	def _extract_data(self):
		'''
			Extract 
		'''
		self._logs_count = len(self.receipt.logs)
		for event in self.receipt.logs:
			if event.topics[0].hex().endswith('523b3ef'):
				if not self._token_address:
					self._token_address = event.address
			
				if event.topics[1].hex() == NULL_ADDRESS: 
					data_value = int(event.data, 16)/10**18
					if data_value > 1:
						self._pair_address = event.address
						if self._pair_address:
							self._pair_token = PancakePair(self._pair_address)
						self._minted = data_value



	@property
	def logs_count(self):
		return self._logs_count

	@property
	def token_address(self):
		return self._token_address

	@property
	def pair_address(self):
		return self._pair_address

	@property
	def minted(self):
		return self._minted

	@property
	def hash(self):
		return self._hash



class WDL(object): 
	POLL_TIME = 2.5
	BIG_BNB_VALUE = 5
	LIQUIDTY_FUNCTION_IDENT = '0xf305d719'
	def __init__(self, callback, w3) -> None:
		self._w3 = w3
		super().__init__()
		self._events_queue = Queue()
		self._callback = callback
		self._filter_liquidity_thread()


	def _is_big_transaction(self, val):
		return val > self.BIG_BNB_VALUE


	def _is_liquidity_transaction(self, tnx):
		tx = self._w3.eth.get_transaction(tnx)
		if tx.input.startswith(self.LIQUIDTY_FUNCTION_IDENT):
			return tx


	def _probe(self):
		# cnt = 0
		router_bnb_deposit_filter = WBNB.contract_instance.events.Deposit().createFilter(
			fromBlock='latest', 
			argument_filters={
				'dst': addresses.ROUTER
			})

		while True:
			time.sleep(self.POLL_TIME)
			print('. ', end='', flush=True)  # debug
			
			# this is a fix for 'filter not found' err
			try:
				entries = router_bnb_deposit_filter.get_new_entries()
			except ValueError:
				router_bnb_deposit_filter = WBNB.contract_instance.events.Deposit().createFilter(
					fromBlock='latest', 
					argument_filters={
						'dst': router_address
					})
				entries = router_bnb_deposit_filter.get_new_entries()
			
			for e in entries:
				self._events_queue.put(e)

	def probe(self, ):
		print('Starting probe thread .. ', end='')  # debug
		_pt = threading.Thread(target=self._probe)
		_pt.setDaemon(True)
		_pt.start()
		print('Done ! . ')


	def _filter_liquidity(self):
		while True:
			event = self._events_queue.get()
			_bnb_amount = event.args.wad/10**18
			_tnx_hash = event.transactionHash.hex()

			if self._is_big_transaction(_bnb_amount):
				tx = self._is_liquidity_transaction(_tnx_hash)
				if tx:
					print(_tnx_hash, 'Cost:',  _bnb_amount)
					self._callback(_tnx_hash, _bnb_amount)


	def _filter_liquidity_thread(self, ):
		print('Starting liquity filter thread .. ', end='')  # debug
		_pt = threading.Thread(target=self._filter_liquidity)
		# _pt.setDaemon(True)
		_pt.start()
		print('Done ! . ')


class PancakeRouter(Contract):
	def __init__(self):
		self._ca = router_address
		super().__init__(self._ca, abi=abis.pancakerouter)

	def buy(self, token_address, amount_in_bnb, wallet_address='', private_key=''):
		nonce = wb3.eth.get_transaction_count(wallet_address)
		self.contract_instance.functions.swapExactETHForTokens(
			amount_in_bnb, # amountIn 
			0, # amount Out Min 
			[bnb_address, token_address], # path 
			wallet_address, # to 
			int(time.time())+1000# deadline 
			).buildTransaction({
				'from': wallet_address, 
				'value': wb3.toWei(amount_in_bnb, 'ether'), 
				'gas': 250000, 
				'gasPrice': wb3.toWei('5', 'gwei'),
				'nonce': nonce
			})

		signed_txn = wb3.eth.account.sign_transaction(new_txn, private_key='')
		tx_token = wb3.eth.send_raw_transaction(signed_txn.rawTransaction)
		if tx_token:
			return wb3.toHex(tx_token)


	def sell(self, token_address, percent=100, wallet_address='', private_key=''):
		nonce = wb3.eth.get_transaction_count(wallet_address)
		new_txn = _router.contract_instance.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
		0, # amount Out Min 
		[web3.Web3.toChecksumAddress(bnb_address), token_address], # path 
		wallet_address, 
		int(time.time())+10000 # now + 10 seconds
		).buildTransaction({
			'from': wallet_address, 
			'value': wb3.toWei(amount_in_bnb, 'ether'), 
			'gas': 400000, 
			'gasPrice': wb3.toWei('8', 'gwei'),
			'nonce': nonce
		})

		print(f'(info) Signing transaction ..  ')
		signed_txn = wb3.eth.account.sign_transaction(new_txn, private_key=private_key)
		print(f'(info) Broadcasting transaction to chain..  ')
		tx_token = wb3.eth.send_raw_transaction(signed_txn.rawTransaction)
		if tx_token:
			return wb3.toHex(tx_token)



class PancakeFactory(Contract):
	def __init__(self):
		self._ca = factory_address
		super().__init__(self._ca, abi=bama3.pancakefactory_abi)

	def get_pair(self, token_ca):
		pair = self.contract_instance.functions.getPair(
				Web3.toChecksumAddress(token_ca), 
				Web3.toChecksumAddress(bnb_address)
			).call()
		return pair 


class PancakePair(Token):
	def __init__(self, ca):
		super().__init__(ca, abi=abis.pancakelp)
		self._ca = ca
		self._balance = 0
		
	def total_supply(self): 
		self._supply = self.contract_instance.functions.totalSupply().call()		
		return self._supply

	def __repr__(self):
		return f'PancakePair( {self.contract_address} )'


class PancakePair(Token):
	def __init__(self, ca):
		super().__init__(ca, abi=bama3.pancakelp_abi)
		self._ca = ca
		self._reserve0 = 0
		self._reserve1 = 0
		self._token0_ca = ''
		self._token1_ca = ''
		self._token0 = None
		self._token1 = None
		self._sortnormal = True


	@property
	def rugpull(self):
		return self._reserve1 < 1

	def balance(self): 
		pass
		

	def get_reserves(self):
		ret = self.contract_instance.functions.getReserves().call()
		
		# fetch the tokens 
		self.get_tokens()

		# we need to divide them by the decimals
		if self._sortnormal: 
			self._reserve0 = ret[0]/10**self._token0.decimals # we need to get the token decimals 
			self._reserve1 = ret[1]/10**18 # bnb has 18 decimals 
		else:
			self._reserve0 = ret[1]/10**self._token0.decimals # we need to get the token decimals 
			self._reserve1 = ret[0]/10**18 # bnb has 18 decimals 
			
		# this reserves are not raw . . they've been scaled and formatted


	def get_tokens(self):
		t0 = self.contract_instance.functions.token0().call()
		if t0 == bnb_address:
			t1 = self.contract_instance.functions.token1().call()
			self._token0_ca = t1
			self._sortnormal = False
		else:
			self._token0_ca = t0
			
		self._token0 = Token(self._token0_ca)	
		self._token1_ca = bnb_address
		self._token1 = bnb


	@property
	def reserve0(self):
		return self._reserve0


	@property
	def reserve1(self):
		return self._reserve1


	@property
	def token0(self):
		return self._token0


	@property
	def token1(self):
		return self._token1


	def __repr__(self):
		return f'PancakePair( {self.contract_address} )'


class Pancake(object):
	SWAP_FEE = 0.02
	def __init__(self):
		super().__init__()
		self._factory = PancakeFactory()


	def get_bnb_price(self):
		pass


	def price_per_token(self, token_ca, quote_token):
		pass


	def price_per_usd(self, token_ca):
		pass


	def price_per_bnb(self, token_ca):
		# find the token lp 
		lp_token = self.get_token_lp(token_ca)
		
		# call the reserve method on it 
		lp_token.get_reserves()

		price = round((lp_token.reserve0/lp_token.reserve1)*(1-self.SWAP_FEE), 4)

		# return the price  
		return price 


	def get_token_lp(self, token_ca):
		# pass the token and bnb to get pair on factory
		pair_ca = self._factory.get_pair(token_ca)

		# make a contract instance out of the ca 
		pair_contract = PancakePair(pair_ca)
		
		return pair_contract


WBNB = Token(addresses.WBNB)
