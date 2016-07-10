##
#	\namespace	cross3d.abstract.trackgroup
#
#	\remarks	The AbstractTrackGroup class provides a base implementation of a
#				cross-application interface to a layer trackgroup.
#
#	\author		willc@blur.com
#	\author		Blur Studio
#	\date		10/13/15
#

import cross3d
from cross3d import Track, abstractmethod

class AbstractTrackGroup(object):
	"""The AbstractTrackGroup class provides a base implementation of a
		cross-application interface to a trackgroup within a layer mixer.

	Attributes:
		trackGroup: The native accessor for the TrackGroup object.
		mixer: The Mixer object this TrackGroup is a part of.
		numTracks: The number of tracks in this TrackGroup.
	"""
	def __init__(self, mixer, trackGroup):
		super(AbstractTrackGroup, self).__init__()
		self._trackGroup = trackGroup
		self._mixer = mixer
		self._hasSoloedTrack = None

	@property
	def trackGroup(self):
		"""The native accessor for the TrackGroup object"""
		return self._trackGroup
	@trackGroup.setter
	def trackGroup(self, value):
		self._trackGroup = value

	@property
	def mixer(self):
		"""The Mixer instance for the TrackGroup's parent Mixer."""
		return self._mixer
	@mixer.setter
	def mixer(self, value):
		self._mixer = value

	@property
	def numTracks(self):
		"""The number of tracks contained in this TrackGroup."""
		return self.trackGroup.numTracks

	@abstractmethod
	def getTrack(self, index):
		""" Returns a Track instance for the Track at the specified index
			in the TrackGroup.

		Args:
						index(int): Index of desired track to retrieve.

		Returns:
						Track: The Track instance for the Track at the
							specified index.

		Raises:
						IndexError
		"""
		return None

	@abstractmethod
	def iterTracks(self):
		""" Returns a generator that yields Track instances for each Track in
			the TrackGroup, from top to bottom.

		Returns:
						generator: Generator that yields Track instances.
		"""
		yield None

	@abstractmethod
	def tracks(self):
		"""Get a list of Track instance for each Track in this TrackGroup
			from top to bottom.

		Returns:
						list: List of Track instances for each Track in the
							TrackGroup from top to bottom.
		"""
		return None

	@abstractmethod
	def iterEnabledTracks(self):
		""" Returns a generator that yields Track instances for each enabled
			Track in the TrackGroup, from top to bottom.  This means that in the
			case that a Track is soloed, only that Track will be returned.
			Otherwise, only non-muted tracks will be returned.

		Returns:
						generator: Generator that produces Track instances
							for enabled Tracks.
		"""
		yield None

	@abstractmethod
	def enabledTracks(self):
		"""Get a list of Track instance for each enabled Track in this
			TrackGroup from top to bottom.  This means that in the case that a
			Track is soloed, a list containing only that Track will be returned.
			Otherwise, only non-muted tracks will be returned.

		Returns:
						list: List of Track instances for each enabled Track
						in the TrackGroup from top to bottom.
		"""
		return None

	@property
	def hasSoloedTrack(self):
		"""Returns a boolean indicating whether any track in this TrackGroup is
		soloed.
		"""
		# If we've already checked for a soloed track, it should be cached, so
		# we'll check that first, and otherwise iterate over the tracks, and
		# cache the soloed track for later.
		return None

	@property
	def soloedTrack(self):
		"""The soloed track for this TrackGroup, or None if no tracks are
			soloed.
		"""
		return None

	@abstractmethod
	def checkFilter(self, filterName, checkValidName=False):
		"""Tests whether a filter name is enabled for this TrackGroup.

		Args:
						filterName: string of the filter name to test for.
						checkValidName(bool): If True, will test whether the
							provided name is in the list of valid filter names
							before comparing, and if it is not a ValueError will
							be raised.  If False, checkFilter will return False
							if the name is not valid (or if it is valid and
							disabled.)

		Returns:
						bool: Whether the specified filter name is enabled for
							this TrackGroup.

		Raises:
						TypeError
						ValueError
		"""
		return None

	@abstractmethod
	def iterFilters(self):
		"""Returns a generator that returns string names for each enabled
			filter on the TrackGroup.

		Returns:
						generator: Generator that yields a string for each
							enabled filter.
		"""
		yield None

	@abstractmethod
	def filters(self):
		"""Returns a list of stringified names of enabled filters on the
			TrackGroup.

		Returns:
						list: A list of the string names of enabled filters.
		"""
		return None

	@abstractmethod
	def getClipPortions(self, occludedPortions=[]):
		"""Analyzes the weights for all tracks in the TrackGroup and returns a
			tuple of two lists, a list of ClipPortion instance for every used
			section of clips within the TrackGroup, and a list of TrackPortion
			instances for every occluding portion in the TrackGroup.

		Returns:
						tuple: A tuple containing a list of ClipPortion instances
							for each used portion of a Clip in any enabled Track
							in the TrackGroup, and a list of TrackPortion
							instances for each portion of fully occluding Clip in
							any enabled Track in the TrackGroup.
		"""
		return None


# register the symbol
cross3d.registerSymbol('TrackGroup', AbstractTrackGroup, ifNotFound=True)
