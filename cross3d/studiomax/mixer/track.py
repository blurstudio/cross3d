##
#	\namespace	blur3d.api.studiomax
#
#	\remarks	The blur3d.api.studiomax.Track module contains an
#				abstraction of the MAXScript MXTrack class for interacting
#				with the Motion Mixer.
#	
#	\author		willc@blur.com
#	\author		Blur Studio
#	\date		09/28/15
#

import Py3dsMax
from Py3dsMax import mxs
from blur3d.api import Clip, ClipPortion, TrackPortion
from blur3d.api.abstract.mixer.track import AbstractTrack

################################################################################
#####------------------------------ Classes -------------------------------#####
################################################################################

class StudiomaxTrack(AbstractTrack):
	"""An abstraction of the MAXScript MxTrack class.

	Attributes:
		track: The ValueWrapper for the MxTrack this Track is wrapping.
		trackGroup: The TrackGroup instance for the MxTrack's parent
			MxTrackGroup.
		numClips: The number of Clips in this Track.
		isMuted: Whether this Track is Muted.
		isSoloed: Whether this Track is Soloed
		isLayerTrack: Whether this Track is a Layer Track
		isTransitionTrack: Whether this Track is a Transition Track
		numWeights: The number of weights in the tracks's weight curve
			(relevant only when the track is a transition track)
	"""
	
	@property
	def numClips(self):
		if self.isLayerTrack:
			return int(self.track.numClips)
		elif self.isTransitionTrack:
			return int(self.track.numTransClips)

	@property
	def isLayerTrack(self):
		"""Whether this track is a Layer Track"""
		return self.track.trackType == mxs.pyhelper.namify('layertrack')

	@property
	def isTransitionTrack(self):
		"""Whether this track is a Transition Track"""
		return self.track.trackType == mxs.pyhelper.namify('transtrack')

	@property
	def isMuted(self):
		"""Whether this track is Muted"""
		return self.track.mute

	@property
	def isSoloed(self):
		"""Whether this track is Soloed"""
		return self.track.solo

	@property
	def numWeights(self):
		"""Number of weights present on this track.  Will always be zero for
			non-transition tracks.
		"""
		return int(self.track.numWeights)

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
		if index < 0 or index >= self.numWeights:
			raise IndexError('Index out of range')
		return float(mxs.getWeight(self.track, index+1))

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
		if index < 0 or index >= self.numWeights:
			raise IndexError('Index out of range')
		return float(mxs.getWeightTime(self.track, index+1))

	def iterWeights(self):
		"""Wraps the MAXScript getWeight and getWeightTime global functions into
			a generator that returns tuples of the time and value for all
			weights in the Track.

		Returns:
						generator: Generator that produces tuples of
							((float)time, (float)value) for weights on the
							track
		"""
		count = self.numWeights
		for i in range(count):
			# adjust the weight time to be global, not local to the clip.
			t = self.getWeightTime(i)
			v = self.getWeightValue(i)
			yield (t, v)

	def weights(self):
		"""Wraps the MAXScript getWeight and getWeightTime global functions into
			a generator that returns tuples of the time and value for all
			weights in the Track.

		Returns:
						list: List of tuples for every weight on the track in
						the form ((float)time, (float)value).
		"""
		return [w for w in self.iterWeights()]

	def getClip(self, index):
		"""Returns the Clip instance for the Clip at the specified index
			within this Track.

		Returns:
						Clip: Clip instance for the Clip at the
							specified index.
		"""
		clip = mxs.getClip(self.track, index+1)
		return Clip(self, clip)

	def iterClips(self):
		"""Wraps the MAXScript getClip global function into a generator that
		returns each clip in the Track chronologically.

		Returns:
						generator: Generator that produces Clip instances
						for each Clip that appears in this Track.
		"""
		count = self.numClips
		for i in range(count):
			yield self.getClip(i)

	def clips(self):
		"""Get a list of Clip instance for each Clip in this track
			chronologically.

		Returns:
						list: List of Clip instances for each clip in the
							track in chronological order.
		"""
		return [c for c in self.iterClips()]

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
		ClipPortions = []
		if self.isLayerTrack:
			for clip in self.iterClips():
				sc, occl = clip.analyzeWeights(occludedPortions)
				occludedPortions = occl
				ClipPortions.extend(sc)
		elif self.isTransitionTrack:
			return self.analyzeTrackWeights(occludedPortions)
		return ClipPortions, occludedPortions
	
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
		if not len(self.clips()):
			# If track is empty, return two empty lists (we're not occulding or
			# using any ClipPortions.)
			return ([], [])
		trackStart = self.getClip(0).globStart
		trackEnd = self.getClip(self.numClips - 1).globEnd
		trackOcclPortions = []
		usedPortions = []
		if self.numWeights:
			# Get start / end from first and last clip in the track -- this will
			# give us the maximum range to analyze the track for.
			# Initialize the first rangeStart with the global start for the
			# clip.  We'll modify this if the weights make the clip have no
			# effect for part of its duration.
			rangeStart, rangeEnd = trackStart, None
			# Keep a seperate occluding range.  We'll keep track of occluding
			# areas so we can test against them to update clip/track ranges
			# later on.
			occlStart, occlEnd = None, None
			# initialize weight Value to 1.0, since if no weights are present
			# the track defaults to a weight of 1.0.
			wVal = 1.0
			prevWVal = 0.0
			for wi, (wTime, wVal) in enumerate(self.iterWeights()):
				# Always move the end to the current position
				rangeEnd = wTime
				if wVal == 0.0:
					# If the usedPortion has a non-zero length and isn't
					# non-effecting for its entire duration, add it to the
					# used portions.
					if rangeEnd > rangeStart and prevWVal:
						usedPortions.append(
							TrackPortion(self, rangeStart, rangeEnd)
						)
					# Reset start to current position
					rangeStart = wTime
				if wVal == 1.0:
					# If this is the first weight, start at the beggining of the
					# first clip in the track, since the curve will extend back
					# past this weight.
					if wi == 0:
						occlStart = trackStart
					# If we already have a start stored for an occluding
					# portion, store the current time as the occluding portion's
					# end.
					if occlStart:
						occlEnd = wTime
					else:
						occlStart = wTime
				else:
					# If a start and end are stored for the occluding
					# TrackPortion, add that TrackPortion to the list of occluding
					# portions for this clip.
					if occlStart and occlEnd:
						trackOcclPortions.append(
							TrackPortion(self, occlStart, occlEnd)
						)
					# Clear the occluding start/end, since the track weighting
					# is no longer fully occluding.
					occlStart, occlEnd = None, None
				prevWVal = wVal
			# If occlStart is set, add the remainder of the clip to occluding
			# clips.
			if occlStart:
				trackOcclPortions.append(
					TrackPortion(self, occlStart, trackEnd)
				)
			# If the clip ended with a non-zero weight, add the remainder as a
			# usedPortion.
			if wVal:
				usedPortions.append(
					TrackPortion(self, rangeStart, trackEnd)
				)
		else:
			# If there are no weights, we can assume that the entire track will
			# be used.
			usedPortions = [TrackPortion(self, trackStart, trackEnd)]	
		# Finally, we'll clean up the list of ClipPortions by eliminating occluded
		# sections of clips, and condensing continuous clips that were split
		# where their weight dips tangential to zero.
		usedTR = self._occludeTrackPortions(usedPortions, occludedPortions)
		ClipPortions = self._findClipPortions(usedTR)
		occludedPortions.extend(trackOcclPortions)
		return ClipPortions, occludedPortions

	def _occludeTrackPortions(self, usedPortions, occludedPortions):
		outputPortions = []
		while len(usedPortions):
			tr = usedPortions.pop(0)
			for ocR in occludedPortions:
				# If TrackPortion is completely occluded
				if (ocR.start < tr.start) and (tr.end < ocR.end):
					tr = None
					break
				containsOcclStart = ((tr.start < ocR.start) and (ocR.start < tr.end))
				containsOcclEnd = ((tr.start < ocR.end) and (ocR.end < tr.end))
				if containsOcclStart and containsOcclEnd:
					outputPortions.append(
						TrackPortion(self, tr.start, ocR.start)
					)
					tr = TrackPortion(self, ocR.end, tr.end)
				elif containsOcclStart:
					tr = TrackPortion(self, tr.start, ocR.start)
				elif containsOcclEnd:
					tr = TrackPortion(self, ocR.end, tr.end)
			else:
				outputPortions.append(tr)
		return outputPortions

	def _findClipPortions(self, usedTrackPortions):
		clipPortions = []
		for clip in self.iterClips():
			currClipPortions = []
			for tr in usedTrackPortions:
				start = max(clip.globStart, tr.start)
				end = min(clip.globEnd, tr.end)
				if end > start:
					currClipPortions.append(ClipPortion(clip, start, end))
			# Coalesce ClipPortions for this clip before appending to the output
			clipPortions.extend(self._coalesceClipPortions(currClipPortions))
		return clipPortions

	def _coalesceClipPortions(self, inputPortions):
		ClipPortions = []
		portion = inputPortions.pop(0)
		scStart = portion.start
		scEnd = portion.end
		while len(inputPortions):
			portion = inputPortions.pop(0)
			if scEnd == portion.start:
				scEnd = portion.end
			else:
				ClipPortions.append(ClipPortion(portion.clip, scStart, scEnd))
				scStart, scEnd = portion.start, portion.end
		ClipPortions.append(ClipPortion(portion.clip, scStart, scEnd))
		return ClipPortions

################################################################################

# register the symbol
from blur3d import api
api.registerSymbol('Track', StudiomaxTrack)
