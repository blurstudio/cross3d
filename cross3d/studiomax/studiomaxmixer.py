##
#	\namespace	blur3d.api.studiomax
#
#	\remarks	The blur3d.api.studiomax.studiomaxmixer module contains
#				abstractions of MAXScript classes for interacting with the
#				Motion Mixer.
#	
#	\author		willc@blur.com
#	\author		Blur Studio
#	\date		09/28/15
#

import Py3dsMax
from Py3dsMax import mxs

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

class TrackRegion(object):
	"""A region within a TrackInfo.

	Attributes:
		end: The end of the region, in global frames.
		start: The start of the region, in global frames.
	"""
	def __init__(self, start, end):
		"""Initializes TrackRegion.

		Args:
			start(int): The start of the region, in global frames.
			end(int): The end of the region, in global frames.
		"""
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

	def __str__(self):
		return '{}-{}'.format(self.start, self.end)

################################################################################

class SubClip(TrackRegion):
	"""A portion of a ClipInfo.

	Attributes:
		end: The end of the region, in global frames.
		start: The start of the region, in global frames.
		clip: The ClipInfo of which this SubClip is a portion.
	"""
	def __init__(self, clip, start, end):
		"""Initializes TrackRegion.

		Args:
			clip(ClipInfo): The clip that this SubClip is a portion of.
			start(int): The start of the region, in global frames.
			end(int): The end of the region, in global frames.
		"""
		self._start = start
		self._end = end
		self._clip = clip

	@classmethod
	def fromTrackRegion(cls, tr, clip):
		"""Initializes a SubClip instance from a TrackRegion and ClipInfo."""
		return cls(clip, tr.start, tr.end)

	@property
	def clip(self):
		"""The associated ClipInfo."""
		return self._clip
	@clip.setter
	def clip(self, value):
		self._clip = value

################################################################################

