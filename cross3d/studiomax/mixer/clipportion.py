##
#	\namespace	cross3d.studiomax
#
#	\remarks	The cross3d.studiomax.ClipPortion module provides an
#				objectified representation of a region of a Clip, to allow for
#				cleaner interaction with the Max Motion Mixer.
#	
#	\author		willc
#	\author		Blur Studio
#	\date		09/28/15
#

import Py3dsMax
from Py3dsMax import mxs
from cross3d import TrackPortion
from cross3d.abstract.mixer.clipportion import AbstractClipPortion

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
		sourceEnd = mxs.globalToLocal(self.clip.clip, int(self.end))
		sourceIn = self.clip.clip.orgstart
		return sourceEnd - sourceIn

	@property
	def sourceStart(self):
		"""The number of frames from the beginning of the clip's file at which
		this ClipPortion starts."""
		# In Max, clips can't be trimmed to subframes, so we shouldn't have to
		# worry about rounding.  All the same, int will take care of this for us
		sourceStart = mxs.globalToLocal(self.clip.clip, int(self.start))
		sourceIn = self.clip.clip.orgstart
		return sourceStart - sourceIn

	def __str__(self):
		return '{}: {}-{}'.format(self.clip, self.start, self.end)

################################################################################

# register the symbol
import cross3d
cross3d.registerSymbol('ClipPortion', StudiomaxClipPortion)
