##
#	\namespace	blur3d.api.studiomax
#
#	\remarks	The blur3d.api.studiomax.Mixer module contains an
#				abstraction of the MAXScript MXMixer class for interacting with
#				the Motion Mixer.
#	
#	\author		willc@blur.com
#	\author		Blur Studio
#	\date		09/28/15
#

import Py3dsMax
from Py3dsMax import mxs
from blur3d.api import TrackGroup
from blur3d.api.abstract.mixer.mixer import AbstractMixer

# ==============================================================================
# Mixers are organized hierarchically with the reltionships as follows:
# 
#	Mixer
#	|
#	|-> Trackgroup
#		| * At this level, Filters are stored.  Filters dictate what parts of
#		| 	the rig are effected by the Tracks that are children of the
#		|	trackgroup.
#		|
#		|-> Track
#			| * At this level, the Transition tracks are differentiated from
#			|	Layer tracks
#			| 		* Transition tracks have a global "weight" curve, while
#			|			layer tracks store weights per clip
#			| 		* Overlaps on Transition tracks need to be treated as
#			|			overlaps always
#			| 		* Overlaps between tracks need to be evaluated based on
#			|			track weight to determine overlap
#			| * Also at this level, Track "mute" or "solo" status is stored.
#			| 		* Soloing a track operates globally within the mixer
#			|			(across trackgroups)
#			| 		* Muted tracks can be ignored for our purposes.
#			|
#			|-> Clip
#				| * Weights are stored for clips on Layer tracks.
#				| * The in/out of clips is stored at this level
#				| * The Speed (scale) of clips is stored at this level
#				| * The start time within the shot is stored at this level
#
# ==============================================================================


################################################################################
#####------------------------------ Classes -------------------------------#####
################################################################################

class StudiomaxMixer(AbstractMixer):
	"""An abstraction of the MAXScript MxMixer class.

	Attributes:
		mixer: The ValueWrapper for the MxMixer this Mixer is wrapping.
		numTrackGroups: The number of TrackGroups present in this Mixer.
	"""

	@property
	def numTrackGroups(self):
		"""The number of TrackGroups this Mixer contains. """
		return self._mixer.numTrackGroups

	def getTrackGroup(self, index):
		"""Retrieves the TrackGroup for the TrackGroupt at the specified
			index.

		Args:
						index(int): Index of desired TrackGroup to retrieve.

		Returns:
						TrackGroup: TrackGroup instance for the
							TrackGroup at the specified index.

		Raises:
						IndexError
		"""
		tgCount = self.numTrackGroups
		if index < 0 or index >= tgCount:
			raise IndexError('Index out of range')
		# We'll reverse the order we return TrackGroups in, since we want to
		# iterate from top to bottom.
		trackGroup = mxs.getTrackGroup(self.mixer, tgCount-index)
		return TrackGroup(self, trackGroup)

	def iterTrackGroups(self):
		"""Wraps the MAXScript getTrackGroup global function into a generator
			that returns TrackGroup instances for each TrackGroup in the
			Mixer, from top to bottom.

		Returns:
						generator: Generator that produces TrackGroup
							instances.
		"""
		count = self.numTrackGroups
		for i in range(count):
			yield self.getTrackGroup(i)

	def trackGroups(self):
		"""Returns a list of TrackGroup instances for every TrackGroup in
			the Mixer, ordered from top to bottom.

		Returns:
						list: A list of TrackGroup instances.
		"""
		return [tg for tg in self.iterTrackGroups()]

	def getClipPortions(self):
		"""Analyzes the weights for all tracks in all TrackGroups in the Mixer,
			and compares the filters on each track group in order to generate a
			list of ClipPortion instance for every used section of every clip on an
			enabled Track.

		Returns:
						list: A list of ClipPortion instances for each used portion
							of a Clip.
		"""
		ClipPortions = []
		analyzedTrackGroups = []
		for i, tg in enumerate(self.iterTrackGroups()):
			tgInfo = {}
			filters = set(tg.filters())
			tgInfo['filters'] = filters
			occludedPortions = []
			# For every trackgroup above this one whose filters are a superset
			# of this track's filters, any clips that occlude in that trackgroup
			# will also occlude in this one.
			for atg in analyzedTrackGroups:
				if atg['filters'].issuperset(filters):
					occludedPortions.extend(atg['occludedPortions'])
			sc, occl = tg.getClipPortions(occludedPortions=occludedPortions)
			tgInfo['occludedPortions'] = occl
			tgInfo['i'] = i
			ClipPortions.extend(sc)
			analyzedTrackGroups.append(tgInfo)
		return ClipPortions

################################################################################

# register the symbol
from blur3d import api
api.registerSymbol('Mixer', StudiomaxMixer)