class ClipInfo(object):
	"""An abstraction of the MAXScript MxClip class.

	Attributes:
		clip: The ValueWrapper for the MxClip this ClipInfo is wrapping.
		track: The TrackInfo instance for the MxClip's parent MxTrack.
		numWeights: The number of weights in the clip's weight curve
			(relevant only when clip is in a layer track)
		globStart: The global frame value for the start point of the MxClip
		globEnd: The global frame value for the end point of the MxClip
		filename: The filename of the bip file used by the MxClip.
		scale: The MxClip's scale. Modifying the scale will cause the Clip to
			scale on the right edge. The left edge will not move.
	"""
	def __init__(self, track, clip):
		self._track = track
		self._clip = clip
		self._dirty = False

	@property
	def clip(self):
		"""The ValueWrapper instance for the MxClip"""
		return self._clip
	@clip.setter
	def clip(self, value):
		self._clip = value

	@property
	def track(self):
		"""The TrackInfo instance for the MxClip's parent MxTrack."""
		return self._track
	@track.setter
	def track(self, value):
		self._track = value

	@property
	def numWeights(self):
		"""The number of weights in the clip's weight curve
			(relevant only when clip is in a layer track)"""
		return int(self.clip.numWeights)

	@property
	def globStart(self):
		"""The global frame value for the start point of the MxClip"""
		return float(self.clip.globStart)

	@property
	def globEnd(self):
		"""The global frame value for the end point of the MxClip"""
		return float(self.clip.globEnd)

	@property
	def filename(self):
		"""The filename of the bip file used by the MxClip."""
		return None
		## TODO ##

	@property
	def scale(self):
		## TODO ##
		return None
	@scale.setter
	def scale(self, value):
		## TODO ##
		return

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

	def analyzeWeights(self, occludedRegions):
		"""Determines which portions of the Clip are used, and which portions of
			the Clip will occlude Tracks below.

		Args:
						occludedRegions(list): A list of `TrackRegion` instances
							for every portion of the Clip that will be occluded
							by Tracks above it.

		Returns:
						tuple: A tuple containing a list of `SubClip`
							instances for every used portion of the Clip, and a
							list of `TrackRegion` instances for every portion of
							the Clip that will occlude tracks below it.
		"""
		if self.track.isTransitionTrack:
			# this won't work...
			return
		clipOcclRegions = []
		subClips = []
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
						usedPortions.append(TrackRegion(rangeStart, rangeEnd))
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
					# TrackRegion, add that TrackRegion to the list of occluding
					# regions for this clip.
					if occlStart and occlEnd:
						clipOcclRegions.append(TrackRegion(occlStart, occlEnd))
					# Clear the occluding start/end, since the track weighting
					# is no longer fully occluding.
					occlStart, occlEnd = None, None
				prevWVal = wVal
			# If occlStart is set, add the remainder of the clip to occluding
			# clips.
			if occlStart:
				clipOcclRegions.append(TrackRegion(occlStart, clipEnd))
			# If the clip ended with a non-zero weight, add the remainder as a
			# usedPortion.
			if wVal:
				usedPortions.append(TrackRegion(rangeStart, clipEnd))
			# Finally, we'll clean up the list of subclips by eliminating
			# occluded sections of clips, and condensing continuous clips that
			# were split where their weight dips tangential to zero.
			usedSC = self._occludeSubClips(usedPortions, occludedRegions)
			subClips = self._coalesceSubClips(usedSC)
		else:
			clipRange = self.globStart, self.globEnd
			clipOcclRegions = [TrackRegion(*clipRange)]
			subClips = self._occludeSubClips(
				[SubClip(self, *clipRange)],
				occludedRegions
				)

		occludedRegions.extend(clipOcclRegions)
		return subClips, occludedRegions

	def _occludeSubClips(self, subClips, occludedRegions):
		outputClips = []
		while len(subClips):
			sc = subClips.pop(0)
			for ocR in occludedRegions:
				# if subClip is completely occluded
				if (ocR.start < sc.start) and (sc.end < ocR.end):
					sc = None
					break
				containsOcclStart = (
					(sc.start < ocR.start) and (ocR.start < sc.end)
				)
				containsOcclEnd = ((sc.start < ocR.end) and (ocR.end < sc.end))
				if containsOcclStart and containsOcclEnd:
					subClips.append(SubClip(self, sc.start, ocR.start))
					sc = SubClip(self, ocR.end, sc.end)
				elif containsOcclStart:
					sc = SubClip(self, sc.start, ocR.start)
				elif containsOcclEnd:
					sc = SubClip(self, ocR.end, sc.end)
			else:
				outputClips.append(sc)
		return outputClips

	def _coalesceSubClips(self, inputRegions):
		subClips = []
		clip = inputRegions.pop(0)
		scStart = clip.start
		scEnd = clip.end
		while len(inputRegions):
			clip = inputRegions.pop(0)
			if scEnd == clip.start:
				scEnd = clip.end
			else:
				subClips.append(SubClip(self, scStart, scEnd))
				scStart, scEnd = clip.start, clip.end
		subClips.append(SubClip(self, scStart, scEnd))
		return subClips

################################################################################

