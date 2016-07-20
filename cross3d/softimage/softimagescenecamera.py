##
#	\namespace	cross3d.softimage.softimagescenecamera
#
#	\remarks	The SotimageSceneCamera class provides the implementation of the AbstractSceneCamera class as it applies
#				to Softimage scenes
#
#	\author		douglas
#	\author		Blur Studio
#	\date		03/15/10
#

import os
import re
import math
import traceback
import cross3d

from PySoftimage import xsi, constants as xsiConstants
from cross3d import application
from cross3d import FileSequence
from cross3d.abstract.abstractscenecamera import AbstractSceneCamera

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneCamera(AbstractSceneCamera):

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def interest(self):
		if self._nativePointer.Interest:
			return cross3d.SceneObject(self._scene, self._nativePointer.Interest)
		return None

	def setInterest(self, interest):
		if interest:
			self._nativePointer.Interest = interest.nativePointer()

	def fov(self, rounded=False):
		param_name = '{}.camera.fov'.format(self._nativePointer.FullName)
		prop = xsi.Dictionary.GetObject(param_name)
		fov = prop.Value
		if rounded:
			return int(round(fov))
		return fov

	def frustrumPlaneImagePath(self, name):

		# Conforming the name. Non supported Softimage character will become underscores.
		name = application.conformObjectName(name)

		# This means the plane is present on the camera either by parenting or constraint.
		if self._findNativeChild(name) or name in [obj.name for obj in self._constrainedNativeObjects()]:

			# Now we are looking for the corresponding clip.
			clip = xsi.Dictionary.GetObject('Clips.%s' % name, False)
			if clip:
				path = clip.Source.FileName.Value

				# This is the painful process of converting Softimage way to express path into our generic one.
				match = re.match(cross3d.application.imageSequenceRegex(), path)
				if match:
					t = match.groupdict()
					fileSequence = FileSequence('%s%s-%s.%s' % (t['path'], t['start'], t['end'], t['extension']))
					fileSequence.setPadding(int(t['padding']))
					return fileSequence.path()
				else:
					return path

		# Otherwise return empty.
		return ''

	def setFrustrumPlaneImagePath(self, name, imagePath, offset=0.0, speed=1.0):

		# Conforming the name. Non supported Softimage character will become underscores.
		name = application.conformObjectName(name)
		clip = xsi.Dictionary.GetObject('Clips.%s' % name, False) or xsi.SICreateImageClip2(imagePath, name)(0)

		# Figuring out if we have an image or a file sequence.
		if FileSequence.isValidSequencePath(imagePath):
			fs = FileSequence(imagePath)
			template = '{}{}[{}..{};{}].{}'
			baseName = template.format(fs.baseName(), fs.separator(), fs.start(), fs.end(), fs.padding(), fs.extension())
			clip.Source.FileName.Value = os.path.join(fs.basePath(), baseName)
			xsi.setValue('%s.timectrl.clipin' % clip.FullName, fs.start())
			xsi.setValue('%s.timectrl.clipout' % clip.FullName, fs.end())
			xsi.setValue('%s.timectrl.startoffset' % clip.FullName, fs.start() + offset)
			xsi.setValue('%s.timectrl.scale' % clip.FullName, speed)

		else:
			clip.Source.FileName.Value = imagePath
			xsi.setValue('%s.timectrl.startoffset' % clip.FullName, offset)
			xsi.setValue('%s.timectrl.scale' % clip.FullName, speed)

		# Finally returning the clip object.
		return clip

	def removeFrustrumPlane(self, name):
		name = application.conformObjectName(name)
		plane = self.nativePointer().findChild(name)
		if plane:

			# Removing the plane. I branch it cause there is cases where we have a plane parent.
			xsi.DeleteObj('B:{}'.format(plane.FullName))

			# Removing material.
			material = xsi.Dictionary.GetObject('Sources.Materials.DefaultLib.%s' % name, False)
			if material:
				xsi.DeleteObj(material.FullName)

			# Removing clip.
			clip = xsi.Dictionary.GetObject('Clips.%s' % name, False)
			if clip:
				xsi.DeleteObj(clip.FullName)

			return True
		return False

	def createFrustrumPlane(self, name='', imagePath='', offset=0.0, speed=1.0, distance=1.0, parent=None):
		""" Will create a 3D plane attached to the camera and matching the camera view frustum.
			Parent can be used when the plane should not be directly parented under the camera and constrained instead.
		"""

		from win32com.client import Dispatch
		xsiMath = Dispatch("XSI.Math")

		# Initializing things.
		fs = None

		# Figuring out if we have an image or a file fs.
		if FileSequence.isValidSequencePath(imagePath):
			fs = FileSequence(imagePath)
			name = name or fs.baseName()
		else:
			name = name or os.path.splitext(os.path.basename(imagePath))[0]

		# Conforming the name. Non supported Softimage character will become underscores.
		name = application.conformObjectName(name)
		anchor = xsi.ActiveSceneRoot.AddNull(name) if parent or self.isReferenced() else self._nativePointer

		# Creating the Plane.
		plane = xsi.CreatePrim("Grid", "MeshSurface", '{}_Plane'.format(name) if parent or self.isReferenced() else name, "")
		plane.Properties("Visibility").Parameters("selectability").Value = False

		# Parenting the plane to the anchor.
		anchor.AddChild(plane)

		# If parent is defined.
		if parent:
			parent.nativePointer().addChild(anchor)

		# If the anchor is not the camera we need to constrain the anchor to the camera. 
		# This is mosty useful for cameras inside a reference model.
		if not anchor.isEqualTo(self._nativePointer):
			anchor.Kinematics.AddConstraint('Pose', self._nativePointer)

		# Setting dipslay options.
		display = plane.AddProperty("Display Property")
		parameters = ['staticsel', 'intsel', 'playbacksel', 'staticunselnear', 'intunselnear', 'staticunselfar', 'intunselfar', 'playbackunselfar']
		for parameter in parameters:
			display.Parameters(parameter).Value = 9

		# Setting the plane transform.
		transform = xsiMath.CreateTransform()
		transform.SetTranslation(xsiMath.CreateVector3(0, 0, -distance))
		transform.SetRotationFromXYZAngles(xsiMath.CreateVector3(math.pi * 0.5, 0, math.pi))
		plane.Kinematics.Local.Transform = transform

		# Setting the plane subdivs and size.
		for parameter in ['subdivu', 'subdivv', 'ulength', 'vlength']:
			plane.Parameters(parameter).Value = 1

		# Creating UVs
		xsi.CreateProjection(plane, "siTxtPlanarXZ", "siTxtDefaultPlanarXZ", "", "imagePath_Projection")
		xsi.FreezeObj(plane)

		# Setting the scale expressions.
		expression = 'tan(%s.camera.fov * 0.5) * %s.kine.local.posz * 2' % (self.name(), plane.FullName)
		plane.sclx.AddExpression(expression)
		expression = '%s / %s.camera.aspect' % (expression, self.name())
		plane.sclz.AddExpression(expression)

		# Locking transforms.
		for parameter in ['posx', 'posy', 'rotx', 'roty', 'rotz', 'sclx', 'scly', 'sclz']:
			parameter = plane.Parameters(parameter)
			parameter.Keyable = False
			parameter.ReadOnly = True

		# If a imagePath is provided we create a material.
		if not imagePath:
			return True

		# Getting or creating the clip.
		clip = self.setFrustrumPlaneImagePath(name, imagePath, offset, speed)

		# Getting or creating the material.
		header = 'Sources.Materials.DefaultLib'
		material = xsi.Dictionary.GetObject('%s.%s' % (header, name), False)
		if not material:
			preset = '$XSI_DSPRESETS\\Shaders\\Material\\Constant.Preset'
			material = xsi.Dictionary.GetObject(header).CreateMaterial(preset, 'Constant')
			material.Name = name
			xsi.SIApplyShaderToCnxPoint("Image", "%s.Constant.color" % material.FullName)
			xsi.SIConnectShaderToCnxPoint(clip.FullName, "%s.Image.tex" % material.FullName)

			# TODO: Ideally I would detect if the image has alpha.
			if os.path.splitext(imagePath)[1] in ['.png', '.tga', '.exr', '.tif', '.tiff']:
				xsi.SIConnectShaderToCnxPoint("%s.Image.out" % material.FullName, "%s.Constant.transparency" % material.FullName, False)
				xsi.SetValue("%s.Constant.usealphatrans"  % material.FullName, True)
				xsi.SetValue("%s.Constant.inverttrans" % material.FullName, True)

		if material:
			xsi.AssignMaterial(','.join([material.FullName, plane.FullName]))

		# Returning.
		return True

	def setPlatePath(self, path):
		"""
			TODO: This is currently only handling FileSequence paths defined by the cross3d.FileSequence class.
				  It does not support static images or movies.
		"""
		fs = FileSequence(path)
		start = fs.start()
		end = fs.end()

		# Example: S:\\Deadpool\\Footage\\Sc000\\S0000.00\\Plates\\Sc000_S0000.00.[100..190;4].jpg
		fileName = '%s%s[%i..%i;%i].%s' % (fs.baseName(), fs.separator(), start, end, fs.padding(), fs.extension())
		path = os.path.join(fs.basePath(), fileName)
		clip = xsi.Dictionary.GetObject('Clips.%s_Plate' % self.name(), False)
		if not clip:
			clip = xsi.SICreateImageClip2(path, '%s_Plate' % self.name())(0)
		else:
			clip.Source.FileName.Value = path

			# TODO: Do not get why this does not work!
			# clip.TimeControl.clipin = start
			# clip.TimeControl.clipout= end
			# clip.TimeControl.startoffset = start

			xsi.setValue('%s.timectrl.clipin' % clip.FullName, start)
			xsi.setValue('%s.timectrl.clipout' % clip.FullName, end)
			xsi.setValue('%s.timectrl.startoffset' % clip.FullName, start)

		xsi.SetValue("%s.rotoscope.imagename" % self.name(), clip.FullName, "")
		return False

	def platePath(self):
		"""
			TODO: This is currently only handling FileSequence paths defined by the cross3d.FileSequence class.
				  It does not support static images or movies.
		"""

		# If not plate is assigned the clip name will be and empty string.
		clipName = xsi.GetValue("%s.rotoscope.imagename" % self.name())
		if clipName:
			clip = xsi.Dictionary.GetObject(clipName, False)
			path = clip.Source.FileName.Value
			match = re.match(cross3d.application.imageSequenceRegex(), path)
			if match:
				t = match.groupdict()
				fileSequence = FileSequence('%s%s-%s.%s' % (t['path'], t['start'], t['end'], t['extension']))
				fileSequence.setPadding(int(t['padding']))
				return fileSequence.path()

		# Fallback.
		return ''

	def setPlateEnabled(self, enabled):
		self._nativePointer.Properties('Camera Display').Parameters('rotoenable').Value = enabled
		return True

	def plateEnabled(self):
		return self._nativePointer.Properties('Camera Display').Parameters('rotoenable').Value

	def matchViewport(self, viewport):
		return self.matchCamera(viewport.camera())

	def matchCamera(self, camera):
		"""
			Match this camera to another one.
		"""
		self.setParameters(camera.parameters())
		self.setViewOptions(camera.viewOptions())
		self.matchTransforms(camera)
		return True

	def filmWidth(self):
		"""
			\remarks	Returns the film_width of the camera in mm.
			\return		film_width (float)
		"""
		width = self._nativePointer.projplanewidth.Value
		# XSI uses inches, convert inches to mm 1in / 25.4mm
		return width * 25.4

	def setFilmWidth(self, width):
		"""
			\remarks	Sets the film_width value for the camera.
			\param		width <float>
			\return		n/a
		"""
		# XSI uses inches, convert inches to mm 1in / 25.4mm
		self._nativePointer.projplanewidth.Value = width / 25.4
		return True

	def filmHeight(self):
		"""
			\remarks	Returns the film_height of the camera in mm.
			\return		film_width (float)
		"""
		height = self._nativePointer.projplaneheight.Value
		# XSI uses inches, convert inches to mm 1in / 25.4mm
		return height * 25.4

	def setFilmHeight(self, height):
		"""
			\remarks	Sets the film_height value for the camera.
			\param		width <float>
			\return		n/a
		"""
		# XSI uses inches, convert inches to mm 1in / 25.4mm
		self._nativePointer.projplaneheight.Value = height / 25.4
		return True

	def _nativeFocalLength(self):
		return xsi.GetValue(self.name() + '.camera.projplanedist')

	def setLens(self, value):
		self._nativePointer.Parameters('projplanedist').Value = value

	def showsFrame(self):
		return xsi.GetValue(self.name() + '.camvis.currenttime')

	def setShowsFrame(self, switch):
		xsi.SetValue(self.name() + '.camvis.currenttime', switch)
		return True

	def setShowsCustomParameters(self, switch):
		xsi.SetValue(self.name() + '.camvis.custominfo', switch)
		return True

	def setHeadLightIsActive(self, switch):
		xsi.SetValue(self.name() + '.camdisp.headlight', switch)
		return True

	def headlightIsActive(self):
		return xsi.GetValue(self.name() + '.camdisp.headlight')

	def pictureRatio(self):
		return self._nativePointer.Parameters('aspect').Value

	def setPictureRatio(self, pictureRatio):
		xsi.setValue(self.name() + '.camera.aspect', pictureRatio)
		#self._nativePointer.Parameters( 'aspect' ).Value = pictureRatio
		return True

	def farClippingPlane(self):
		return self._nativePointer.Parameters('far').Value

	def setFarClippingPlane(self, distance):
		xsi.setValue(self.name() + '.camera.far', distance)
		#self._nativePointer.Parameters( 'far' ).Value = distance
		return True

	def nearClippingPlane(self):
		return self._nativePointer.Parameters('near').Value

	def setNearClippingPlane(self, distance):
		xsi.setValue(self.name() + '.camera.near', distance)
		#self._nativePointer.Parameters( 'near' ).Value = distance
		return True

	def clippingEnabled(self):
		return self.userProps().setdefault('clipping_enabled', False)
		
	def setClippingEnabled(self, state):
		self.userProps()['clipping_enabled'] = state

	def viewOptions(self):
		viewOptions = {'Camera Visibility': {}, 'Camera Display': {}}

		for parameter in self._nativePointer.Properties('Camera Visibility').Parameters:
			viewOptions['Camera Visibility'][ parameter.ScriptName ] = parameter.Value

		for parameter in self._nativePointer.Properties('Camera Display').Parameters:
			viewOptions['Camera Display'][ parameter.ScriptName ] = parameter.Value

		viewOptions[ 'viewcubeshow' ] = xsi.GetValue('preferences.ViewCube.show')
		return viewOptions

	def setViewOptions(self, viewOptions):
		for prop in viewOptions:
			if prop in [ 'Camera Visibility', 'Camera Display' ]:
				for param in viewOptions[prop]:
					if not param in ['hidlincol', 'wrfrmdpthcuecol']:
						try:
							self._nativePointer.Properties(prop).Parameters(param).Value = viewOptions[prop][param]
						except:
							print 'TRACEBACK: skipping param: {} {}...'.format(prop, param)
							print traceback.format_exc()

		xsi.SetValue('preferences.ViewCube.show', viewOptions.get('viewcubeshow'), xsi.GetValue('preferences.ViewCube.show'))
		return True

# register the symbol
import cross3d
cross3d.registerSymbol('SceneCamera', SoftimageSceneCamera)
