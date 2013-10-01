##
#   :namespace  blur3d.api.studiomax.studiomaxgroup
#
#   :remarks    [desc::commented]
#   
#   :author     douglas@blur.com
#   :author     Blur Studio
#   :date       09/26/13
#

from blur3d.api.studiomax.studiomaxscenelayer import StudiomaxSceneLayer
from blur3d import api

class StudiomaxGroup(StudiomaxSceneLayer):
	'''
		Max not having the concept of groups, we expose layers as a fallback.
	'''
	pass

# register the symbol
api.registerSymbol('Group', StudiomaxGroup)