class TrackInfo(object):
	"""An abstraction of the MAXScript MxTrack class.

	Attributes:
		track: The ValueWrapper for the MxTrack this TrackInfo is wrapping.
		trackGroup: The TrackGroupInfo instance for the MxTrack's parent
			MxTrackGroup.
		numClips: The number of Clips in this Track.
		isMuted: Whether this Track is Muted.
		isSoloed: Whether this Track is Soloed
		isLayerTrack: Whether this Track is a Layer Track
		isTransitionTrack: Whether this Track is a Transition Track
		numWeights: The number of weights in the tracks's weight curve
			(relevant only when the track is a transition track)
	"""
	def __init__(self, trackGroup, track):
		self._track = track
		self._trackGroup = trackGroup
		self._dirty = False

	@property
	def track(self):
		"""The ValueWrapper instance for the MxTrack"""
		return self._track
	@track.setter
	def track(self, value):
		self._track = value

	@property
	def trackGroup(self):
		"""The TrackGroupInfo instance for the MxTrackGroup this Track belongs
			to.
		"""
		return self._trackGroup
	@trackGroup.setter
	def trackGroup(self, value):
		self._trackGroup = value

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
		"""Returns the ClipInfo instance for the Clip at the specified index
			within this Track.

		Returns:
						ClipInfo: ClipInfo instance for the Clip at the
							specified index.
		"""
		clip = mxs.getClip(self.track, index+1)
		return ClipInfo(self, clip)

	def iterClips(self):
		"""Wraps the MAXScript getClip global function into a generator that
		returns each clip in the Track chronologically.

		Returns:
						generator: Generator that produces ClipInfo instances
						for each Clip that appears in this Track.
		"""
		count = self.numClips
		for i in range(count):
			yield self.getClip(i)

	def clips(self):
		"""Get a list of ClipInfo instance for each Clip in this track
			chronologically.

		Returns:
						list: List of ClipInfo instances for each clip in the
							track in chronological order.
		"""
		return [c for c in self.iterClips()]

	def analyzeWeights(self, occludedRegions):
		"""Determines which portions of Clips within the Track are used, and
			which portions of the track will occlude Tracks below.

		Args:
						occludedRegions(list): A list of `TrackRegion` instances
							for every portion of the Track that will be occluded
							by Tracks above it.

		Returns:
						tuple: A tuple containing a list of `SubClip`
							instances for every used portion of each Clip in the
							Track, and a list of `TrackRegion` instances for
							every occluding portion of the Track.
		"""
		subClips = []
		if self.isLayerTrack:
			for clip in self.iterClips():
				sc, occl = clip.analyzeWeights(occludedRegions)
				occludedRegions = occl
				subClips.extend(sc)
		elif self.isTransitionTrack:
			return self.analyzeTrackWeights(occludedRegions)
		return subClips, occludedRegions
	
	def analyzeTrackWeights(self, occludedRegions):
		"""Determines which portions of Clips within the Track are used, and
			which portions of the track will occlude Tracks below.

		Args:
						occludedRegions(list): A list of `TrackRegion` instances
							for every portion of the Track that will be occluded
							by Tracks above it.

		Returns:
						tuple: A tuple containing a list of `SubClip`
							instances for every used portion of each Clip in the
							Track, and a list of `TrackRegion` instances for
							every occluding portion of the Track.
		"""
		trackStart = self.getClip(0).globStart
		trackEnd = self.getClip(self.numClips - 1).globEnd
		trackOcclRegions = []
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
			prevWVal = 0.0
			for (wTime, wVal) in self.iterWeights():
				# Always move the end to the current position
				rangeEnd = wTime
				if wVal == 0.0:
					# If the usedPortion has a non-zero length and isn't
					# non-effecting for its entire duration, add it to the
					# used portions.
					if rangeEnd > rangeStart and prevWVal:
						usedPortions.append(TrackRegion(rangeStart, rangeEnd))
					# Reset start to current position
					rangeStart = wTime
				if wVal == 1.0:
					# If this is the first weight, start at the beggining of the
					# clip, since the curve will extend back past this weight.
					if wi == 0:
						occlStart = trac
					# If we already have a start stored for an occluding
					# portion, store the current time as the occluding region's
					# end.
					if occlStart:
						occlEnd = wTime
					else:
						occlStart = wTime
				else:
					# If a start and end are stored for the occluding
					# TrackRegion, add that TrackRegion to the list of occluding
					# regions for this clip.
					if occlStart and occlEnd:
						trackOcclRegions.append(TrackRegion(occlStart, occlEnd))
					# Clear the occluding start/end, since the track weighting
					# is no longer fully occluding.
					occlStart, occlEnd = None, None
				prevWVal = wVal
			# If occlStart is set, add the remainder of the clip to occluding
			# clips.
			if occlStart:
				trackOcclRegions.append(TrackRegion(occlStart, trackEnd))
			# If the clip ended with a non-zero weight, add the remainder as a
			# usedPortion.
			if wVal:
				usedPortions.append(TrackRegion(rangeStart, trackEnd))
		else:
			# If there are no weights, we can assume that the entire track will
			# be used.
			usedPortions = [TrackRegion(trackStart, trackEnd)]	
		# Finally, we'll clean up the list of subclips by eliminating occluded
		# sections of clips, and condensing continuous clips that were split
		# where their weight dips tangential to zero.
		usedTR = self._occludeTrackRegions(usedPortions, occludedRegions)
		subClips = self._findSubClips(usedTR)
		occludedRegions.extend(trackOcclRegions)
		return subClips, occludedRegions

	def _occludeTrackRegions(self, usedPortions, occludedRegions):
		outputRegions = []
		while len(usedPortions):
			tr = usedPortions.pop(0)
			for ocR in occludedRegions:
				# If TrackRegion is completely occluded
				if (ocR.start < tr.start) and (tr.end < ocR.end):
					tr = None
					break
				containsOcclStart = ((tr.start < ocR.start) and (ocR.start < tr.end))
				containsOcclEnd = ((tr.start < ocR.end) and (ocR.end < tr.end))
				if containsOcclStart and containsOcclEnd:
					outputRegions.append(TrackRegion(tr.start, ocR.start))
					tr = TrackRegion(ocR.end, tr.end)
				elif containsOcclStart:
					tr = TrackRegion(tr.start, ocR.start)
				elif containsOcclEnd:
					tr = TrackRegion(ocR.end, tr.end)
			else:
				outputRegions.append(tr)
		return outputRegions

	def _findSubClips(self, usedTrackRegions):
		subClips = []
		for clip in self.iterClips:
			for tr in usedTrackRegions:
				start = max(clip.start, tr.start)
				end = min(clip.end, tr.end)
				if end > start:
					subClips.append(SubClip(clip, start, end))

