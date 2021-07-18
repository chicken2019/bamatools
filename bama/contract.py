from web3 import Web3
from . import blockexplorer
from . import bama33

bama_utils = bama33.W3Util
explorer = blockexplorer.BlockExplorer()

class Contract(object):
	def __init__(self, contract_address, abi=''):
		self._contract_address = contract_address
		# self._contract_instance = bama33.bama_utils.contract(contract_address, abi or explorer.get_contract_abi(contract_address))
		# self._abi = self.contract_instance.abi

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
