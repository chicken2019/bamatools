# $5
from web3 import Web3
import bama3
from token3 import Token
from contract import Contract

router_address = '0x10ed43c718714eb63d5aa57b78b54704e256024e'
factory_address = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'
bnb_address = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'

bnb = Token(bnb_address)

class PancakeRouter(Contract):
	def __init__(self):
		self._ca = router_address
		super().__init__(self._ca)



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