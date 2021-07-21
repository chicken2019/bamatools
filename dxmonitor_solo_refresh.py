import os,sys
import datetime
import time
import json

import web3
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

def time_to_block(ts):
    return (((ts-1626718326)/3)+9300058)

if __name__ == '__main__':
    private_key = load_private_key()
    while True:
        presale = dxsale.DxPresale('0xD5f870f0D5E3b7235963dE5b8D24382AAe3a13dB', wb3)
        # presale = dxsale.DxPresale('0x238dd8Fcd60f84FfC2beDB81FAe2004B4E86632b', wb3)
        presale.display()
        input('<enter> to refetch !')
    # while True:
    #     try:
    #         date_time = input('Enter start time (01/06/2021 12:00): ')
    #         timestamp = datetime.datetime.strptime(date_time, '%d/%m/%Y %H:%M').timestamp()
    #     except Exception as ex:
    #         print(ex)
    #     else: 
    #         break

    # block = time_to_block(timestamp)
    # print(f'(info) Derived block: {block}')
    # dxscraper = dxscrape.DxPresaleScraper(wb3, block)
    # while True:
    #     dxscraper.get_presale_deploy_transactions()
    #     print('Waiting for next iteration .. ')
    #     time.sleep(60)
