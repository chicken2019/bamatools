# https://bscscan.com/address/0x5d7272e2c4a1b2b6c1de4402d56eaec70d3b36cc#tokentxns
# the difference between this and Token is that 
# this has an account associated to it as well as
# the address of that account 

import json
import bama3
from token3 import Token


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


    def update_balance(self):
        # balance = wallet_token.contract_instance.functions.balanceOf(
            # self._address).call()
        balance = bama3.Bama3.get_token_balance(self)
        self._balance = balance


    def __repr__(self):
        return f'WalletToken({self._contract_address})'

