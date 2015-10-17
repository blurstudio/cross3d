##
#	\namespace	blur3d.api.abstract.clipportion
#
#	\remarks	The AbstractTrackPortion class provides a base implementation of
#				a cross-application interface to a portion of a track.
#
#	\author		willc@blur.com
#	\author		Blur Studio
#	\date		10/15/15
#

from blur3d import abstractmethod
from blur3d import api

class AbstractTrackPortion(object):
	"""The AbstractTrackPortion class provides a base implementation of a
		cross-application interface to a portion of a track within a layer mixer.

	Attributes:
		end: The end of the region, in global frames.
		start: The start of the region, in global frames.
		track: The Track instance for the Track this TrackPortion corresponds to.
	"""

	def __init__(self, track, start, end):
		"""Initializes TrackPortion.

		Args:
			track(Track): The Track instance that this TrackPortion instance is
				a portion of.
			start(int): The start of the region, in global frames.
			end(int): The end of the region, in global frames.
		"""
		super(AbstractTrackPortion, self).__init__()
		self._track = track
		self._start = start
		self._end = end

	@property
	def end(self):
		"""The end of the region, in global frames."""
		return self._end
	@end.setter
	def end(self, value):
		self._end = value
	
	@property
	def start(self):
		"""The start of the region, in global frames."""
		return self._start
	@start.setter
	def start(self, value):
		self._start = value

	@property
	def track(self):
		"""The associated Track object."""
		return self._track
	@track.setter
	def track(self, value):
		self._track = value

################################################################################

# register the symbol
api.registerSymbol('TrackPortion', AbstractTrackPortion, ifNotFound=True)
