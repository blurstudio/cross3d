##
#	\namespace	cross3d.studiomax
#
#	\remarks	The cross3d.studiomax.TrackGroup module contains an
#				abstraction of the MAXScript MXTrackGroup class for interacting
#				with the Motion Mixer.
#	
#	\author		willc@blur.com
#	\author		Blur Studio
#	\date		09/28/15
#

import Py3dsMax
from Py3dsMax import mxs
from cross3d import Track
from cross3d.abstract.mixer.trackgroup import AbstractTrackGroup

################################################################################
#####------------------------------ Classes -------------------------------#####
################################################################################

class StudiomaxTrackGroup(AbstractTrackGroup):
	"""An abstraction of the MAXScript MxTrackGroup class.

	Attributes:
		trackGroup: The ValueWrapper for the MxTrackGroup this TrackGroup is
			wrapping.
		mixer: The Mixer instance for the MxTrackGroup's parent MxMixer.
		numTracks: The number of tracks in this TrackGroup.
	"""
	# This list of filters is taken from the MAX documentation at
	# http://docs.autodesk.com/3DSMAX/16/ENU/MAXScript-Help/files/GUID-10144917-5039-4F7D-8614-E7F9E5442653.htm
	FILTERS = [mxs.pyhelper.namify(f) for f in [
		'lftArm', 'rgtArm', 'lftHand', 'rgtHand', 'lftFoot', 'rgtFoot',
		'lftLeg', 'rgtLeg', 'lftPony', 'rgtPony', 'head', 'horizontal',
		'vertical', 'rotation','spine', 'pelvis', 'tail', 'prop1', 'prop2',
		'prop3'
	]]

	def getTrack(self, index):
		"""Returns a Track instance for the MxTrack at the specified index
			in the TrackGroup.

		Args:
						index(int): Index of desired track to retrieve.

		Returns:
						Track: The Track instance for the MxTrack at the
							specified index.

		Raises:
						IndexError
		"""
		trackCount = self.numTracks
		if index < 0 or index >= trackCount:
			raise IndexError('Index out of range')
		# We'll reverse the order we return Tracks in, since we want to iterate
		# from top to bottom.
		track = mxs.getTrack(self.trackGroup, trackCount-index)
		return Track(self, track)

	def iterTracks(self):
		"""Wraps the MAXScript getTrack global function into a generator that
			returns Track instances for each Track in the TrackGroup, from
			top to bottom.

		Returns:
						generator: Generator that produces Track instances.
		"""
		count = self.numTracks
		for i in range(count):
			yield self.getTrack(i)

	def tracks(self):
		"""Get a list of Track instance for each Track in this TrackGroup
			from top to bottom.

		Returns:
						list: List of Track instances for each Track in the
							TrackGroup from top to bottom.
		"""
		return [t for t in self.iterTracks()]

	def iterEnabledTracks(self):
		"""Wraps the MAXScript getTrack global function into a generator that
			returns Track instances for each enabled Track in the
			TrackGroup, from top to bottom.  This means that in the case that a
			Track is soloed, only that Track will be returned.  Otherwise, only
			non-muted tracks will be returned.

		Returns:
						generator: Generator that produces Track instances
							for enabled Tracks.
		"""
		if self.hasSoloedTrack:
			yield self.soloedTrack
		else:
			for track in self.iterTracks():
				if not track.isMuted:
					yield track

	def enabledTracks(self):
		"""Get a list of Track instance for each enabled Track in this
			TrackGroup from top to bottom.  This means that in the case that a
			Track is soloed, a list containing only that Track will be returned.
			Otherwise, only non-muted tracks will be returned.

		Returns:
						list: List of Track instances for each enabled Track
						in the TrackGroup from top to bottom.
		"""
		if self.hasSoloedTrack:
			return [self.soloedTrack]
		else:
			return [t for t in self.iterTracks() if not t.isMuted]

	@property
	def hasSoloedTrack(self):
		"""Returns a boolean indicating whether any track in this TrackGroup is
		soloed.
		"""
		# If we've already checked for a soloed track, it should be cached, so
		# we'll check that first, and otherwise iterate over the tracks, and
		# cache the soloed track for later.
		if self._hasSoloedTrack != None:
			return self._hasSoloedTrack
		for track in self.iterTracks():
			if track.isSoloed:
				self._soloedTrack = track
				self._hasSoloedTrack = True
				return True
		self._hasSoloedTrack = False
		return False

	@property
	def soloedTrack(self):
		"""The soloed track for this TrackGroup, or None if no tracks are
			soloed.
		"""
		if self.hasSoloedTrack():
			return self._soloedTrack
		else:
			return None

	def checkFilter(self, filterName, checkValidName=False):
		"""Tests whether a filter name is enabled for this TrackGroup.

		Args:
						filterName: string or Py3dsMax.ValueWrapper instance of
							the filter name to test for.
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
		# The filter needs to be a name, so if we were passed a string,
		# namify it.
		if isinstance(filterName, basestring):
			filterName = mxs.pyhelper.namify(filterName)
		# Ensure that we now have a ValueWrapper.
		if isinstance(filterName, Py3dsMax.ValueWrapper):
			# MAXScript's getFilter function throws a Runtime error when
			# passed a disabled filter, so we'll have to catch and ignore.
			# This means that if an invalid filter name is passed, this
			# method will return False, and not raise an exception, unless
			# we check for that explicitly.
			try:
				return mxs.getFilter(self.trackGroup, filterName)
			except RuntimeError as e:
				# If checkValidName is set, check to see if the filterName
				# is in our list of filter names.  Since ValueWrappers don't
				# compare properly for Names, we'll need to cast to strings
				# first.
				if checkValidName:
					if not str(filterName) in [str(f) for f in self.FILTERS]:
						raise ValueError(
							'filterName is not recognized as a valid Filter Name.'
						)
				if 'Runtime error: Improper filter type' in e.message:
					return False
				else:
					raise
		else:
			raise TypeError(
				'Expected string or ValueWrapper for filterName.  Received {}'.format(
					type(filterName)
				)
			)

	def iterFilters(self):
		"""Returns a generator that returns stringified names for each enabled
			filter on the TrackGroup.

		Returns:
						generator: Generator that produces a string for each
							enabled filter.
		"""
		for fil in self.FILTERS:
			if self.checkFilter(fil):
				yield str(fil)

	def filters(self):
		"""Returns a list of stringified names of enabled filter on the
			TrackGroup.

		Returns:
						list: A list of the string names of enabled filters.
		"""
		return [f for f in self.iterFilters()]

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
		ClipPortions = []
		for track in self.iterEnabledTracks():
			sc, occl = track.analyzeWeights(occludedPortions)
			occludedPortions.extend(occl)
			ClipPortions.extend(sc)

		return ClipPortions, occludedPortions

################################################################################

# register the symbol
import cross3d
cross3d.registerSymbol('TrackGroup', StudiomaxTrackGroup)
