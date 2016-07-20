##
#   :namespace  cross3d.studiomax.studiomaxgroup
#
#   :remarks    [desc::commented]
#   
#   :author     douglas
#   :author     Blur Studio
#   :date       09/26/13
#

import cross3d
from cross3d.studiomax.studiomaxscenelayer import StudiomaxSceneLayer

class StudiomaxGroup(StudiomaxSceneLayer):

	'''
		Since Max does not have a native group object that fit our need, we are exposing layers instead.
		For your information, native groups in Max are a way to contain a bunch of object under a single transform.
	'''

	pass

# register the symbol
cross3d.registerSymbol('Group', StudiomaxGroup)