################################################################################

class TrackGroupInfo(object):
	"""An abstraction of the MAXScript MxTrackGroup class.

	Attributes:
		trackGroup: The ValueWrapper for the MxTrackGroup this TrackGroupInfo is
			wrapping.
		mixer: The MixerInfo instance for the MxTrackGroup's parent MxMixer.
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

	def __init__(self, mixer, trackGroup):
		self._trackGroup = trackGroup
		self._mixer = mixer
		self._hasSoloedTrack = None

	@property
	def trackGroup(self):
		"""The ValueWrapper for the MxTrackGroup this TrackGroupInfo is
			wrapping.
		"""
		return self._trackGroup
	@trackGroup.setter
	def trackGroup(self, value):
		self._trackGroup = value

	@property
	def mixer(self):
		"""The MixerInfo instance for the MxTrackGroup's parent MxMixer."""
		return self._mixer
	@mixer.setter
	def mixer(self, value):
		self._mixer = value

	@property
	def numTracks(self):
		"""The number of tracks contained in this TrackGroup."""
		return self.trackGroup.numTracks

	def getTrack(self, index):
		"""Returns a TrackInfo instance for the MxTrack at the specified index
			in the TrackGroup.

		Args:
						index(int): Index of desired track to retrieve.

		Returns:
						TrackInfo: The TrackInfo instance for the MxTrack at the
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
		return TrackInfo(self, track)

	def iterTracks(self):
		"""Wraps the MAXScript getTrack global function into a generator that
			returns TrackInfo instances for each Track in the TrackGroup, from
			top to bottom.

		Returns:
						generator: Generator that produces TrackInfo instances.
		"""
		count = self.numTracks
		for i in range(count):
			yield self.getTrack(i)

	def tracks(self):
		"""Get a list of TrackInfo instance for each Track in this TrackGroup
			from top to bottom.

		Returns:
						list: List of TrackInfo instances for each Track in the
							TrackGroup from top to bottom.
		"""
		return [t for t in self.iterTracks()]

	def iterEnabledTracks(self):
		"""Wraps the MAXScript getTrack global function into a generator that
			returns TrackInfo instances for each enabled Track in the
			TrackGroup, from top to bottom.  This means that in the case that a
			Track is soloed, only that Track will be returned.  Otherwise, only
			non-muted tracks will be returned.

		Returns:
						generator: Generator that produces TrackInfo instances
							for enabled Tracks.
		"""
		if self.hasSoloedTrack:
			yield self.soloedTrack
		else:
			for track in self.iterTracks():
				if not track.isMuted:
					yield track

	def enabledTracks(self):
		"""Get a list of TrackInfo instance for each enabled Track in this
			TrackGroup from top to bottom.  This means that in the case that a
			Track is soloed, a list containing only that Track will be returned.
			Otherwise, only non-muted tracks will be returned.

		Returns:
						list: List of TrackInfo instances for each enabled Track
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

	def getSubClips(self, occludedRegions=[]):
		"""Analyzes the weights for all tracks in the TrackGroup and returns a
			tuple of two lists, a list of SubClip instance for every used
			section of clips within the TrackGroup, and a list of TrackRegion
			instances for every occluding region in the TrackGroup.

		Returns:
						tuple: A tuple containing a list of SubClip instances
							for each used portion of a Clip in any enabled Track
							in the TrackGroup, and a list of TrackRegion
							instances for each region of fully occluding Clip in
							any enabled Track in the TrackGroup.
		"""
		subClips = []
		for track in self.iterEnabledTracks():
			sc, occl = track.analyzeWeights(occludedRegions)
			occludedRegions = occl
			subClips.extend(sc)

		return subClips, occludedRegions

