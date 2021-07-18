# sniper bot , takes in a contract address 
# monitor all activity involving the contract
# address and filter out liquidity 

# self question 
# can web3 get pending receipt using block number 
import os
import time
import json 
import web3
from web3 import Web3
from web3.middleware import geth_poa_middleware

wb3 = web3.Web3(web3.Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
wb3.middleware_onion.inject(geth_poa_middleware, layer=0)

abi_folder = 'abis'
# 
router_address = '0x10ed43c718714eb63d5aa57b78b54704e256024e'
factory_address = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'
bnb_address = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c'


class Bama3:
	

	pancakelp_abi = json.load(open(os.path.join(abi_folder, 'pancakelp.abi')))
	pancakefactory_abi = json.load(open(os.path.join(abi_folder, 'pancakefactory.abi')))
	pancakerouter_abi = json.load(open(os.path.join(abi_folder, 'pancakerouter.abi')))
	erc20_abi = json.load(open(os.path.join(abi_folder, 'erc20.abi')))
	
	def __init__(self):
		wb3.eth.account.enable_unaudited_hdwallet_features() 
	
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
	# 	return self._is_token

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


class PancakePair(Token):
	def __init__(self, ca):
		super().__init__(ca, abi=Bama3.pancakelp_abi)
		self._ca = ca
		self._balance = 0
		
	def balance(self): 
		self._balance = self.contract_instance.functions.totalSupply().call()		
		return self._balance

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
	SWAP_FEE = 0.02
	def __init__(self):
		super().__init__()
		self._factory = PancakeFactory()

	def get_token_lp(self, token_ca):
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


	def sell(self, token_address, token_amount, wallet_address='', private_key=''):
		nonce = wb3.eth.get_transaction_count(wallet_address)
		new_txn = _router.contract_instance.functions.swapExactTokensForETHSupportingFeeOnTransferTokens(
			token_amount, # convert to raw 
			0, # amount Out Min 
			[token_address, web3.Web3.toChecksumAddress(bnb_address)], # path 
			wallet_address, 
			int(time.time())+10000 # now + 10 seconds
		).buildTransaction({
			'from': wallet_address, 
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





def await_liquidity_pair(token_address):
	while True:
		print('(info) Probing FActory for pair address ... ', end='', flush=True)
		lp_address = _factory.get_pair(token_address)
		print(f'[{lp_address}]')
		
		if lp_address == '0x0000000000000000000000000000000000000000':
			# bad address 
			print('No Liquidity Pair yet .. ')
			continue
		
		print('(INFO) fOUND a Liquidity Pair')
		return lp_address


if __name__ == '__main__':
	# the amount of token to sell in bnb

	print('(info) Loading account .. ')
	private_key = open('private.key').read().strip()
	print('(debug) private_key: ', private_key[:16],  '...')

	if not private_key:
		print('Please check private key file to make sure its valid ')
		exit()

	# the user's wallet derived from the private key 
	account = wb3.eth.account.from_key(private_key)
	# derive users address from imported account 
	wallet_address = web3.Web3.toChecksumAddress(account.address)
	print(f'(info) Account derv from key: {wallet_address}')
	
	# get some balance 
	wallet_balance = wb3.eth.get_balance(wallet_address)
	print(f'(info) Balance: {round(wallet_balance/10**18, 4)} BNB')
	

	# the token contract address
	while True:
		try:
			token_address = web3.Web3.toChecksumAddress(input('Enter Token Address: '))
			# make a contract out of the token address
			token_object = Token(token_address)
		except Exception as ex:
			print(f'(Error) {ex}')
			continue

		try:
			sell_percent = int(input('Enter token percent to sell: '))
		except ValueError:
			print('Invalid percent entered !!')
			continue

		break

	token_balance = token_object.balance(wallet_address)
	token_amount = int(token_balance * (sell_percent/100))
	print(f'Token Balance: {token_balance/10**token_object.decimals} {token_object.symbol}')
	print(f'Token to sell: {token_amount/10**token_object.decimals} {token_object.symbol}')

	# pancake factory 
	print('(INFO) Initializing FActory .. ', end='', flush=True)
	_factory = PancakeFactory()
	print(':)')

	# we defaulted to another method for this .

	# block until liquidity is available 
	lp_address = await_liquidity_pair(token_address)

	# start probing for balance 
	print(f'(info) Initializing Pair contract at [{lp_address}]')
	pair_contract = PancakePair(lp_address)


	while True:
		print('(inFo) Waiting for Mint operation .. ')
		pair_balance = pair_contract.balance()/10**18
		print('(debug) ', pair_balance)
		if pair_balance > 0:
			print('(info) Liquidity has been minteD .. proceeding to SELL')
			break

		time.sleep(5)

	if pair_balance > 0 and pair_balance < 1:
		print('(warning) Token has been rug pulled ! :( :( :(')
		input('<enter> to proceed forcefully .. ')

	print('(info) Checking Spending approval for pancake Router on contract .. ')
	tx = Bama3.approve(token_address, wallet_address, router_address, private_key=private_key)
	print(f'(debug) approve tx: {tx}')	

	print('(INFO) Initializing Router .. ', end='', flush=True)
	_router = PancakeRouter()
	print(':)')

	input('<enter> to proceed 1.')	
	input('<enter> to proceed 2.')	

	print('(info) Preparing to MAke Selloff.. ')	
	tx_hash = _router.sell(token_address, token_amount, wallet_address, private_key)
	if tx_hash:
		print(f'(info) Tx Hash: ', tx_hash)
			
	# can the transaction status be checked
	# wb3.eth.get_transaction(tx_hash); if ftx['status'] == '' ... 
	input('<enter> to quit !')