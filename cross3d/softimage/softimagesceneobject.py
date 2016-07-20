##
#	\namespace	cross3d.softimage.softimagesceneobject
#
#	\remarks	The SoftimageSceneObject class provides the implementation of the AbstractSceneObject class as it applies
#				to Softimage
#
#	\author		douglas
#	\author		Blur Studio
#	\date		04/04/11
#

#------------------------------------------------------------------------------------------------------------------------

from cross3d import application
from cross3d.constants import ObjectType
from PySoftimage import xsi, xsiFactory, constants as xsiConstants
from win32com.client.dynamic import Dispatch as dynDispatch
from cross3d.abstract.abstractsceneobject import AbstractSceneObject

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneObject(AbstractSceneObject):

	_nativeToAbstractObjectType = { 'light'         : ObjectType.Light,
									'camera'        : ObjectType.Camera,
									'Thinking'      : ObjectType.Particle | ObjectType.Thinking,
									'PF_Source'     : ObjectType.Particle,
									'FumeFX'		: ObjectType.FumeFX,
									'polymsh' 		: ObjectType.Geometry,
									'surfmsh'		: ObjectType.NurbsSurface,
									'crvlist'		: ObjectType.Curve,
									'#model'		: ObjectType.Model,
									'#Group'		: ObjectType.Group,
									'CameraInterest': ObjectType.CameraInterest }

	_abstractToNativeObjectType = dict((v,k) for k, v in _nativeToAbstractObjectType.iteritems())

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _findNativeChild(self, name, recursive=False, parent=None):
		"""
			\remarks	implements the AbstractSceneObject._findNativeChildren method to look up a specific native children for this object
			\return		<PySotimage.xsi.Object> nativeObject
		"""
		return self.nativePointer().FindChild(name, '', '', recursive)

	def _nativeChildren(self, recursive=False, wildcard='', type='', parent='', childrenCollector=[]):
		"""
			\remarks	implements the AbstractSceneObject._nativeChildren method to look up the native children for this object
			\param		recursive <bool> wildcard <string> type <string parent <string> childrenCollector <list>
			\sa			children
			\return		<list> [ <PySoftimage.xsi.Object> nativeObject, .. ]
		"""
		nativeType = ''
		if type != '':
			nativeType = self._nativeTypeOfObjectType(type)
		#return [ obj for obj in self._nativePointer.FindChildren( name, nativeType, parent, recursive ) ]
		return self._nativePointer.FindChildren2(wildcard, nativeType, '', recursive)

	def _nativeParent(self):
		"""
			\remarks	implements the AbstractSceneObject._nativeParent method to look up the native parent for this object
			\sa			parent, setParent, _setNativeParent
			\return		<PySoftimage.xsi.Object> nativeObject || None
		"""
		return self._nativePointer.Parent

	def _setNativeParent(self, nativeParent):
		"""
			\remarks	implements the AbstractSceneObject._setNativeParent method to set the native parent for this object
			\sa			parent, setParent, _nativeParent
			\param		<PySoftimage.xsi.Object> nativeObject || None
			\return		<bool> success
		"""
		if nativeParent is None:
			nativeParent = xsi.ActiveSceneRoot

		# Making sure the object is not already a child of the parent, otherwise Softimage throws an error
		if not self._nativePointer.Parent3DObject.IsEqualTo(nativeParent):
			nativeParent.AddChild(self._nativePointer)
		return True

	def _nativeModel(self):
		"""
			\remarks	implements the AbstractSceneObject._nativeModel method to look up the native model for this object
			\sa			children
			\return		<list> [ <PySotimage.xsi.Model> nativeObject, .. ]
		"""
		model = None
		obj = self.nativePointer()
		ignoreSceneRoot = True
		
		if str(obj.Type) == "#model":
			if ignoreSceneRoot is True and obj.Name == "Scene_Root":
				model = None
			else:
				model = obj
		else:
			try:
				if ignoreSceneRoot is True and obj.Model.Name == "Scene_Root":
					model = None
				else:
					model = obj.Model
			except AttributeError:
				pass

		return model

	def _setNativeModel(self, nativeModel):
		"""
		"""
		if self._nativePointer.Model.IsEqualTo(nativeModel):
			return True

		# Making sure the object is not already a child of the parent, otherwise Softimage throws an error
		if not self._nativePointer.Parent3DObject.IsEqualTo(nativeModel):
			nativeModel.AddChild(self._nativePointer)

		return True

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def isDeleted(self):
		return (self._nativePointer.Parent is None)

	def _constrainingNativeObjects(self):
		constraining = []
		for constraint in self.Kinematics.Constraints:
			constraining += [obj for obj in constraint.Constraining]
		return constraining

	def _constrainedNativeObjects(self):
		constraineds = []

		# TODO: Currently we only support "Pose Constraints".
		constraints = xsi.FindObjects(None, "{D42BBF71-3C47-11D2-8B42-00A024EE586F}")
		for constraint in constraints:

			# This is a weird thing when looking for all object type constraint.
			if constraint.FullName.startswith("TransientObjectContainer") or constraint.Parent3DObject is None:
				continue
				
			# Looping through constraining object.
			for constraining in constraint.Constraining:
				if constraining.isEqualTo(self._nativePointer):
					constraineds.append(constraint.Constrained)
					
		return constraineds
   
	def getCacheName(self, type):
		typeDic = {	"Pc":".pc2",
					"Tmc":".tmc",
					"Abc":".abc",
					"Icecache":".icecache"}


		obj = self._nativePointer
		name = obj.Fullname
		cacheName = name.replace("." , "")
		cacheName = cacheName + typeDic[type]


		return cacheName


	def deleteProperty(self, propertyName):
		"""
			\remarks	implements the AbstractSceneObject.deleteProperty that deletes a property of this object.
			\return		<bool> success
		"""
		xsi.DeleteObj('.'.join([ self.name(), propertyName ]))
		return True

	def uniqueId(self):
		"""
			\remarks	implements the AbstractSceneObject.uniqueId to look up the unique name for this object and returns it
			\sa			displayName, setDisplayName, setName
			\return		<str> name
		"""
		return self._nativePointer.ObjectID

	def applyCache(self, path, type):
		"""Applies cache to object
		param <string>path , <string>types "Pc","Tmc","Icecache", "Abc", Type 
		return cache object
		"""
		obj = self._nativePointer
		if type == "Pc":

			cache = obj.ActivePrimitive.ConstructionHistory.Find("BlurPCOperator")
			if not cache:
				xsi.BlurPCAddDeformer(self._nativePointer)
				cache = obj.ActivePrimitive.ConstructionHistory.Find("BlurPCOperator")
				cache.Parameters("Filename").Value = path
				#xsi.setValue((cache.Fullname +".Filename"), path)
				return cache
			else:
				cache.Parameters("Filename").Value = path
				return cache

		elif type == "Tmc":
			kine = obj.Kinematics.Global
			tmcop = kine.NestedObjects("TmcOp")


			if not tmcop:
				cache = xsi.ApplyTmcOp(self._nativePointer)
				tmcop = kine.NestedObjects("TmcOp")

			tmcop.Parameters("Filename").Value = path

			return tmcop

		elif type == "Icecache":
			cache = xsi.AddFileCacheSource(obj, path)
			return cache


		elif type == "abc":
			print("unsupported")
			return None

		else:
			print("unsupported cache Type")
			return None

	def parameters(self):
		parameters = {}
		for parameter in self._nativePointer.Parameters:
			parameters[parameter.ScriptName] = parameter.Value
		return parameters

	def setParameters(self, parameters):
		for key, value in parameters.iteritems():
			try:
				self._nativePointer.Parameters(key).Value = value
			except:
				print 'TRACEBACK: skipping param: {} {}...'.format(key, value)
				print traceback.format_exc()

	def resetTransforms(self, pos=True, rot=True, scl=True):
		"""
			Resets the transforms to zero.
		"""
		if pos and rot and scl:
			xsi.ResetTransform(self._nativePointer, "siObj", "siSRT", "siXYZ")
		else:
			if pos:
				xsi.ResetTransform(self._nativePointer, "siObj", "siTrn", "siXYZ")
			if rot:
				xsi.ResetTransform(self._nativePointer, "siObj", "siRot", "siXYZ")
			if pos:
				xsi.ResetTransform(self._nativePointer, "siObj", "siScl", "siXYZ")
		return True

	def rotation(self, local=False):
		"""
		Returns the rotation of the current object.
		:param local: If True return the local rotation. Default False.
		"""
		if local:
			trans = self._nativePointer.Kinematics.Local
		else:
			trans = self._nativePointer.Kinematics.Global
		return trans.rotx.Value, trans.roty.Value, trans.rotz.Value

	def setHidden(self, state):
		"""Hides/unhides this object
		"""
		self._nativePointer.Properties('Visibility').Parameters('viewvis').SetValue(not state)
		self._nativePointer.Properties('Visibility').Parameters('rendvis').SetValue(not state)
		return True

	def matchTransforms(self, obj, position=True, rotation=True, scale=True):
		"""
			Currently the auto-key support is a bit lite, but it should cover most of the cases.
		"""

		if position:
			self._nativePointer.Kinematics.Global.Parameters('posx').Value = obj.nativePointer().Kinematics.Global.Parameters('posx').Value
			self._nativePointer.Kinematics.Global.Parameters('posy').Value = obj.nativePointer().Kinematics.Global.Parameters('posy').Value
			self._nativePointer.Kinematics.Global.Parameters('posz').Value = obj.nativePointer().Kinematics.Global.Parameters('posz').Value

		if rotation:
			self._nativePointer.Kinematics.Global.Parameters('rotx').Value = obj.nativePointer().Kinematics.Global.Parameters('rotx').Value
			self._nativePointer.Kinematics.Global.Parameters('roty').Value = obj.nativePointer().Kinematics.Global.Parameters('roty').Value
			self._nativePointer.Kinematics.Global.Parameters('rotz').Value = obj.nativePointer().Kinematics.Global.Parameters('rotz').Value

		if scale:
			self._nativePointer.Kinematics.Global.Parameters('sclx').Value = obj.nativePointer().Kinematics.Global.Parameters('sclx').Value
			self._nativePointer.Kinematics.Global.Parameters('scly').Value = obj.nativePointer().Kinematics.Global.Parameters('scly').Value
			self._nativePointer.Kinematics.Global.Parameters('sclz').Value = obj.nativePointer().Kinematics.Global.Parameters('sclz').Value

		if application.autokey():
			self.key()

		return True

	def key(self, target='keyable'):
		"""
			Set keys on the object parameters.
		"""
		xsi.SaveKeyOnKeyable(self._nativePointer)

	def translation(self, local=False):
		"""
		Returns the translation of the current object.
		:param local: If True return the local translation. Default False.
		"""
		if local:
			trans = self._nativePointer.Kinematics.Local
		else:
			trans = self._nativePointer.Kinematics.Global
		return trans.posx.Value, trans.posy.Value, trans.posz.Value

	#------------------------------------------------------------------------------------------------------------------------
	# 												class methods
	#------------------------------------------------------------------------------------------------------------------------

	@classmethod
	def _typeOfNativeObject(cls, nativeObject):
		"""
			\remarks	reimplements the AbstractSceneObject._typeOfNativeObject method to returns the ObjectType of the nativeObject applied
			\param		<PySoftimage.xsi.Object> nativeObject || None
			\return		<bool> success
		"""

		type = nativeObject.Type
		abstractType = cls._nativeToAbstractObjectType.get(type)

		if abstractType == None:
			return AbstractSceneObject._typeOfNativeObject(nativeObject)
			
		return abstractType

	#------------------------------------------------------------------------------------------------------------------------
	# 												static methods
	#------------------------------------------------------------------------------------------------------------------------

	@staticmethod
	def _nativeTypeOfObjectType(objectType):
		"""
			\remarks	reimplements the AbstractSceneObject._nativeTypeOfObjectType method to return the nativeType of the ObjectType supplied
			\param		<cross3d.constants.ObjectType> objectType || None
			\return		<bool> success
		"""
		if objectType == ObjectType.Geometry:
			return 'polymsh'
		elif objectType == ObjectType.Light:
			return 'light'
		elif objectType == ObjectType.Camera:
			return 'camera'
		elif objectType == ObjectType.Model:
			return '#model'
		elif objectType == ObjectType.Group:
			return '#group'
		elif objectType == ObjectType.NurbsSurface:
			return 'surfmsh'
		elif objectType == ObjectType.Curve:
			return 'crvlist'
		else:
			return None
		return AbstractSceneObject._nativeTypeOfObjectType(objectType)

	def keyedFrames(self, start=None, end=None):		
		
		# Collecting the transform parameters with animation.
		parameters = []
		transformsGlobal = self._nativePointer.Kinematics.Global
		transformsLocal = self._nativePointer.Kinematics.Local
		for transform in [ 'pos', 'rot', 'scl' ]:
			for axis in 'xyz':
				parameterGlobal = transformsGlobal.Parameters(transform + axis)
				parameterLocal = transformsLocal.Parameters(transform + axis)
				if (parameterGlobal and parameterGlobal.IsAnimated(xsiConstants.siFCurveSource)) or (parameterLocal and parameterLocal.isAnimated(xsiConstants.siFCurveSource)):
					parameters.append(parameterLocal)

		# Collecting all curves for this parameters.
		curves = []
		for parameter in parameters:
			for source in parameter.Sources:
				if source.Type == 20:
					curves.append(source)

		# Collecting all frames with keys for these curves.
		frames = set()
		for curve in curves:
			for key in curve.Keys:
				frames.add(key.Time) 
		
		frames = list(frames)
		frames = filter(lambda a: (start is None or start-1E-6 <= a) and (end is None or a <= end+1E-6), frames)
		return sorted(frames)

# register the symbol
import cross3d
cross3d.registerSymbol('SceneObject', SoftimageSceneObject)
