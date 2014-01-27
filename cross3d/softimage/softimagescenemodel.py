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

from PySoftimage import xsi
from win32com.client import constants
from blur3d.api.abstract.abstractscenemodel import AbstractSceneModel

#-------------------------------------------------------------------------


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
			xsi.RemoveRefModelResolution(self._nativePointer, name)
			return True
		return False

	def resolutionsPaths(self):
		return [self.resolutionPath(resolution) for resolution in self.resolutions()]

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

		# If I dont re-initialize a model object it does not return me the right resolutions.
		resolutions = self._scene.findObject(self.name()).resolutions()
		
		if resolution in resolutions:
			xsi.SetResolutionOfRefModels(self._nativePointer, resolutions.index(resolution))
			if self.resolution() == resolution:
				return True
		return False

	def resolution(self):
		
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

	def export( self, fileName ):
		xsi.ExportModel( self._nativePointer, fileName, True, False )
		return True
	
	def export( self, fileName ):
		xsi.ExportModel( self._nativePointer, fileName, True, False )
		return True
	
# register the symbol
from blur3d import api
api.registerSymbol('SceneModel', SoftimageSceneModel)
