import maya.OpenMaya as om
from blur3d.constants import ObjectType
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
		ObjectType.Model: om.MFn.kModel,
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
	
	#--------------------------------------------------------------------------------
	#							blur3d private methods
	#--------------------------------------------------------------------------------
	@classmethod
	def _typeOfNativeObject(cls, nativeObject):
		"""
			\remarks	reimplements the AbstractSceneObject._typeOfNativeObject method to returns the ObjectType of the nativeObject applied
			\param		<Py3dsMax.mxs.Object> nativeObject || None
			\return		<bool> success
		"""
		apiType = nativeObject.apiType()
		if apiType == om.MFn.kTransform:
			apiType = cls._getShapeNode(nativeObject).apiType()
		if apiType in cls._nativeToAbstractObjectType:
			return cls._nativeToAbstractObjectType[apiType]
		return AbstractSceneObject._typeOfNativeObject(nativeObject)

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObject', MayaSceneObject )