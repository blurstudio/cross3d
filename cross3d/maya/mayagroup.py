from blur3d import api
from blur3d.api.abstract.abstractgroup import AbstractGroup

class MayaGroup(AbstractGroup):
	pass
# register the symbol
api.registerSymbol('Group', MayaGroup)