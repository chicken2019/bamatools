import json
import os
import pathlib

ABI_FOLDER = os.path.join(pathlib.Path(__file__).parent.parent.resolve(), 'abis')

def resolve_abis(filename: str) -> any:
	return json.load(open(os.path.join(ABI_FOLDER, filename)))

pancakelp = resolve_abis('pancakelp.abi')
pancakefactory =resolve_abis('pancakefactory.abi')
pancakerouter = resolve_abis('pancakerouter.abi')
erc20 = resolve_abis('erc20.abi')

