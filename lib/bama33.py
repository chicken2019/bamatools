# bama33 
# the renounced file .. the main chef .. the cordinator 

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
		self._hash = txh # the transaction hash itself
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
		self._tx = wb3.eth.get_transaction(self._hash)
		self._extract_data()


	@staticmethod
	def is_liquidity_transaction(transaction_hash):
		'''
		Returns True if transaction is one involving liquidity
		'''
		return self._tx.input.startswith(self.LIQUIDTY_FUNCTION_IDENT):
		

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
			self._receipt = wb3.eth.get_transaction_receipt(self._tx)
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
