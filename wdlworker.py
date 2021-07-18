import datetime

from celery import Celery

import bama3
import apit 
import pancake

app = Celery('wdl')
app.conf.broker_url='redis://127.0.0.1:6379/0'
app.conf.task_serializer='pickle'
app.conf.result_serializer='pickle'
app.conf.accept_content=['pickle']
app.conf.result_accept_content=['pickle']
app.conf.result_backend ='redis://127.0.0.1:6379/0'
app.conf.result_expires=60*60 # 1 hour 

@app.task
def debug_task():
	print(f'Request : This is a debug task ')

@app.task
def liquidity_callback(tx):
	# resolve the tx address into tx object
	# we're previously passing in the transaction object
	# but the broker is not able to serialize it 
	# this will be reverse as we re going to use pickle serializer 
	txo = bama3.wb3.eth.get_transaction(tx)

	# resove token from tx input
	token_ca = bama3.get_ca_from_input(txo.input)

	print('[INFO] token_ca ', token_ca)

	# resove lp pair from token using pancake factory 
	factory = pancake.PancakeFactory()
	pair_ca = factory.get_pair(token_ca)

	# make a pair object out of the ca 
	pair_token = pancake.PancakePair(pair_ca)
	pair_token.get_reserves()

	# make a json out of of the parameters 
	amount = round(txo.value/10**18, 4)
	timestamp = int(datetime.datetime.now().timestamp())
	fresh = bama3.is_first_liquidity(pair_ca, txo)
	print('Fresh ? ', fresh)
	json = apit.api_constructor(pair_token, txo.blockNumber, timestamp, amount, tx, fresh)
	print(json)
	# simulated middle ware for extracheck 
	# 1- # dont bother pushing it at all if token0 is bnb 
	if pair_token.token0 == pancake.bnb:
		print('[ISSUE] This is a double bnb liquidity transaction !')
		return 

	#--> [API SERVER]
	reqr = apit.api_connector(json) 
	print(reqr.content)
	return reqr