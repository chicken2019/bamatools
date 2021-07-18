from pancake import PancakePair
import requests
import settings 

def api_connector(json_data):
	'''
		This connects to the api server and sends in a new liquidty 
		This will be called from celery task 
	'''
	# print(json_data)
	connection_string = ''.join([settings.API_CONNECTION_STRING, '/liquidities/'])
	request = requests.post(connection_string, json=json_data)
	print('Status code: ', request.status_code)
	# if request.status_code == requests.codes.ok:
	return request


def api_constructor(pair: PancakePair, block: int, timestamp: int, amount: int, tx: str, fresh: bool) -> dict:
	''' makes a json format out of the passed object 
		based on what's required by the api server 
		to create a new liquidty

		@param lptoken - <Pair>
		@param block - int | the block where the liquidity occur 
		@timestamp - datetime.timestamp 
		@amount - int 

		output : --- 
		{'lptoken': {'name': 'lp2', 'symbol': 'lp2', 'decimals': 9, 'address': '0x93298393839283', 'reserve0': 283923, 'reserve1': 100, 'token0': serializers.TokenSerializer(instance=soup).data, 'token1': serializers.TokenSerializer(instance=bnb).data}, 'block':239928, 'amount':298, 'timestamp': 239389283928})

	'''
	return {
		'lptoken':
			 {
				'name': 	pair.name, 
				'symbol': 	pair.symbol, 
				'decimals': pair.decimals, 
				'address': 	pair.contract_address, 
				'reserve0': round(pair.reserve0, 4),
				'reserve1': round(pair.reserve1, 4),
				'token0': 
					{
						'name': 	pair.token0.name, 
						'symbol': 	pair.token0.symbol, 
						'decimals': pair.token0.decimals, 
						'address': 	pair.token0.contract_address, 
					},
				'token1': 
					{
						'name': 	pair.token1.name, 
						'symbol': 	pair.token1.symbol, 
						'decimals': pair.token1.decimals, 
						'address': 	pair.token1.contract_address, 
					}
			}, 
		'block': block,
		'timestamp': timestamp,
		'amount': amount,
		'tx': tx,
		'fresh': fresh
	}
