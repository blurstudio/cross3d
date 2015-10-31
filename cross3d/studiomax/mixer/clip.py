##
#	\namespace	blur3d.api.studiomax
#
#	\remarks	The blur3d.api.studiomax.Clip module contains an
#				abstraction of the MAXScript MXClip class for interacting
#				with the Motion Mixer.
#	
#	\author		willc@blur.com
#	\author		Blur Studio
#	\date		09/28/15
#

import Py3dsMax
from Py3dsMax import mxs
from blur3d.api import ClipPortion, TrackPortion
from blur3d.api.abstract.mixer.clip import AbstractClip

################################################################################
#####------------------------------ Classes -------------------------------#####
################################################################################

class StudiomaxClip(AbstractClip):
	"""An abstraction of the MAXScript MxClip class.

	Attributes:
		clip: The ValueWrapper for the MxClip this Clip is wrapping.
		track: The Track instance for the MxClip's parent MxTrack.
		numWeights: The number of weights in the clip's weight curve
			(relevant only when clip is in a layer track)
		globStart: The global frame value for the start point of the MxClip
		globEnd: The global frame value for the end point of the MxClip
		filename: The filename of the bip file used by the MxClip.
		scale: The MxClip's scale. Modifying the scale will cause the Clip to
			scale on the right edge. The left edge will not move.
	"""
	
	@property
	def filename(self):
		"""The filename of the bip file used by the MxClip."""
		return self.clip.filename

	@property
	def globStart(self):
		"""The global frame value for the start point of the MxClip"""
		return float(self.clip.globStart)

	@property
	def globEnd(self):
		"""The global frame value for the end point of the MxClip"""
		return float(self.clip.globEnd)

	@property
	def numWeights(self):
		"""The number of weights in the clip's weight curve
			(relevant only when clip is in a layer track)"""
		return int(self.clip.numWeights)

	@property
	def sourceEnd(self):
		return float(self.clip.orgEnd)

	@property
	def sourceStart(self):
		return float(self.clip.orgStart)

	@property
	def scale(self):
		return float(self.clip.scale)

	@property
	def trimEnd(self):
		return float(self.clip.trimEnd)

	@property
	def trimStart(self):
		return float(self.clip.trimStart)

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
		if self.track.isTransitionTrack:
			# this won't work...
			return
		clipOcclPortions = []
		ClipPortions = []
		clipStart, clipEnd = self.globStart, self.globEnd
		if self.numWeights:
			usedPortions = []
			# Initialize the first rangeStart with the global start for the
			# clip.  We'll modify this if the weights make the clip have no
			# effect for part of its duration.
			rangeStart, rangeEnd = clipStart, None
			# Keep a seperate occluding clip range.  We'll keep track of
			# occluding clips so we can test against them to update clip ranges
			# later on.
			occlStart, occlEnd = None, None
			prevWVal = 0.0
			for wi, (wTime, wVal) in enumerate(self.iterWeights()):
				# Always move the end to the current position
				rangeEnd = wTime
				if wVal == 0.0:
					# If the usedPortion has a non-zero length and isn't
					# non-effecting for its entire duration, add it to the used
					# portions.
					if rangeEnd > rangeStart and prevWVal:
						usedPortions.append(
							TrackPortion(self.track, rangeStart, rangeEnd)
						)
					# Reset start to current position
					rangeStart = wTime
				if wVal == 1.0:
					# If this is the first weight, start at the beggining of the
					# clip, since the curve will extend back past this weight.
					if wi == 0:
						occlStart = clipStart
					# If we already have a start stored for an occluding
					# portion, store this weight as the (new) end.  Otherwise,
					# store it as the start.
					if occlStart:
						occlEnd = wTime
					else:
						occlStart = wTime
				else:
					# If a start and end are stored for the occluding
					# TrackPortion, add that TrackPortion to the list of
					# occluding portions for this clip.
					if occlStart and occlEnd:
						clipOcclPortions.append(
							TrackPortion(self.track, occlStart, occlEnd)
						)
					# Clear the occluding start/end, since the track weighting
					# is no longer fully occluding.
					occlStart, occlEnd = None, None
				prevWVal = wVal
			# If occlStart is set, add the remainder of the clip to occluding
			# clips.
			if occlStart:
				clipOcclPortions.append(
					TrackPortion(self.track, occlStart, clipEnd)
				)
			# If the clip ended with a non-zero weight, add the remainder as a
			# usedPortion.
			if wVal:
				usedPortions.append(
					TrackPortion(self.track, rangeStart, clipEnd)
				)
			# Finally, we'll clean up the list of ClipPortions by eliminating
			# occluded sections of clips, and condensing continuous clips that
			# were split where their weight dips tangential to zero.
			usedSC = self._occludeClipPortions(usedPortions, occludedPortions)
			ClipPortions = self._coalesceClipPortions(usedSC)
		else:
			clipRange = self.globStart, self.globEnd
			clipOcclPortions = [TrackPortion(self.track, *clipRange)]
			ClipPortions = self._occludeClipPortions(
				[ClipPortion(self, *clipRange)],
				occludedPortions
				)

		occludedPortions.extend(clipOcclPortions)
		return ClipPortions, occludedPortions

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
		if index < 0 or index >= self.numWeights:
			raise IndexError('Index out of range')
		# Adjust the weight time to be global, not local to the clip.
		return float(mxs.getWeightTime(self.clip, index+1)) + self.globStart

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
		return float(mxs.getWeight(self.clip, index+1))

	def iterWeights(self):
		"""Wraps the MAXScript getWeight and getWeightTime global functions into
			a generator that returns tuples of the time and value for all
			weights in the Track.

		Returns:
						generator: Generator that produces tuples of
							((float)time, (float)value) for weights on the
							track.
		"""
		count = self.numWeights
		for i in range(count):
			t = self.getWeightTime(i)
			v = self.getWeightValue(i)
			yield (t, v)

	def weights(self):
		"""Wraps the MAXScript getWeight and getWeightTime global functions into
			a generator that returns tuples of the time and value for all
			weights on the Clip.

		Returns:
						list: List of tuples for every weight on the Clip in
						the form ((float)time, (float)value).
		"""
		return [w for w in self.iterWeights()]

	def _coalesceClipPortions(self, inputPortions):
		ClipPortions = []
		clip = inputPortions.pop(0)
		scStart = clip.start
		scEnd = clip.end
		while len(inputPortions):
			clip = inputPortions.pop(0)
			if scEnd == clip.start:
				scEnd = clip.end
			else:
				ClipPortions.append(ClipPortion(self, scStart, scEnd))
				scStart, scEnd = clip.start, clip.end
		ClipPortions.append(ClipPortion(self, scStart, scEnd))
		return ClipPortions

	def _occludeClipPortions(self, ClipPortions, occludedPortions):
		outputClips = []
		while len(ClipPortions):
			sc = ClipPortions.pop(0)
			for ocR in occludedPortions:
				# if ClipPortion is completely occluded
				if (ocR.start < sc.start) and (sc.end < ocR.end):
					sc = None
					break
				containsOcclStart = (
					(sc.start < ocR.start) and (ocR.start < sc.end)
				)
				containsOcclEnd = ((sc.start < ocR.end) and (ocR.end < sc.end))
				if containsOcclStart and containsOcclEnd:
					ClipPortions.append(ClipPortion(self, sc.start, ocR.start))
					sc = ClipPortion(self, ocR.end, sc.end)
				elif containsOcclStart:
					sc = ClipPortion(self, sc.start, ocR.start)
				elif containsOcclEnd:
					sc = ClipPortion(self, ocR.end, sc.end)
			else:
				outputClips.append(sc)
		return outputClips

	def __str__(self):
		return 'Clip [{}]'.format(self.filename)

################################################################################

# register the symbol
from blur3d import api
api.registerSymbol('Clip', StudiomaxClip)
