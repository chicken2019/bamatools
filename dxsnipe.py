import os,sys
import datetime
import time
import json
import web3
import requests
import dxsale
import dxscrape
import blockexplorer
from web3 import Web3
from web3.middleware import geth_poa_middleware

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
    dxscraper = dxscrape.DxPresaleScraper(wb3, 9235036)
    while True:
        dxscraper.get_presale_deploy_transactions()
        time.sleep(60)
