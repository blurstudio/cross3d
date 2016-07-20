##
#	\namespace	cross3d.abstract.track
#
#	\remarks	The AbstractTrack class provides a base implementation of a
#				cross-application interface to a track.
#
#	\author		willc
#	\author		Blur Studio
#	\date		10/15/15
#

import cross3d
from cross3d import Clip, ClipPortion, TrackPortion, abstractmethod

class AbstractTrack(object):
	"""The AbstractClip class provides a base implementation of a
		cross-application interface to a track within a layer mixer.

	Attributes:
		track: The native accessor for the TRack object.
		trackGroup: The TrackGroup instance for the Track's parent TrackGroup.
		numClips: The number of Clips in this Track.
		isMuted: Whether this Track is Muted.
		isSoloed: Whether this Track is Soloed
		isLayerTrack: Whether this Track is a Layer Track
		isTransitionTrack: Whether this Track is a Transition Track
		numWeights: The number of weights in the tracks's weight curve
	"""
	def __init__(self, trackGroup, track):
		super(AbstractTrack, self).__init__()
		self._track = track
		self._trackGroup = trackGroup
		self._dirty = False

	@property
	def track(self):
		"""The native accessor for the Track object"""
		return self._track
	@track.setter
	def track(self, value):
		self._track = value

	@property
	def trackGroup(self):
		"""The TrackGroup instance for the TrackGroup this Track belongs to."""
		return self._trackGroup
	@trackGroup.setter
	def trackGroup(self, value):
		self._trackGroup = value

	@property
	def numClips(self):
		return None

	@property
	def isLayerTrack(self):
		"""Whether this track is a Layer Track"""
		return None

	@property
	def isTransitionTrack(self):
		"""Whether this track is a Transition Track"""
		return None

	@property
	def isMuted(self):
		"""Whether this track is Muted"""
		return None

	@property
	def isSoloed(self):
		"""Whether this track is Soloed"""
		return None

	@property
	def numWeights(self):
		"""Number of weights present on this track.  Will always be zero for
			non-transition tracks.
		"""
		return None

	@abstractmethod
	def getWeightValue(self, index):
		"""Retrieves the value of the weight at the specified index.

		Args:
						index(int): Index of desired weight to retrieve a value
							for.

		Returns:
						float: Value of the weight at the index specified.

		Raises:
						IndexError
		"""
		return None

	@abstractmethod
	def getWeightTime(self, index):
		"""Retrieves the global frame number the weight at the specified index
			is placed at.

		Args:
						index(int): Index of desired weight to retrieve a time
							for.

		Returns:
						float: Frame number for the position of the weight.

		Raises:
						IndexError
		"""
		return None

	@abstractmethod
	def iterWeights(self):
		"""Returns a generator that yields tuples of the time and value for all
			weights in the Track.

		Returns:
						generator: Generator that yields tuples of
							((float)time, (float)value) for weights on the
							track
		"""
		yield None

	@abstractmethod
	def weights(self):
		"""Returns a list of tuples of the time and value for all weights in the
			Track.

		Returns:
						list: List of tuples for every weight on the track in
						the form ((float)time, (float)value).
		"""
		return None

	@abstractmethod
	def getClip(self, index):
		"""Returns the Clip instance for the Clip at the specified index
			within this Track.

		Returns:
						Clip: Clip instance for the Clip at the
							specified index.
		"""
		return None

	@abstractmethod
	def iterClips(self):
		"""Returns a generator that yields each clip in the Track chronologically.

		Returns:
						generator: Generator that produces Clip instances
						for each Clip that appears in this Track.
		"""
		yield None

	@abstractmethod
	def clips(self):
		"""Get a list of Clip instance for each Clip in this track
			chronologically.

		Returns:
						list: List of Clip instances for each clip in the
							track in chronological order.
		"""
		return None

	@abstractmethod
	def analyzeWeights(self, occludedPortions):
		"""Determines which portions of Clips within the Track are used, and
			which portions of the track will occlude Tracks below.

		Args:
						occludedPortions(list): A list of `TrackPortion` instances
							for every portion of the Track that will be occluded
							by Tracks above it.

		Returns:
						tuple: A tuple containing a list of `ClipPortion`
							instances for every used portion of each Clip in the
							Track, and a list of `TrackPortion` instances for
							every occluding portion of the Track.
		"""
		return None
	
	@abstractmethod
	def analyzeTrackWeights(self, occludedPortions):
		"""Determines which portions of Clips within the Track are used, and
			which portions of the track will occlude Tracks below.

		Args:
						occludedPortions(list): A list of `TrackPortion` instances
							for every portion of the Track that will be occluded
							by Tracks above it.

		Returns:
						tuple: A tuple containing a list of `ClipPortion`
							instances for every used portion of each Clip in the
							Track, and a list of `TrackPortion` instances for
							every occluding portion of the Track.
		"""
		return None


################################################################################

# register the symbol
cross3d.registerSymbol('Track', AbstractTrack, ifNotFound=True)
