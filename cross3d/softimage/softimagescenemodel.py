#
#	\namespace	blur3d.api.softimage.softimagesceneobject
#
#	\remarks	The SoftimageSceneModel class provides the implementation of the AbstractSceneModel class as it applies
#				to Softimage scenes
#
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/04/11
#

import os
import copy

from PySoftimage import xsi, xsiFactory
from win32com.client import constants
from blurdev.decorators import pendingdeprecation
from blur3d.api.abstract.abstractscenemodel import AbstractSceneModel

#------------------------------------------------------------------------

class SoftimageSceneModel(AbstractSceneModel):

	def _setNativeParent(self, nativeParent):
		xsi.Application.ParentObj(nativeParent, self._nativePointer)
		return True

	def _nativeGroups(self, wildcard='*'):
		return self._nativePointer.Groups.Filter('', '', wildcard)

	def isReferenced(self):
		return self._nativePointer.ModelKind == constants.siModelKind_Reference

	def update(self):
		xsi.UpdateReferencedModel(self._nativePointer)
		return True

	def offloaded(self):
		return not bool(self._nativePointer.Parameters('active_resolution').Value)

	def offload(self):
		xsi.SetResolutionOfRefModels(self._nativePointer, 0)
		return True

	def addResolution(self, name='', path='', load=False):
		if self.isReferenced():
			xsi.AddRefModelResolution(self._nativePointer, name, path)
			if load:
				self.setResolution(name)
			return True
		return False

	def removeResolution(self, name):
		if self.isReferenced():

			# Softimage does not allow to remove active resolutions.
			if self.resolution() == name:
				self.offload()
				
			xsi.RemoveRefModelResolution(self._nativePointer, name)
			return True
		return False

	def resolutionsPaths(self):
		return [self.resolutionPath(resolution) for resolution in self.resolutions() if resolution != 'Offloaded']

	def resolutionPath(self, resolution=''):
		if self.isReferenced():
			if not resolution:
				resolution = self.resolution()
			resolutions = self.resolutions()
			if resolution in resolutions:
				return xsi.GetValue("%s.resolutions.res%i.file" % (self.name(), resolutions.index(resolution)))
		return ''

	def setResolutionPath(self, path, resolution=''):
		if self.isReferenced():
			if not resolution:
				resolution = self.resolution()
			resolutions = self.resolutions()
			if resolution in resolutions:
				xsi.SetValue("%s.resolutions.res%i.file" % (self.name(), resolutions.index(resolution)), path)
				return True
		return False

	def setResolution(self, resolution):
		# handles qstrings
		resolution = unicode(resolution)
		# If I dont re-initialize a model object it does not return me the right resolutions.
		resolutions = self._scene.findObject(self.name()).resolutions()
		for res in resolutions:
			
			# Handles cases sensitivity (crappy, but needed because resolution
			# names often come from filenames).
			if res.lower() != resolution.lower():
				continue
		
			# Storing the user props that might be compromised when switching the reference model.
			userProps = self.userProps()
			oldUserProps = userProps.lookupProps()

			# Setting the resolution.
			xsi.SetResolutionOfRefModels(self._nativePointer, resolutions.index(res))

			# Making sure all the keys that where on the old resolution are re-assigned to the new one.
			for key in oldUserProps:
				if oldUserProps.get(key) and not userProps.get(key):
					userProps[key] = oldUserProps[key]

			# If the resolution did change.
			if self.resolution() == res:
				return True

		return False

	def resolution(self):
		if self.isReferenced():

			# If I dont re-initialize a model object it does not return me the right resolutions.
			resolutions = self._scene.findObject(self.name()).resolutions()
			if resolutions:
				return resolutions[self._nativePointer.Parameters('active_resolution').Value]
				
		return ''

	def resolutions(self):
		resolutions = []
		for parameter in self._nativePointer.Parameters:
			if 'resolutions' in parameter.fullname:
				resolutions.append(parameter.Value)
		return resolutions

	def export(self, fileName):
		xsi.ExportModel(self._nativePointer, fileName, True, False)
		return True
	
	def export(self, fileName):
		xsi.ExportModel(self._nativePointer, fileName, True, False)
		return True
	
	@pendingdeprecation('Use loadAnimation instead with mixer flag true.')
	def addAnimationClip(self, path, name=None):
		self.loadAnimationInMixer(self, path, name)

	def storePose(self, name='', objects=[]):
		if not objects:
			objects = self.objects()

		controllers = xsiFactory.CreateObject('XSI.Collection')
		controllers.AddItems([obj.nativePointer() for obj in objects])
		parameters = controllers.FindObjectsByMarkingAndCapabilities( None, 2048 )

		# Creating the action.
		return xsi.SIStoreAction(self._nativePointer, parameters, 1, False, '', '', '', '', True)

	def storeAnimation(self, name='', objects=[]):
		if not objects:
			objects = self.objects()

		controllers = xsiFactory.CreateObject('XSI.Collection')
		controllers.AddItems([obj.nativePointer() for obj in objects])
		parameters = controllers.FindObjectsByMarkingAndCapabilities( None, 2048 )

		# Creating the action.
		return xsi.SIStoreAction(self._nativePointer, parameters, 2, name, False, '', '', '', '', True)

	def savePose(self, basePath, name='', objects=[]):
		xsi.ExportAction(self.storePose(name, objects), os.path.join(basePath, name + '.eani'))
		return True

	def saveAnimation(self, basePath, name='', objects=[]):
		xsi.ExportAction(self.storeAnimation(name, objects), os.path.join(basePath, name + '.eani'))
		return True

	def loadPose(self, path):
		self.loadAnimation(path)
		# TODO: Set key if auto-key is on for relevant objects.

	def loadAnimation(self, path):
		if os.path.exists(path):
			xsi.ImportActionAndApply(self._nativePointer, path)

	def loadAnimationInMixer(self, path, name=None):
		native_model = self.nativePointer()
		native_mixer = native_model.mixer
		
		base_track_name = 'BlurAnimTrack'
		
		if name is None:
			name = os.path.basename(path).replace('.', '_') + '_Clip'

		# Each clip should be loaded onto its own track.
		# Look at the mixer on the Asset to find an empty track, or create a new
		# empty track to add the clip to.
		
		# If an asset doesn't have a mixer, it means it doesn't have any tracks
		# either. Create a new track, which will create the mixer.
		if not native_mixer:
			track_name = '{}0'.format(base_track_name)
			native_track = xsi.AddTrack(native_model, '', 0, track_name)
			native_mixer = native_model.mixer
			
		# If a mixer does exist, uses sequential numbering to create a new track,
		# or if that track already exists, test if it's empty.
		else:
			i = 0
			native_track = None
			while native_track is None or native_track.clips.count > 0:
				track_name = '{}{}'.format(base_track_name, i)
				native_track = native_mixer.tracks(track_name)
				if not native_track:
					native_track = xsi.AddTrack(native_model, native_model, 0, track_name)
					break
				i += 1
				
		# Adding clips is a 2-step process.  First, import the animation as an
		# Action.  Then create an "instance" of that animation as a Clip on one
		# of the tracks (a single action can be added as a clip to multiple tracks
		# on multiple assets).
		# Also, by Convention, clips should be offset to their start frame. This 
		# will be true unless Layout changes the way they export things.
		native_action = xsi.ImportAction(native_model, path, 0)
		native_clip = xsi.AddClip(native_model, native_action, "", native_track.FullName, native_action.FrameStart.Value, name)
		
		#TODO: wrap native clip (no specific blur3d object for it yet) and return it.
		return True

	def matchPose(self, model, objects=[]):

		action = model.storeAnimation('Match', objects)
		xsi.ApplyAction(action, self._nativePointer)

		# TODO:
		# For each object make a global match transform from this model to the target model.
		# Set keys if auto-key is on.

		return True

	def matchAnimation(self, model, objects=[]):

		action = model.storeAnimation('Match', objects)
		print model, action, self._nativePointer
		xsi.ApplyAction(action, self._nativePointer)

		# TODO:
		# Get a list of frames with keys for the provided objects.
		# For each frame make a global match transform from this model to the target model.
		# Set keys if auto-key is on.

		return True

# register the symbol
from blur3d import api
api.registerSymbol('SceneModel', SoftimageSceneModel)
