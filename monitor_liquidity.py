import os
from queue import Queue
import threading 
import json
import time
import os
import web3

from web3 import Web3
from web3.middleware import geth_poa_middleware

wb3 = web3.Web3(web3.Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
wb3.middleware_onion.inject(geth_poa_middleware, layer=0)
abi_folder = 'abis'

factory_address = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'
bnb_address = '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c'
router_address = '0x10ed43c718714eb63d5aa57b78b54704e256024e'
cake_cake_lp = '0x0ed7e52944161450477ee417de9cd3a859b14fd0'
NULL_ADDRESS = '0x0000000000000000000000000000000000000000000000000000000000000000'
POLL_TIME = 2.5
BIG_BNB_VALUE = 5
LIQUIDTY_FUNCTION_IDENT = '0xf305d719'


class Bama3(object):	

	pancakelp_abi = json.load(open(os.path.join(abi_folder, 'pancakelp.abi')))
	pancakefactory_abi = json.load(open(os.path.join(abi_folder, 'pancakefactory.abi')))
	pancakerouter_abi = json.load(open(os.path.join(abi_folder, 'pancakerouter.abi')))
	erc20_abi = json.load(open(os.path.join(abi_folder, 'erc20.abi')))
	
	def __init__(self):
		wb3.eth.account.enable_unaudited_hdwallet_features() 

	@staticmethod
	def get_ca_from_input(txi):
		'''
		function length = 10, address length = 40
		'''
		return ''.join(['0x', txi[10:10+64][64-40:]])

	@classmethod
	def extract_data_from_liquidity_transaction(cls, tx):
		
		ret = {'token_address': '', 'pair_address': '', 'minted': '', 'logs_count': 0}
		transaction_receipt = wb3.eth.get_transaction_receipt(tx)
		ret['logs_count'] = len(transaction_receipt.logs)
		for event in transaction_receipt.logs:
			if event.topics[0].hex().endswith('523b3ef'):
				if not ret.get('token_address'):
					ret['token_address'] = event.address
			
				if event.topics[1].hex() == NULL_ADDRESS: 
					data_value = int(event.data, 16)/10**18
					if data_value > 1:
						# this is the event where liquidity is minted
						ret['pair_address'] = event.address
						ret['minted'] = data_value

		return ret


	# @classmethod
	# def get_minted_liquidity_and_lp_from_transaction(cls, tx):
	# 	'''
	# 		@tx - the transaction string we working with 
	# 	'''
	# 	transaction_receipt = wb3.eth.get_transaction_receipt(tx)
	# 	# process the transfer events | Loading new token contract is redundant
	# 	for event in transaction_receipt.logs:
	# 		if event.topics[0].hex().endswith('523b3ef') and \
	# 		event.topics[1].hex() == NULL_ADDRESS: 
	# 		# 523b3ef is last char of transfer topic
		
	# 			# convert hex str to int then scale it down 
	# 			# 18 is standard erc20 decimal places 
	# 			data_value = int(event.data, 16)/10**18
	# 			if data_value > 1:
	# 				# this is the event where liquidity is minted
	# 				return data_value, event.address # address is the lp
	# 		else:
	# 			pass

	# 	return None, None
	# 	# in which case are we not going to find what we need ??? huh

	@classmethod
	def get_pair_supply(cls, pair_address):
		# construct a pair object from the token address
		pair = PancakePair(pair_address)
		
		# call for it's total supply 
		total_s = pair.total_supply
		
		return total_s/10**18


	@classmethod
	def get_pair_supply_from_transaction(cls, tx):
		# fetch transaction object
		transaction = wb3.eth.get_transaction(tx)

		# fetch token address from transaction input
		token_address = cls.get_ca_from_input(transaction.input)
		
		# get the token pair from pancake factory
		pair_address = _factory.get_pair(token_address)
		
		return cls.get_pair_supply(pair_address)
		


	@classmethod
	def is_first_liquidity(cls, data):
		if data.get('logs_count', 0) > 8:
			return True, -1
		else:
			# get the minted lp, pair address and pair supply 
			minted = data.get('minted')
			pair_address = data.get('pair_address')
			pair_supply = cls.get_pair_supply(pair_address)
			res = round(float((minted/pair_supply)*100), 4)
			return (res > 98, res)
	
	@staticmethod
	def contract(contract_address, abi):
		_abi = abi 
		if _abi:
			contract_instance = wb3.eth.contract(
				address=web3.Web3.toChecksumAddress(contract_address),
				abi=_abi)
			return contract_instance

	@staticmethod
	def private_key_from_mnemonics(mnemonics):
		return wb3.eth.account.from_mnemonic(mnemonics).privateKey.hex()

	
	@staticmethod
	def is_approve(token_address, spender_address):
		# make a contract object from the token address 
		token_contract = Bama3.contract(token_address, Bama3.erc20_abi)
		allowance = token_contract.functions.allowance(
			wallet_address, 
			web3.Web3.toChecksumAddress(spender_address)
		).call()
		allowance = allowance/10**18
		return allowance > 1


	@staticmethod 
	def approve(token_address, wallet_address, spender_address, private_key=''):
		'''
			//
		'''

		# confirm the private key passed 
		if not private_key:
			return 

		# make a contract object from the token address 
		token_contract = Bama3.contract(token_address, Bama3.erc20_abi)
		allowance = token_contract.functions.allowance(
			wallet_address, 
			web3.Web3.toChecksumAddress(spender_address)
		).call()
		allowance = allowance/10**18

		print('(debug) allowance: ', allowance)
		if allowance > 1:
			print('(info) Approval Allowance confirmed . ')
			return allowance

		nonce = wb3.eth.get_transaction_count(wallet_address)
		tx = token_contract.functions.approve(
			spender_address, 
			wb3.toWei(2**64-1,'ether')
		).buildTransaction({
			'from': wallet_address,
			'nonce': nonce
		})
		
		# signed the transaction
		signed_txn = wb3.eth.account.sign_transaction(tx, private_key)

		# broadcase the signed transaction 
		tx_hash = wb3.eth.send_raw_transaction(signed_txn.rawTransaction)
		return tx_hash




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
		return f'{self._contract_address}'


class Token(Contract):
	def __init__(self, contract_address='', **kwargs):
		super().__init__(contract_address, kwargs.get('abi') or Bama3.erc20_abi)
		if kwargs.get('load'):
			self._load()

	def _load(self):
		self._name = self.contract_instance.functions.name().call()
		self._symbol = self.contract_instance.functions.symbol().call()
		self._decimals = self.contract_instance.functions.decimals().call()
		self._supply = self.contract_instance.functions.totalSupply().call()

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
		super().__init__(ca, abi=Bama3.erc20_abi, load=True)


class PancakePair(Token):
	def __init__(self, ca):
		super().__init__(ca, abi=Bama3.pancakelp_abi, load=True)
		self._ca = ca
		
	def __repr__(self):
		return f'PancakePair( {self.contract_address} )'


class PancakeFactory(Contract):
	def __init__(self):
		self._ca = factory_address
		super().__init__(self._ca, abi=Bama3.pancakefactory_abi)

	def get_pair(self, token_ca):
		pair = self.contract_instance.functions.getPair(
				Web3.toChecksumAddress(token_ca), 
				Web3.toChecksumAddress(bnb_address)
			).call()
		return pair 


	def __repr__(self):
		return f'PancakeFactory( {self.contract_address} )'


class Pancake(object):
	def __init__(self):
		super().__init__()
		self._factory = PancakeFactory()
		self._router = PancakeRouter()

	@property
	def factory(self):
		return self._factory

	@property
	def router(self):
		return self._router

	def get_token_pair(self, token_ca):
		# pass the token and bnb to get pair on factory
		pair_ca = self._factory.get_pair(token_ca)

		# make a contract instance out of the ca 
		pair_contract = PancakePair(pair_ca)
		
		return pair_contract

class PancakeRouter(Contract):
	def __init__(self):
		self._ca = router_address
		super().__init__(self._ca, abi=Bama3.pancakerouter_abi)

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

class WDL(object):
	def __init__(self, callback) -> None:
		super().__init__()
		self._events_queue = Queue()
		self._callback = callback
		self._filter_liquidity_thread()


	def _is_big_transaction(self, val):
		return val > BIG_BNB_VALUE


	def _is_liquidity_transaction(self, tnx):
		try:
			tx = wb3.eth.get_transaction(tnx)
			if tx.input.startswith(LIQUIDTY_FUNCTION_IDENT):
				return tx
		except Exception as ex:
			print(ex)
			
	def _probe(self):
		# cnt = 0
		router_bnb_deposit_filter = bnb.contract_instance.events.Deposit().createFilter(
			fromBlock='latest', 
			argument_filters={
				'dst': router_address
			})

		while True:
			time.sleep(POLL_TIME)
			print('. ', end='', flush=True)
			try:
				entries = router_bnb_deposit_filter.get_new_entries()
			except ValueError:
				router_bnb_deposit_filter = bnb.contract_instance.events.Deposit().createFilter(
					fromBlock='latest', 
					argument_filters={
						'dst': router_address
					})
				entries = router_bnb_deposit_filter.get_new_entries()
			except Exception as ex:
				print(f'Err: {ex}')
			
			for e in entries:
				self._events_queue.put(e)


	def probe(self, ):
		print('(info) Starting probe thread .. ', end='')  # debug
		_pt = threading.Thread(target=self._probe)
		_pt.setDaemon(True)
		_pt.start()
		print('Done ! . ')


	def _filter_liquidity(self):
		# filters out > BIG_BNB  && filter out non liquidity tnx 
		while True:
			event = self._events_queue.get()
			_bnb_amount = event.args.wad/10**18
			_tnx_hash = event.transactionHash.hex()

			if self._is_big_transaction(_bnb_amount):
				tx = self._is_liquidity_transaction(_tnx_hash)
				if tx:
					# print('\n', _tnx_hash, 'Cost:',  _bnb_amount)
					self._callback(_tnx_hash, _bnb_amount)


	def _filter_liquidity_thread(self, ):
		print('(info) Starting liquity filter thread .. ', end='')  # debug
		_pt = threading.Thread(target=self._filter_liquidity)
		# _pt.setDaemon(True)
		_pt.start()
		print('Done ! . ')


def callback_func(tx, bnb_amount):
	data = Bama3.extract_data_from_liquidity_transaction(tx)
	print(data)
	fl, score = Bama3.is_first_liquidity(data)

	if ONLY_FTL:
		print(f'\ntx: {tx} | {bnb_amount} BNB ')
	else:
		print(f'\ntx: {tx} | {bnb_amount} BNB | FL: {fl} | FTL Score: {score}%')

	# print the token information 
	token_address = data.get('token_address')
	token = Token(token_address, load=True)
	print()
	print('Token Name: ', token.name)
	print('Token Symbol: ', token.symbol)
	print('Token Address: ', token.contract_address)


# def resolve_token_data(tx)


if __name__ == '__main__':
	bnb = Token(bnb_address)
	_factory = PancakeFactory()
	ONLY_FTL = False
	wdl = WDL(callback_func)
	wdl.probe()
