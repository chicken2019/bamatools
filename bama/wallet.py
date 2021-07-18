import time
import threading
import bama3
from wallettoken import WalletToken

MILLISECONDS = 1000


class Wallet(object):
    def __init__(self, address='') -> None:
        self._address = ''
        self._tokens = {}
        self._polling_time = 20
        self._address = address


    @property
    def address(self):
        return self._address


    @address.setter
    def address(self, address):
        print(f'Wallet address updated to {address}') # debug
        self._address = address


    def poll(self):
        self._poller(self._update_balance)


    def _poller(self, callback) -> None:
        print('starting poller .. ')
        _to = threading.Thread(target=callback)
        _to.setDaemon(True)
        _to.start()


    def _update_balance(self):
        while True:
            # print('updating balances .. ')
            
            for token, wallet_token in self._tokens.items():
               wallet_token.update_balance()
            
            # wait for the next poll 
            time.sleep(self._polling_time)


    def _render(self, token) -> str:
        return f'{token.balance} : {token.name}'


    def add_token(self, contract_address):
        self._tokens.update({contract_address: WalletToken(contract_address, self._address)})


    def set_polling_time(self, t):
        self._polling_time = t


    def show(self) -> None:
        for token_ca, wallet_token in self._tokens.items():
            print(self._render(wallet_token))
