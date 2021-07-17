import wdl		
import bama3
import wdlworker 

def liquidity_callback(tx):
	# ## #
	print(tx)
	wdlworker.liquidity_callback.delay(tx)

if __name__ == '__main__':
	wdl = wdl.WDL(wdlworker.liquidity_callback.delay)
	wdl.probe()
