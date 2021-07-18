import os
from queue import Queue
import threading 
import json
import time
import os
import web3

from bama.bama import PancakeFactory, Token, WDL, WBNB

from web3 import Web3
from web3.middleware import geth_poa_middleware


wb3 = web3.Web3(web3.Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
wb3.middleware_onion.inject(geth_poa_middleware, layer=0)

ONLY_FTL = False


def callback_func(liquidity_transaction_object, bnb_amount):
	
	first_liquidity = liquidity_transaction_object.is_first_liquidity()
	if ONLY_FTL:
		print(f'\ntx: {tx} | {bnb_amount} BNB ')
	else:
		print(f'\ntx: {tx} | {bnb_amount} BNB | FL: {first_liquidity} ')#| FTL Score: {score}%')


	token = Token(liquidity_transaction_object.token_address, load=True)
	print()
	print('Token Name: ', token.name)
	print('Token Symbol: ', token.symbol)
	print('Token Address: ', token.contract_address)


if __name__ == '__main__':
	wdl = WDL(callback_func, wb3)
	wdl.probe()
