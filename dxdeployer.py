import dxdeployerabi

class DxDeployer(Contract):
	def __init__(self, address, w3=None):
		super().__init__(address, dxdeployerabi.abi)


	def presale_owner_to_index(self, owner):
		idx = self._contract_instance.functions.presaleOwnerToIndex(owner)

	def __str__(self):
		return f'DxDeployer({self.ca})'
