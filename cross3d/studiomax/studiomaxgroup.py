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
		Since Max does not have a native group object that fit our need, we are exposing layers instead.
		For your information, native groups in Max are a way to contain a bunch of object under a single transform.
	'''

	pass

# register the symbol
api.registerSymbol('Group', StudiomaxGroup)

