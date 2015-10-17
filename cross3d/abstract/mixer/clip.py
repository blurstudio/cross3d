##
#	\namespace	blur3d.api.abstract.clip
#
#	\remarks	The AbstractClip class provides a base implementation of a
#				cross-application interface to a clip.
#
#	\author		willc@blur.com
#	\author		Blur Studio
#	\date		10/15/15
#

from blur3d import abstractmethod
from blur3d import api
from blur3d.api import ClipPortion, TrackPortion

class AbstractClip(object):
	"""The AbstractClip class provides a base implementation of a
		cross-application interface to a clip within a layer mixer.

	Attributes:
		clip: The native accessor for the Clip object.
		track: The Track instance for the Clip's parent Track.
		numWeights: The number of weights in the clip's weight curve
			(relevant only when clip is in a layer track)
		globStart: The global frame value for the start point of the Clip
		globEnd: The global frame value for the end point of the Clip
		filename: The filename of the bip file used by the Clip.
		scale: The Clip's scale. Modifying the scale will cause the Clip to
			scale on the right edge. The left edge will not move.
	"""
	def __init__(self, track, clip):
		super(AbstractClip, self).__init__()
		self._track = track
		self._clip = clip

	@property
	def clip(self):
		"""The native accessor for the Clip object"""
		return self._clip
	@clip.setter
	def clip(self, value):
		self._clip = value

	@property
	def filename(self):
		""" The filename of the file used by the Clip. """
		return None

	@property
	def globStart(self):
		""" The global frame value for the start point of the Clip """
		return None

	@property
	def globEnd(self):
		""" The global frame value for the end point of the Clip """
		return None

	@property
	def numWeights(self):
		"""The number of weights in the clip's weight curve
			(relevant only when clip is in a layer track)"""
		return None

	@property
	def orgStart(self):
		return None

	@property
	def orgEnd(self):
		return None

	@property
	def scale(self):
		return None

	@property
	def track(self):
		"""The Track instance for the Clip's parent Track."""
		return self._track
	@track.setter
	def track(self, value):
		self._track = value

	@property
	def trimStart(self):
		return float(self.clip.trimStart)

	@property
	def trimEnd(self):
		return float(self.clip.trimEnd)

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
						float: Global frame number for the position of the
							weight.

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
							track.
		"""
		yield None

	@abstractmethod
	def weights(self):
		"""Returns a list of tuples of the time and value for all weights on the
			Clip.

		Returns:
						list: List of tuples for every weight on the Clip in
						the form ((float)time, (float)value).
		"""
		return None

	@abstractmethod
	def analyzeWeights(self, occludedPortions):
		"""Determines which portions of the Clip are used, and which portions of
			the Clip will occlude Tracks below.

		Args:
						occludedPortions(list): A list of `TrackPortion` instances
							for every portion of the Clip that will be occluded
							by Tracks above it.

		Returns:
						tuple: A tuple containing a list of `ClipPortion`
							instances for every used portion of the Clip, and a
							list of `TrackPortion` instances for every portion of
							the Clip that will occlude tracks below it.
		"""
		return None

################################################################################

# register the symbol
api.registerSymbol('Clip', AbstractClip, ifNotFound=True)
