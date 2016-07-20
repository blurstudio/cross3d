##
#   \namespace  cross3d.studiomax.collection
#
#   \remarks    This module implements the collection class allowing to manipulate multiple objects.
#   
#   \author     douglas
#   \author     Blur Studio
#   \date       04/20/15
#

#------------------------------------------------------------------------------------------------------------------------

import cross3d
from cross3d.abstract.collection import Collection as AbstractCollection

class Collection(AbstractCollection):
	pass

# Registering the symbol.
cross3d.registerSymbol('Collection', Collection)