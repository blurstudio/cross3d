##
#   \namespace  blur3d.api.softimage.collection
#
#   \remarks    This module implements the collection class allowing to manipulate multiple objects.
#   
#   \author     douglas@blur.com
#   \author     Blur Studio
#   \date       04/20/15
#

#------------------------------------------------------------------------------------------------------------------------

from blur3d import api
from blur3d.api.abstract.collection import Collection as AbstractCollection

class Collection(AbstractCollection):
	pass

# Registering the symbol.
api.registerSymbol('Collection', Collection)