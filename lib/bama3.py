import json
import os
import web3
from web3.middleware import geth_poa_middleware

wb3 = web3.Web3(web3.Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
wb3.middleware_onion.inject(geth_poa_middleware, layer=0)

abi_folder = 'abis'

erc20_abi = json.load(open(os.path.join(abi_folder, 'erc20.abi')))
pancakelp_abi = json.load(open(os.path.join(abi_folder, 'pancakelp.abi')))
pancakefactory_abi = json.load(open(os.path.join(abi_folder, 'pancakefactory.abi')))

dead_address = '0x0000000000000000000000000000000000000000'

def get_ca_from_input(txi):
	# function length = 10, address length = 40
	return ''.join(['0x', txi[10:10+64][64-40:]])


def get_token_balance(wallet_token):
	balance = wallet_token.contract_instance.functions.balanceOf(
		wallet_token.address).call()
	return balance


def get_token_data(token) -> tuple:
	try:
		name = token.contract_instance.functions.name().call()
		symbol = token.contract_instance.functions.symbol().call()
		decimals = token.contract_instance.functions.decimals().call()
	except Exception as e :
		print(e)
		return 
	else:
		return (name, symbol, decimals)


def contract(contract_address, abi):
	_abi = abi 
	if _abi:
		contract_instance = wb3.eth.contract(
			address=web3.Web3.toChecksumAddress(contract_address),
			abi=_abi)
		return contract_instance


def is_first_liquidity(lp_token_ca, tx):
	# just check the lp balance . 
	# check the minted lp token 
	# confirm it's the same as supply balance 
	return False
	# # fetch the tx transaction receipt
	# receipt = wb3.eth.get_transaction_receipt(tx) 
	# cont = contract.Contract(lp_token_ca) 
	# processed_logs = cont.contract_instance.events.Transfer.processReceipt(receipt)
	# pre_main_transfer_event = processed_logs[2]
	# main_transfer_event = processed_logs[3]
	# return pre_main_transfer_event.args['from'] == dead_address and \
	# 	pre_main_transfer_event.args['to'] == dead_address and \
	# 	lp_token_ca == main_transfer_event.address


def private_key_from_mnemonics(mnemonics):
	return wb3.eth.account.from_mnemonic(mnemonics).privateKey.hex()

