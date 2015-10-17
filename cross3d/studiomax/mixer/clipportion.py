##
#	\namespace	blur3d.api.studiomax
#
#	\remarks	The blur3d.api.studiomax.ClipPortion module provides an
#				objectified representation of a region of a Clip, to allow for
#				cleaner interaction with the Max Motion Mixer.
#	
#	\author		willc@blur.com
#	\author		Blur Studio
#	\date		09/28/15
#

import Py3dsMax
from Py3dsMax import mxs
from blur3d.api import TrackPortion
from blur3d.api.abstract.mixer.clipportion import AbstractClipPortion

################################################################################
#####------------------------------ Classes -------------------------------#####
################################################################################

class StudiomaxClipPortion(AbstractClipPortion):
	"""A portion of a Clip.

	Attributes:
		end: The end of the region, in global frames.
		start: The start of the region, in global frames.
		clip: The Clip of which this ClipPortion is a portion.
	"""
	
	def __str__(self):
		return '{}: {}-{}'.format(self.clip, self.start, self.end)

################################################################################

# register the symbol
from blur3d import api
api.registerSymbol('ClipPortion', StudiomaxClipPortion)
