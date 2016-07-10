import re
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma
import maya.cmds as cmds
from cross3d.constants import ObjectType, RotationOrder, PointerTypes
from cross3d import application, UserProps, ExceptionRouter
from cross3d.abstract.abstractsceneobject import AbstractSceneObject
						
class MayaSceneObject( AbstractSceneObject ):
	#--------------------------------------------------------------------------------
	#							Init class variables
	#--------------------------------------------------------------------------------
	
	# This enum provides a map between cross3d's objectTypes and OpenMaya.MFn object types.
	# If the values are in a tuple more than one MFn object type needs to map to cross3d's objectType
	# None values are ignored. They eather don't exist, or we haven't found the maya equivelent of it.
	# NOTE: Many of these are untested.
	_abstractToNativeObjectType = {ObjectType.Generic: om.MFn.kDagNode,
		ObjectType.Geometry: om.MFn.kMesh,
		ObjectType.Light: om.MFn.kLight,
		ObjectType.Camera: om.MFn.kCamera,
		ObjectType.Model: om.MFn.kTransform,
		ObjectType.Group: None,
		ObjectType.Bone: om.MFn.kJoint,
		ObjectType.Particle: (om.MFn.kParticle, om.MFn.kNParticle), # I am not sure this is required, but it is supported
		ObjectType.FumeFX: None,
		ObjectType.Curve: om.MFn.kCurve,
		ObjectType.PolyMesh: om.MFn.kPolyMesh,
		ObjectType.NurbsSurface: om.MFn.kNurbsSurface,
		ObjectType.Thinking: None,
		ObjectType.XMeshLoader: None,
		ObjectType.CameraInterest: None
	}
	# Create the inverse of _abstractToNativeObjectType.
	_nativeToAbstractObjectType = {}
	for abstract, native in _abstractToNativeObjectType.iteritems():
		if isinstance(native, (tuple, list)):
			for item in native:
				_nativeToAbstractObjectType[item] = abstract
		else:
			_nativeToAbstractObjectType[native] = abstract
	
	def __init__(self, scene, nativeObject):
		""" MayaSceneObject's should always have the shape node stored in _nativePointer
		MayaSceneObject's should have the transform node stored in _nativeTransform
		A transform can have multiple shape nodes, as children, but a shape node can only
		have a single transform as its parent. If you init this class with a transform node
		it will automaticly convert the native pointer to the first shape node. If you init
		this class with a shape node it will use that shape node as the native pointer.
		
		TODO: When we want to add support for swaping shape nodes they should be implemented
		as self.setTransform(SceneObject). This will update the _nativeTransform for self and
		prevent needing to create a new SceneObject.
		"""
		# Make sure the nativeObject is a OpenMaya.MObject, and that its a shape node.
		mObj = self._asMOBject(nativeObject)
		with ExceptionRouter():
			nativeObject = self._getShapeNode(mObj)
		super(MayaSceneObject, self).__init__(scene, nativeObject)
		# store the transform node so we can access it later
		self._nativeTransform = self._getTransformNode(mObj)
	
	#--------------------------------------------------------------------------------
	#							cross3d private methods
	#--------------------------------------------------------------------------------
	@classmethod
	def _mObjChildren(cls, mObj, recursive=True, regex=None):

		with ExceptionRouter():
			path = om.MDagPath.getAPathTo(mObj)
			for index in range(path.childCount()):
				child = path.child(index)
				if child.apiType() in [om.MFn.kTransform, om.MFn.kJoint]:
					if not regex or regex.match(api.SceneObject._mObjName(child, fullName=False)):
						yield child
					if recursive == True:
						for i in cls._mObjChildren(child, regex=regex):
							yield i 

	def _findNativeChild(self, name, recursive=False, parent=None):
		for child in self._nativeChildren(recursive=recursive, wildcard=name, parent=parent):
			return child

	def _nativeChildren(self, recursive=False, wildcard='', type='', parent='', childrenCollector=[]):
		"""
			\remarks	looks up the native children for this object
			\param		recursive         <bool>
			\param		parent		      <variant> nativeObject(used for recursive searches when necessary)
			\param		childrenCollector <list> (used for recursive searches when necessary)
			\sa			children
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		if type:
			cross3d.logger.debug('type not implemented yet.')
		if parent:
			cross3d.logger.debug('parent not implemented yet.')
		if childrenCollector:
			cross3d.logger.debug('childrenCollector not implemented yet.')
		# Convert the wildcard to a regular expression so the generator doesn't have to create the
		# regex over and over
		regex=None
		if wildcard:
			expression = application._wildcardToRegex(wildcard)
			regex = re.compile(expression, flags=re.I)
		return self._mObjChildren(self._nativeTransform, recursive=recursive, regex=regex)

	def _nativeModel(self):
		"""
			\remarks	looks up the native model for this object
			\sa			model, setModel, _setNativeModel
			\return		<variant> nativeObject || None
		"""
		parent = self.parent()
		while parent is not None:
			if isinstance(parent, api.SceneModel):
				return parent.nativePointer()

			parent = parent.parent()

		# namespace = self._namespace(self._nativePointer)['namespace']
		# if namespace:
		# 	return self._scene._findNativeObject(name=namespace)
		
		return None
	
	def _nativeName(self):
		""" A convience method that returns the name of the shape node, not the transform node.
		"""
		return self._mObjName(self._nativePointer, True)
	
	def _nativeParent(self):
		""" Looks up the native parent for this object
			\sa			parent, setParent, _setNativeParent
			\return		<variant> nativeObject || None
		"""
		ret = cmds.listRelatives(self.path(), parent=True, fullPath=True)
		if ret:
			return self._asMOBject(ret[0])
		return None
	
	def _setNativeParent(self, nativeParent):
		""" sets the native parent for this object
			\sa			parent, setParent, _nativeParent
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		if nativeParent:
			# Making sure the object is not already child of the new parent. Otherwise Maya throw an error.
			parents = cmds.listRelatives(self._mObjName(self._nativeTransform), parent=1, fullPath=True)
			if parents and parents[0] == self._mObjName(nativeParent):
				return True
			cmds.parent(self._mObjName(self._nativeTransform), self._mObjName(nativeParent))
			return True
		return False
	
	@property
	def _nativeTransform(self):
		""" If you are storing OpenMaya.MObject's long enough for them to become invalidated(opening 
		a new scene for example), maya will crash and close because it is now accessing invalid 
		memory. To be able to safely store MObject's for long term, we need to store them in a
		MObjectHandle object.
		"""
		return self._nativeTypeHandle.object()
	
	@_nativeTransform.setter
	def _nativeTransform(self, nativePointer):
		self._nativeTypeHandle = om.MObjectHandle(nativePointer)
	
	@property
	def _nativeTypePointer(self):
		""" Returns a MFn wrapped version of self._nativePointer.
		
		This property is Read-Only.
		
		Returns:
			maya.OpenMaya.MFn[type object].
		"""
		return self._genNativeTypePointer(self._nativePointer)
		
	def _genNativeTypePointer(self, mObj):
		""" Generates a MFn object for the provided MObject.
		"""
		className = 'MFn{0}'.format(mObj.apiTypeStr()[1:])

		# Yep Maya is so consistent !
		if className == "MFnJoint":
			className = "MFnIkJoint"

		if hasattr(om, className):
			return getattr(om, className)(mObj)
		elif hasattr(oma, className):
			return getattr(oma, className)(mObj)
	
	def __call__(self, retType=PointerTypes.Pointer):
		""" Returns the native pointer for the object.
		
		Depending on the software and what you pass into retType, you will get a diffrent object.
		By default this simply returns self.nativePointer().
		
		Args:
			retType (cross3d.constants.PointerTypes): Used to request a specific native object.
					Defaults to cross3d.constants.PointerTypes.Pointer.
		
		Returns:
			Variant: Returns a native pointer object specific to the software.
		"""
		# Make sure we have a valid PointerType
		retType = PointerTypes[retType]
		if retType == PointerTypes.Transform:
			return self._genNativeTypePointer(self._nativeTransform)
		elif retType == PointerTypes.Shape:
			return self._nativeTypePointer
		return self._nativePointer
	
	@classmethod
	def _typeOfNativeObject(cls, nativeObject):
		"""
			\remarks	reimplements the AbstractSceneObject._typeOfNativeObject method to returns the ObjectType of the nativeObject applied
			\param		<Py3dsMax.mxs.Object> nativeObject || None
			\return		<bool> success
		"""
		# Make sure the nativeObject is a OpenMaya.MObject
		# TODO: Move this into a cross3d private function the __new__ factory can call.
		nativeObject = cls._asMOBject(nativeObject)
		with ExceptionRouter():
			apiType = nativeObject.apiType()
			if apiType == om.MFn.kTransform:

				# Checking for model.
				userProps = UserProps(nativeObject)
				if 'model' in userProps and len(cls._mObjName(nativeObject, False).split(':')) > 1:
					return ObjectType.Model
				return ObjectType.Generic

				nativeObject = cls._getShapeNode(nativeObject)
				apiType = nativeObject.apiType()
			
			if apiType in cls._nativeToAbstractObjectType:
				return cls._nativeToAbstractObjectType[apiType]

		return AbstractSceneObject._typeOfNativeObject(nativeObject)
	
	#--------------------------------------------------------------------------------
	#							cross3d public methods
	#--------------------------------------------------------------------------------

	def isHidden(self):
		""" Returns whether or not this object is hidden """
		return not cmds.getAttr('{}.visibility'.format(self._mObjName(self._nativePointer)))
	
	def setHidden(self, state):
		""" Hides/unhides this object """
		return cmds.setAttr('{}.visibility'.format(self._mObjName(self._nativePointer)), not state)

	def namespace(self):
		# I am not re-using the name method on purpose.
		name = self._mObjName(self._nativeTransform, False)

		# Splitting the name to detect for name spaces.
		split = name.split(':')[0:]
		if len(split) > 1:
			return ':'.join(split[:-1])
		return ''

	def setNamespace(self, namespace):
		# I am not re-using the name method on purpose.
		name = self._mObjName(self._nativeTransform, False)
		displayName = name.split(':')[-1]

		if not namespace:
			cmds.rename(self.path(), self.displayName())
		else:
			if not cmds.namespace(exists=namespace):
				cmds.namespace(add=namespace)
			cmds.rename(self.path(), ':'.join([namespace, displayName]))
		return True

	def name(self):
		""" Return the full name of this object, including parent structure """
		return self._mObjName(self._nativeTransform, False)

	def path(self):
		return self._mObjName(self._nativeTransform, True)
	
	def matchTransforms(self, obj, position=True, rotation=True, scale=True):
		""" Currently the auto-key support is a bit lite, but it should cover most of the cases. """
		srcName = obj.path()
		destName = self._mObjName(self._nativeTransform)
		def copyAttr(attrName):
			value = cmds.getAttr('{name}.{attrName}'.format(name=srcName, attrName=attrName))
			cmds.setAttr('{name}.{attrName}'.format(name=destName, attrName=attrName), value)
		
		if position:
			copyAttr('translateX')
			copyAttr('translateY')
			copyAttr('translateZ')
		if rotation:
			copyAttr('rotateX')
			copyAttr('rotateY')
			copyAttr('rotateZ')
		if scale:
			copyAttr('scaleX')
			copyAttr('scaleY')
			copyAttr('scaleZ')

		if application.autokey():
			self.key()
		return True
	
	def parameters(self):
		name = self._mObjName(self._nativePointer)
		parameters = {}
		for attrName in self.propertyNames():
			if attrName not in set([u'translateX', u'translateY', u'translateZ', u'rotateX', u'rotateY', u'rotateZ', u'scaleX', u'scaleY', u'scaleZ']):
				try:
					parameters[attrName] = self.property(attrName)
				except ValueError:
					pass
		return parameters
	
	def setParameters(self, parameters):
		name = self._mObjName(self._nativePointer)
		for key, value in parameters.iteritems():
			try:
				self.setProperty(key, value)
			except:
				print 'TRACEBACK: skipping param: {} {}...'.format(key, value)
				import traceback
				print traceback.format_exc()

	# Overridden to pass the _nativeTransform, not the _nativePointer
	def setParent(self, parent):
		"""Sets the parent for this object to the inputed item
		
		:param parent: :class:`cross3d.SceneObject` or None
		"""
		# set the model in particular
		if (parent and parent.isObjectType(ObjectType.Model)):
			return self._setNativeModel(parent.nativePointer())

		nativeParent = None
		if (parent):
			# NOTE: !!!!!! passing the native transform not the nativePointer
			nativeParent = parent._nativeTransform
		return self._setNativeParent(nativeParent)

	def rotationOrder(self):
		""" Returns the cross3d.constants.RotationOrder enum for this object or zero """
		tform = self._mObjName(self._nativeTransform)
		selected = cmds.getAttr('{}.rotateOrder'.format(tform))
		enumValues = cmds.attributeQuery('rotateOrder', node=tform, listEnum=True)
		if enumValues:
			enumValues = enumValues[0].split(':')
		return RotationOrder.valueByLabel(enumValues[selected].upper())

	def shapes(self):
		""" Returns a generator used to access all shape nodes that are children of this object
		
		Returns:
			generator: SceneObjects representing the shape children of this object
		"""
		for nativeObject in self._getchildShapeNodes(self._nativeTransform):
			yield api.SceneObject(self._scene, nativeObject)

	@classmethod
	def _setNativeRotationOrder(cls, nativePointer, order):
		""" Sets the transform rotation order for the provided object to the provided value.
		
		Args:
			order: cross3d.constants.RotationOrder enum
		"""
		# Set the rotation order for the camera.
		tform = cls._mObjName(cls._asMOBject(nativePointer))
		enumValues = cmds.attributeQuery('rotateOrder', node=tform, listEnum=True)
		if enumValues:
			enumValues = enumValues[0].split(':')
			rotName = RotationOrder.labelByValue(order)
			cmds.setAttr('{}.rotateOrder'.format(tform), enumValues.index(rotName.lower()))

	def setRotationOrder(self, order):
		""" Sets the transform rotation order for this object. 
		
		Args:
			order: cross3d.constants.RotationOrder enum
		"""
		return self._setNativeRotationOrder(self._nativeTransform, order)

# register the symbol
import cross3d
cross3d.registerSymbol('SceneObject', MayaSceneObject)