################################################################################

class MixerInfo(object):
	"""An abstraction of the MAXScript MxMixer class.

	Attributes:
		mixer: The ValueWrapper for the MxMixer this MixerInfo is wrapping.
		numTrackGroups: The number of TrackGroups present in this Mixer.
	"""
	def __init__(self, mixer):
		self._mixer = mixer

	@property
	def mixer(self):
		"""The ValueWrapper for the MxMixer this MixerInfo is wrapping. """
		return self._mixer
	@mixer.setter
	def mixer(self, value):
		self._mixer = value

	@property
	def numTrackGroups(self):
		"""The number of TrackGroups this Mixer contains. """
		return self._mixer.numTrackGroups

	def getTrackGroup(self, index):
		"""Retrieves the TrackGroupInfo for the TrackGroupt at the specified
			index.

		Args:
						index(int): Index of desired TrackGroup to retrieve.

		Returns:
						TrackGroupInfo: TrackGroupInfo instance for the
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
		return TrackGroupInfo(self, trackGroup)

	def iterTrackGroups(self):
		"""Wraps the MAXScript getTrackGroup global function into a generator
			that returns TrackGroupInfo instances for each TrackGroup in the
			Mixer, from top to bottom.

		Returns:
						generator: Generator that produces TrackGroupInfo
							instances.
		"""
		count = self.numTrackGroups
		for i in range(count):
			yield self.getTrackGroup(i)

	def trackGroups(self):
		"""Returns a list of TrackGroupInfo instances for every TrackGroup in
			the Mixer, ordered from top to bottom.

		Returns:
						list: A list of TrackGroupInfo instances.
		"""
		return [tg for tg in self.iterTrackGroups()]

	def getSubClips(self):
		"""Analyzes the weights for all tracks in all TrackGroups in the Mixer,
			and compares the filters on each track group in order to generate a
			list of SubClip instance for every used section of every clip on an
			enabled Track.

		Returns:
						list: A list of SubClip instances for each used portion
							of a Clip.
		"""
		subClips = []
		analyzedTrackGroups = []
		for i, tg in enumerate(self.iterTrackGroups()):
			tgInfo = {}
			filters = set(tg.filters())
			tgInfo['filters'] = filters
			occludedRegions = []
			# For every trackgroup above this one whose filters are a superset
			# of this track's filters, any clips that occlude in that trackgroup
			# will also occlude in this one.
			for atg in analyzedTrackGroups:
				if atg['filters'].issuperset(filters):
					occludedRegions.extend(atg['occludedRegions'])
			sc, occl = tg.getSubClips(occludedRegions=occludedRegions)
			tgInfo['occludedRegions'] = occl
			tgInfo['i'] = i
			subClips.extend(sc)
			analyzedTrackGroups.append(tgInfo)
		return subClips

################################################################################
#####----------------------------- Functions ------------------------------#####
################################################################################

def getMixers():
	"""Finds all mixers present in the current MAX scene.

	Returns:
					list: A list of MixerInfo instances for each MxMixer in the
						current MAX Scene.
	"""
	# Since Mixer is a Class in MAXScript, and not a MAXClass, we're not able
	# to use getClassInstances to retrieve Mixers in the scene.  Instead, we'll
	# iterate over objects in the scene, and test to see if they have a
	# controller with a Mixer attached.
	mixers = []
	for obj in mxs.objects:
		if hasattr(obj, 'controller') and hasattr(obj.controller, 'mixer'):
			mixers.append(MixerInfo(obj.controller.mixer))
	return mixers
