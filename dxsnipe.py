# buys into the presale 
import os,sys
import datetime
import time
import json

import web3
import requests
from web3 import Web3
from web3.middleware import geth_poa_middleware

import dxsale
import dxscrape

wb3 = web3.Web3(web3.Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
wb3.middleware_onion.inject(geth_poa_middleware, layer=0)

def load_private_key():
    print('(info) Loading account .. ')
    private_key_file = 'private.key'
    if not os.path.exists(private_key_file):
        print('Please make sure private key exists .. ')

    private_key = open(private_key_file).read().strip()
    print('(debug) private_key: ', private_key[:16],  '...')
    if not private_key:
        print('Please check private key file to make sure its valid ')
        exit()

    return private_key


if __name__ == '__main__':
    private_key = load_private_key()
    # the user's wallet derived from the private key 
    account = wb3.eth.account.from_key(private_key)
    
    # derive users address from imported account 
    wallet_address = web3.Web3.toChecksumAddress(account.address)
    print(f'(info) Account derv from key: {wallet_address}')
    
    # get some balance 
    wallet_balance = wb3.eth.get_balance(wallet_address)
    print(f'(info) Balance: {round(wallet_balance/10**18, 4)}')
    
    print('Please ensure the BNB amount is sufficient to snipe.')

    # while True:
    try:
        amount_in_bnb = float(input('Enter amount to ape : (in BNB): '))
    except ValueError:
        print('(error) invalid amount . ')
        quit()

    print(f'(debug) $amount_in_bnb = {amount_in_bnb}')

    presale_address = input('Enter presale contract address : ')
    dxsale_o = dxsale.DxPresale(presale_address, wb3)
    dxsale_o.display()

    input('<ENTER> to proceed .')
    print(f'Attempting to snipe presale with {amount_in_bnb} BNB')
    dxsale_o.snipe(amount_in_bnb, private_key)
    input('<enter> to exit !')
