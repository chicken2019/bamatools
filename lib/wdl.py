import time
import threading
import bama3
import pancake
from queue import Queue

bnb_address = '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c'
router_address = '0x10ed43c718714eb63d5aa57b78b54704e256024e'
POLL_TIME = 5
BIG_BNB_VALUE = 5
LIQUIDTY_FUNCTION_IDENT = '0xf305d719'


class WDL(object):
	def __init__(self, callback) -> None:
		super().__init__()
		self._events_queue = Queue()
		self._callback = callback
		self._filter_liquidity_thread()


	def _is_big_transaction(self, val):
		return val > BIG_BNB_VALUE


	def _is_liquidity_transaction(self, tnx):
		tx = bama3.wb3.eth.get_transaction(tnx)
		if tx.input.startswith(LIQUIDTY_FUNCTION_IDENT):
			return tx


	def _probe(self):
		# cnt = 0
		router_bnb_deposit_filter = pancake.bnb.contract_instance.events.Deposit().createFilter(
			fromBlock='latest', 
			argument_filters={
				'dst': router_address
			})

		while True:
			time.sleep(POLL_TIME)
			print('[INFO] Checking for new entries .. ')  # debug
			
			# this is a fix for 'filter not found' err
			try:
				entries = router_bnb_deposit_filter.get_new_entries()
			except ValueError:
				router_bnb_deposit_filter = pancake.bnb.contract_instance.events.Deposit().createFilter(
					fromBlock='latest', 
					argument_filters={
						'dst': router_address
					})
				entries = router_bnb_deposit_filter.get_new_entries()

			# print('.', end='')
			
			for e in entries:
				self._events_queue.put(e)

			# renew the var filter every 5 usage 
			# cnt += 1
			# if cnt == 2:
			# 	print('[INFO] Renewing Filter ')
			# 	router_bnb_deposit_filter = pancake.bnb.contract_instance.events.Deposit().createFilter(
			# 		fromBlock='latest', 
			# 		argument_filters={
			# 			'dst': router_address
			# 		})
			# 	cnt = 0


	def probe(self, ):
		print('Starting probe thread .. ', end='')  # debug
		_pt = threading.Thread(target=self._probe)
		_pt.setDaemon(True)
		_pt.start()
		print('Done ! . ')


	def _filter_liquidity(self):
		while True:
			event = self._events_queue.get()
			_bnb_amount = event.args.wad/10**18
			_tnx_hash = event.transactionHash.hex()

			if self._is_big_transaction(_bnb_amount):
				tx = self._is_liquidity_transaction(_tnx_hash)
				if tx:
					print(_tnx_hash, 'Cost:',  _bnb_amount)
					self._callback(_tnx_hash)
					# self._callback(tx)


	def _filter_liquidity_thread(self, ):
		print('Starting liquity filter thread .. ', end='')  # debug
		_pt = threading.Thread(target=self._filter_liquidity)
		# _pt.setDaemon(True)
		_pt.start()
		print('Done ! . ')
