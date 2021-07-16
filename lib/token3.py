# This was named token3 as "token" was causing conflict 

import json

from contract import Contract
import bama3

class ByMixins:
	@classmethod
	def by_argument(cls, args: tuple) -> object:
		return cls(*args)

	@classmethod
	def by_dict(cls, data: dict) -> object:
		return cls(**data)

	@classmethod
	def by_json(cls, json_data: str) -> object:
		deserialize_dict = json.loads(json_data)
		return cls.by_dict(deserialize_dict)


class TokenData(object):
	def __init__(self, name='', symbol='', decimals=''):
		self._symbol = symbol
		self._name = name
		self._decimals = decimals


class Token(Contract, ByMixins):
	def __init__(self, contract_address='', **kwargs):
		super().__init__(contract_address, kwargs.get('abi') or bama3.erc20_abi)
		if self.contract_instance:
			token_data = bama3.get_token_data(self)
			
			# not all contracts are token 
			if token_data:
				name, symbol, decimals = token_data
				self._symbol = symbol
				self._name = name
				self._decimals = decimals
				self._is_token = True
			else:
				self._is_token = False
			
		else:
			self._is_token = False


	def __bool__(self):
		return self._is_token

	def __repr__(self):
		return f'Token( {self._contract_address} )'

	def __eq__(self, other):
		return self.contract_address == other.contract_address

	@property
	def is_token(self):
		return self._is_token

	@property
	def symbol(self):
		return self._symbol

	@property
	def name(self):
		return self._name

	@property
	def decimals(self):
		return self._decimals
