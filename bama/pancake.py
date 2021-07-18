# $5
from web3 import Web3
from . import abis
from . import token3
from .contract import Contract
from .tokens import bnb

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