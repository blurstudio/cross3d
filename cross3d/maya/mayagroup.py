import cross3d
from cross3d.abstract.abstractgroup import AbstractGroup

class MayaGroup(AbstractGroup):
	pass
# register the symbol
cross3d.registerSymbol('Group', MayaGroup)