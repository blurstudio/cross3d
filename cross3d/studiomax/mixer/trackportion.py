##
#	\namespace	blur3d.api.studiomax
#
#	\remarks	The blur3d.api.studiomax.TrackPortion module provides an
#				objectified representation of a region of a Track, to allow for
#				cleaner interaction with the Max Motion Mixer.
#	
#	\author		willc@blur.com
#	\author		Blur Studio
#	\date		09/28/15
#

import Py3dsMax
from Py3dsMax import mxs
from blur3d.api.abstract.mixer.trackportion import AbstractTrackPortion

################################################################################
#####------------------------------ Classes -------------------------------#####
################################################################################

class StudiomaxTrackPortion(AbstractTrackPortion):
	"""A region within a Track.

	Attributes:
		end: The end of the region, in global frames.
		start: The start of the region, in global frames.
	"""

	def __str__(self):
		return '{}: {}-{}'.format(self.track, self.start, self.end)

################################################################################

# register the symbol
from blur3d import api
api.registerSymbol('TrackPortion', StudiomaxTrackPortion)
