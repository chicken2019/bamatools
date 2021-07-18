# This was named token3 as "token" was causing conflict 

import json

from .contract import Contract
from . import abis 

class Token(Contract):
	def __init__(self, contract_address='', **kwargs):
		super().__init__(contract_address, kwargs.get('abi') or abis.erc20)
		if kwargs.get('load'):
			self._load()

	def _load(self):
		self._name = self.contract_instance.functions.name().call()
		self._symbol = self.contract_instance.functions.symbol().call()
		self._decimals = self.contract_instance.functions.decimals().call()
		self._supply = self.contract_instance.functions.totalSupply().call()

	def __bool__(self):
		return self._is_token

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

