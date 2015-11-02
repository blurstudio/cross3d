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

	@property
	def sourceEnd(self):
		"""The number of frames from the beginning of the clip's file at which
		this ClipPortion ends."""
		# In Max, clips can't be trimmed to subframes, so we shouldn't have to
		# worry about rounding.  All the same, int will take care of this for us
		return mxs.globalToLocal(self.clip.clip, int(self.end))

	@property
	def sourceStart(self):
		"""The number of frames from the beginning of the clip's file at which
		this ClipPortion starts."""
		# In Max, clips can't be trimmed to subframes, so we shouldn't have to
		# worry about rounding.  All the same, int will take care of this for us
		return mxs.globalToLocal(self.clip.clip, int(self.start))

	def __str__(self):
		return '{}: {}-{}'.format(self.clip, self.start, self.end)

################################################################################

# register the symbol
from blur3d import api
api.registerSymbol('ClipPortion', StudiomaxClipPortion)
