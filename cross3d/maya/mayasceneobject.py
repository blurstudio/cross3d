import re
import maya.OpenMaya as om
import maya.cmds as cmds
import blurdev
from blur3d.constants import ObjectType, RotationOrder
from blur3d.api import application, UserProps, ExceptionRouter
from blur3d.api.abstract.abstractsceneobject import AbstractSceneObject
						
class MayaSceneObject( AbstractSceneObject ):
	#--------------------------------------------------------------------------------
	#							Init class variables
	#--------------------------------------------------------------------------------
	
	# This enum provides a map between blur3d's objectTypes and OpenMaya.MFn object types.
	# If the values are in a tuple more than one MFn object type needs to map to blur3d's objectType
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
		# _nativeTypePointer stores the specific MFn* object representation of MObject this is
		# used mostly by subclasses of SceneObject
		self._nativeTypePointer = mObj
		# store the transform node so we can access it later
		self._nativeTransform = self._getTransformNode(mObj)
	
	#--------------------------------------------------------------------------------
	#							blur3d private methods
	#--------------------------------------------------------------------------------
	@classmethod
	def _mObjChildren(cls, mObj, recursive=True, regex=None):
		with ExceptionRouter():
			path = om.MDagPath.getAPathTo(mObj)
			for index in range(path.childCount()):
				child = path.child(index)
				if child.apiType() == om.MFn.kTransform:
					if not regex or regex.match(api.SceneObject._mObjName(child)):
						yield child
					if recursive == True:
						for i in cls._mObjChildren(child, regex=regex):
							yield i 
	
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
			blurdev.debug.debugObject(self._nativeChildren, 'type not implemented yet.')
		if parent:
			blurdev.debug.debugObject(self._nativeChildren, 'parent not implemented yet.')
		if childrenCollector:
			blurdev.debug.debugObject(self._nativeChildren, 'childrenCollector not implemented yet.')
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
		namespace = self._namespace(self._nativePointer)['namespace']
		if namespace:
			return self._scene._findNativeObject(name=namespace)
		return None
	
	def _nativeName(self):
		""" A convience method that returns the name of the shape node, not the transform node.
		"""
		return self._mObjName(self._nativePointer, True)
	
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
	
	@classmethod
	def _typeOfNativeObject(cls, nativeObject):
		"""
			\remarks	reimplements the AbstractSceneObject._typeOfNativeObject method to returns the ObjectType of the nativeObject applied
			\param		<Py3dsMax.mxs.Object> nativeObject || None
			\return		<bool> success
		"""
		# Make sure the nativeObject is a OpenMaya.MObject
		# TODO: Move this into a blur3d private function the __new__ factory can call.
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
	#							blur3d public methods
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

	def rotationOrder(self):
		""" Returns the blur3d.constants.RotationOrder enum for this object or zero """
		tform = self._mObjName(self._nativeTransform)
		selected = cmds.getAttr('{}.rotateOrder'.format(tform))
		enumValues = cmds.attributeQuery('rotateOrder', node=tform, listEnum=True)
		if enumValues:
			enumValues = enumValues[0].split(':')
		return RotationOrder.valueByLabel(enumValues[selected].upper())

	@classmethod
	def _setNativeRotationOrder(cls, nativePointer, order):
		""" Sets the transform rotation order for the provided object to the provided value.
		
		Args:
			order: blur3d.constants.RotationOrder enum
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
			order: blur3d.constants.RotationOrder enum
		"""
		return self._setNativeRotationOrder(self._nativeTransform, order)

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObject', MayaSceneObject )