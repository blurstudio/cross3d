##
#	\namespace	blur3d.api.abstract.mixer
#
#	\remarks	The AbstractMixer class provides a base implementation of a
#				cross-application interface to a layer mixer.
#
#	\author		willc@blur.com
#	\author		Blur Studio
#	\date		10/13/15
#

from blur3d import abstractmethod
from blur3d import api
from blur3d.api import TrackGroup

class AbstractMixer(object):
	"""The AbstractMixer class provides a base implementation of a
		cross-application interface to a layer mixer.

	Attributes:
		mixer: The native accessor for the Mixer object.
		numTrackGroups: The number of TrackGroups present in this Mixer.
	"""
	def __init__(self, mixer):
		super(AbstractMixer, self).__init__()
		self._mixer = mixer

	@property
	def mixer(self):
		"""The native accessor for the Mixer object."""
		return self._mixer
	@mixer.setter
	def mixer(self, value):
		self._mixer = value

	@property
	def numTrackGroups(self):
		"""The number of TrackGroups this Mixer contains. """
		return None

	@abstractmethod
	def getTrackGroup(self, index):
		"""Retrieves the TrackGroup for the TrackGroup at the specified
			index.

		Args:
						index(int): Index of desired TrackGroup to retrieve.

		Returns:
						TrackGroup: TrackGroup instance for the
							TrackGroup at the specified index.

		Raises:
						IndexError
		"""
		return None

	@abstractmethod
	def iterTrackGroups(self):
		"""Wraps the MAXScript getTrackGroup global function into a generator
			that returns TrackGroup instances for each TrackGroup in the
			Mixer, from top to bottom.

		Returns:
						generator: Generator that produces TrackGroup
							instances.
		"""
		yield None

	@abstractmethod
	def trackGroups(self):
		"""Returns a list of TrackGroup instances for every TrackGroup in
			the Mixer, ordered from top to bottom.

		Returns:
						list: A list of TrackGroup instances.
		"""
		return None

	@abstractmethod
	def getClipPortions(self):
		"""Analyzes the weights for all tracks in all TrackGroups in the Mixer,
			and compares the filters on each track group in order to generate a
			list of ClipPortion instance for every used section of every clip on an
			enabled Track.

		Returns:
						list: A list of ClipPortion instances for each used portion
							of a Clip.
		"""
		return None


# register the symbol
api.registerSymbol('Mixer', AbstractMixer, ifNotFound=True)
