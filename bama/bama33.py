# bama33 
# the renounced file .. the main chef .. the cordinator 
import web3
import abis
from .pancake import PancakePair

from web3 import Web3
from web3.middleware import geth_poa_middleware

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
