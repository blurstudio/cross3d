##
#	\namespace	cross3d.studiomax.studiomaxsceneobject
#
#	\remarks	The StudiomaxSceneObject class provides the implementation of the AbstractSceneObject class as it applies
#				to 3d Studio Max scenes
#
#	\author		eric
#	\author		Blur Studio
#	\date		03/15/10
#

from Py3dsMax import mxs
from cross3d import UserProps
from cross3d.constants import ObjectType
from cross3d.abstract.abstractsceneobject import AbstractSceneObject

class StudiomaxSceneObject( AbstractSceneObject ):

	_nativeToAbstractObjectType = { 'light'         : ObjectType.Light,
									'camera'        : ObjectType.Camera,
									'Thinking'      : ObjectType.Particle | ObjectType.Thinking,
									'PF_Source'     : ObjectType.Particle,
									'FumeFX'		: ObjectType.FumeFX,
									'GeometryClass' : ObjectType.Geometry,
									'Targetobject'	: ObjectType.CameraInterest }

	_abstractToNativeObjectType = dict((v,k) for k, v in _nativeToAbstractObjectType.iteritems())

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	def _nativeType(self):
		"""
			\remarks	implements the AbstractSceneObject._findNativeChild method as a convinance function to return class
			information as  string


			\param		parent		<Py3dsMax.mxs.Object> nativeObject	(used for recursive searches when necessary)
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		classof 	= mxs.classof
		classN = str(classof (self._nativePointer))

		return classN

	def _findNativeChild( self, name, recursive = False, parent = None ):
		"""
			\remarks	implements the AbstractSceneObject._findNativeChild method to find
						the child by the name and returns it
			\sa			findChild
			\param		name		<str>
			\param		recursive	<bool>
			\param		parent		<Py3dsMax.mxs.Object> nativeObject	(used for recursive searches when necessary)
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		if ( not parent ):
			parent = self._nativePointer

		# loop through all the objects
		for child in parent.children:
			if ( child.name == name ):
				return child

			# if recursive, lookup child nodes
			if ( recursive ):
				found = self._findNativeChild( name, recursive = True, parent = child )
				if ( found ):
					return found

		return None

	def _nativeCaches( self, cacheType = 0 ):
		"""
			\remarks	implements the AbstractSceneObject._nativeCaches method to return a list of the native caches that are applied to this object
			\param		cacheType	<cross3d.constants.CacheType>	fitler by the inputed cache type
			\return		<list> [ <variant> nativeCache, .. ]
		"""
		output = []

		from cross3d.constants import CacheType

		# store maxscript methods used
		classof 	= mxs.classof

		# collect point cache modifiers
		if ( not cacheType or cacheType & CacheType.Point_Cache ):
			cls 	= mxs.Point_Cache
			for modifier in self._nativePointer.modifiers:
				if ( classof(modifier) == cls ):
					output.append(modifier)

		# collect transform cache controllers
		if ( not cacheType or cacheType & CacheType.Transform_Cache ):
			cls 		= mxs.Transform_Cache
			controller	= self._nativePointer.controller
			while ( classof( controller ) == cls ):
				output.append( controller )
				controller = controller.basecontroller

		return output

	def _nativeChildren( self, recursive = False, parent = None, childrenCollector = [] ):
		"""
			\remarks	implements the AbstractSceneObject._nativeChildren method to look up the native children for this object
			\sa			children
			\return		<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
		"""
		if recursive:
			if parent:
				children = parent.children
			else:
				children = self._nativePointer.children
			for child in children:
				childrenCollector.append( child )
				self._nativeChildren( True, child, childrenCollector )
			return childrenCollector
		else:
			return self._nativePointer.children

	def _nativeLayer( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeLayer method to return the native application's layer that the object is on
			\sa			layer, setLayer, _setNativeLayer
			\return		<Py3dsMax.mxs.Layer> nativeLayer || None
		"""
		return self._nativePointer.layer

	def _nativeMaterial( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeMaterial method to return the native material for this object
			\sa			material, setMaterial, _setNativeMaterial
			\return		<Py3dsMax.mxs.Material> nativeMaterial || None
		"""
		return self._nativePointer.material

	def _nativeModel( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeModel method to look up the native model for this object
			\sa			model, setModel, _setNativeModel
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		fullname = self._nativePointer.name
		if ( '.' in fullname ):
			return mxs.getNodeByName( fullname.split('.')[0] )
		return None

	def _nativeParent( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeParent method to look up the native parent for this object
			\sa			parent, setParent, _setNativeParent
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		return self._nativePointer.parent

	def _nativeWireColor( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeWireColor to return the color for the wireframe of this object in the scene
			\sa			setWireColor
			\return		<QColor>
		"""
		return self._nativePointer.wireColor

	def _setNativeController( self, name, nativeController ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeController method to set the controller type at the inputed name to the given controller
			\param		name				<str>
			\param		nativeController	<Py3dMax.mxs.Controller> || None
			\return		<bool> success
		"""
		# set a point cache controller
		if ( name.startswith( 'modifiers[#Point_Cache]' ) ):
			from cross3d.constants import CacheType
			success = False
			# set controllers within the cache system
			for cache in self.caches( CacheType.Point_Cache ):
				if ( cache._setNativeController( name.replace( 'modifiers[#Point_Cache].', '' ), nativeController ) ):
					success = True

			return success

		return AbstractSceneObject._setNativeController( self, name, nativeController )

	def _setNativeLayer( self, nativeLayer ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeLayer method to set the native layer for this object
			\sa			layer, setLayer, _nativeLayer
			\param		<Py3dsMax.mxs.Layer> nativeLayer || None
			\return		<bool> success
		"""
		if ( not nativeLayer ):
			worldlayer = mxs.layerManager.getLayer(0)
			worldlayer.addNodes( [ self._nativePointer ] )
		else:
			nativeLayer.addNodes( [ self._nativePointer ] )

		return True

	def _setNativeMaterial( self, nativeMaterial ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeMaterial method to set the native material for this object
			\sa			material, setMaterial, _nativeMaterial
			\param		<Py3dsMax.mxs.Material> nativeMaterial || None
			\return		<bool> success
		"""
		self._nativePointer.material = nativeMaterial
		return True

	def _setNativeModel( self, nativeModel ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeModel method to set the native model for this object
			\sa			model, setModel, _nativeModel
			\param		<Py3dsMax.mxs.Object> nativeObject || None
			\return		<bool> success
		"""
		model = self._nativeModel()

		# don't process when we need to reset this model
		if ( nativeModel == model ):
			return True

		# otherwise, we need to reparent this node and reset its name
		obj 		= self._nativePointer
		obj.parent 	= nativeModel
		splt 		= obj.name.split( '.' )

		if ( nativeModel and len( splt ) == 2 ):
			obj.name = nativeModel.name + '.' + splt[1]
		elif ( nativeModel ):
			obj.name = nativeModel.name + '.' + obj.name
		elif ( splt == 2 ):
			obj.name = splt[1]

		return True

	def _setNativeParent( self, nativeParent ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeParent method to set the native parent for this object
			\sa			parent, setParent, _nativeParent
			\param		<Py3dsMax.mxs.Object> nativeObject || None
			\return		<bool> success
		"""
		self._nativePointer.parent = nativeParent
		return True

	def _setNativeWireColor( self, color ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeWireColor to sets the wirecolor for the object to the inputed QColor
			\sa			wireColor
			\param		color	<QColor>
			\return		<bool> success
		"""
		self._nativePointer.wireColor = color
		return True

	def _nativeModel( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeModel method to look up the native model for this object
			\sa			children
			\return		<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
		"""
		name = self.name()
		split = name.split( '.' )
		if len( split ) > 1:
			modelName = split[0]
			from cross3d import Scene
			scene = Scene()
			return scene._findNativeObject( modelName )
		return None

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def isDeleted(self):
		return (str(self._nativePointer) == '<Deleted scene node>')

	def boundingBox(self):
		""" Returns a blur3d.lib.cartesian.BoundingBox object representing the bounding box of the SceneObject.
		"""
		from blur3d.lib.cartesian import BoundingBox, Point
		p1, p2 = mxs.nodeGetBoundingBox(self.nativePointer(), mxs.matrix3(1))
		return BoundingBox(Point.newFromMaxPoint(p1), Point.newFromMaxPoint(p2))

	def clone( self ):
		"""
			\remarks	implements the AbstractSceneobject.clone to make a clone of this object in the scene
			\sa			N/A
			\return		<Py3dsMax.mxs.Object>
		"""
		cloneObject = mxs.cross3dhelper.cloneObjects([self._nativePointer], expandHierarchy=True)
		return self.__class__(self.scene(), cloneObject[0])

	def keyframeTimeControllers(self, alembic=True):
		""" Takes all Alembic, PC and TMC time controllers and keyframe their original time controllers.

		This is used as a base setup for further time alterations.

		Returns:
			SceneAnimationController|boolean: The bezier float keyframed controller used to control time.
		"""

		np = self._nativePointer
		timeController = None
		frameRate = self._scene.animationFPS()

		# Processing Alembic controllers.
		alembicControllers = mxs.getClassInstances(mxs.Alembic_Float_Controller, target=np)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Xform, target=np)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Mesh_Geometry, target=np)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Mesh_Normals, target=np)
		for alembicController in alembicControllers:

			# Instantiating if we already computed the time controller.
			if not timeController:

				# Unfortunately the start and end frame of the cache data is not stored on the controller so we have to parse the file.
				import cask
				archive = cask.Archive(str(alembicController.path))
				item = archive.top.children[str(alembicController.identifier)]

				# Sometimes the identifier will point to a Xform object.
				# Unfortunately I did not find a way to access the sample count from there.
				# So instead I am digging through the hierarchy.
				while item.children:
					item = item.children[item.children.keys()[0]]

				properties = item.iobject.getProperties()
				geometry = properties.getProperty(0)
				core = geometry.getProperty(0)
				sampleCount = core.getNumSamples()
				startTime = core.getTimeSampling().getSampleTime(0)
				endTime = core.getTimeSampling().getSampleTime((sampleCount - 1))

				# Creating the controller.
				timeController = mxs.bezier_float()
				frames = [(round(startTime * frameRate), startTime), (round(endTime * frameRate), endTime)]
				for frame, value in frames:
					k = mxs.addNewKey(timeController, frame)
					k.value = value
					k.inTangentType = mxs.pyhelper.namify('linear')
					k.outTangentType = mxs.pyhelper.namify('linear')

			# Assigning the controller.
			mxs.setPropertyController(alembicController, 'time', timeController)

		# Processing TMCs and PCs.
		nativeCaches = mxs.getClassInstances(mxs.Transform_Cache, target=np) + mxs.getClassInstances(mxs.Point_Cache, target=np)
		for nativeCache in nativeCaches:

			# Unfortunately the start and end frame of the cache data is not stored on the controller so we have to parse the file.
			if mxs.classof(nativeCache) == mxs.Point_Cache:
				from blur3d.lib.pclib import PointCacheInfo
				cacheInfo = PointCacheInfo.read(nativeCache.filename, header_only=True)

			elif mxs.classof(nativeCache) == mxs.Transform_Cache:
				# Ensure file exists
				try:
					from blur3d.lib.tmclib import TMCInfo
					cacheInfo = TMCInfo.read(nativeCache.CacheFile, header_only=True)
				except IOError as e:
					print "Cache file does not exist: {0}".format(nativeCache.CacheFile)
					continue

			# Playback type 3 is "Playback Graph".
			nativeCache.playbackType = 3

			# Set the playback frame to a float controller with start and end values pulled from the cache.
			mxs.setPropertyController(nativeCache, 'playbackFrame', mxs.bezier_float())
			timeController = mxs.getPropertyController(nativeCache, 'playbackFrame')

			# Set keys on the playback frame cache that matches the current frame rate.
			duration = cacheInfo.end_frame - cacheInfo.start_frame + 1
			frames = [(cacheInfo.start_frame, 0), (cacheInfo.end_frame, duration)]
			for frame, value in frames:
				key = mxs.addNewKey(timeController, frame)
				key.value = value
				key.inTangentType = mxs.pyhelper.namify('linear')
				key.outTangentType = mxs.pyhelper.namify('linear')

		# Processing XMeshes.
		xMeshes = mxs.getClassInstances(mxs.XMeshLoader, target=np)
		for xMesh in xMeshes:

			# Enable curve playback.
			xMesh.enablePlaybackGraph = True

			# Create a new bezier float controller for the time.
			mxs.setPropertyController(xMesh, 'playbackGraphTime', mxs.bezier_float())
			timeController = mxs.getPropertyController(xMesh, 'playbackGraphTime')

			# Set keys on the playback in and out frames.
			frames = (xMesh.rangeFirstFrame, xMesh.rangeLastFrame)
			for frame in frames:
				key = mxs.addNewKey(timeController, frame)
				key.value = frame
				key.inTangentType = mxs.pyhelper.namify('linear')
				key.outTangentType = mxs.pyhelper.namify('linear')

		# Processing Ray Fire caches.
		rayFireCaches = mxs.getClassInstances(mxs.RF_Cache, target=np)
		for rayFireCache in rayFireCaches:

			# Enable curve playback.
			xMesh.playUseGraph = True

			# Create a new bezier float controller for the time.
			mxs.setPropertyController(rayFireCache, 'playFrame', mxs.bezier_float())
			timeController = mxs.getPropertyController(rayFireCache, 'playFrame')

			# Set keys on the playback in and out frames.
			frames = (xMesh.rangeFirstFrame, xMesh.rangeLastFrame)
			for frame in frames:
				key = mxs.addNewKey(timeController, frame)
				key.value = frame
				key.inTangentType = mxs.pyhelper.namify('linear')
				key.outTangentType = mxs.pyhelper.namify('linear')

		# Returning the time controller if defined.
		if timeController:
			# Making the extrapolation linear.
			linear = mxs.pyhelper.namify('linear')
			mxs.setBeforeORT(timeController, linear)
			mxs.setAfterORT(timeController, linear)
			from cross3d import SceneAnimationController
			return SceneAnimationController(self._scene, timeController)

		return None

	def isBoxMode( self ):
		"""
			\remarks	implements the AbstractSceneObject.isBoxMode to return whether or not this object is in boxMode
			\sa			setBoxMode
			\return		<bool> boxMode
		"""
		return self._nativePointer.boxmode

	def isFrozen( self ):
		"""
			\remarks	implements the AbstractSceneObject.isFrozen to return whether or not this object is frozen(locked)
			\sa			freeze, setFrozen, unfreeze
			\return		<bool> frozen
		"""
		return self._nativePointer.isfrozen

	def isHidden( self ):
		"""
			\remarks	implements the AbstractSceneObject.isHidden to return whether or not this object is hidden
			\sa			hide, setHidden, unhide
			\return		<bool> hidden
		"""
		return self._nativePointer.ishiddeninvpt

	def isSelected( self ):
		"""
			\remarks	implements the AbstractSceneObject.isSelected to return whether or not this object is selected
			\sa			deselect, select, setSelected
			\return		<bool> selected
		"""
		return self._nativePointer.isselected

	def _addNativeController(self, name, group='', tpe=float, default=0.0):

		if not group:
			group = 'Custom_Attributes'

		types = {float: 'float', int:'integer'}

		if tpe in [float, int] and isinstance(default, tpe):

			maxScript = """fn addAttributeToObject obj = (
				attribute = attributes {group} (
					parameters main (
						{name} type:#{tpe} default:{default}
					)
				)
				CustAttributes.add obj attribute #Unique
				return obj.{name}.controller
			)"""

			mxs.execute(maxScript.format(name=name, group=group, tpe=types[tpe], default=default))
			return mxs.addAttributeToObject(self._nativePointer)

		else:
			raise Exception('This method only support ints ')
			return None

	def key(self, target='keyable'):
		"""
			Set keys on the object parameters.
		"""
		mxs.addNewKey(self._nativePointer.controller, mxs.currentTime)

	def transformLocks(self, manipulation=True, keyability=False):
		""" Returns a dictionary of position, rotation and scale values. This dictionary
		can be passed to setTransformsLocks.
		:param manipulation: Flags if manipulation will be affected. Defaults to True.
		:param keyability: Flags if keyability will be affected. Defaults to False. (Not implemented.)
		"""
		ret = {'position': 'xyz', 'rotation': 'xyz', 'scale': 'xyz'}
		if manipulation:
			# in python BitArrays appear to be zero indexed
			keys = {0: ('position', 'x'), 1: ('position', 'y'), 2: ('position', 'z'),
				3: ('rotation', 'x'), 4: ('rotation', 'y'), 5: ('rotation', 'z'),
				6: ('scale', 'x'), 7: ('scale', 'y'), 8: ('scale', 'z'), }
			for index, value in enumerate(mxs.getTransformLockFlags(self._nativePointer)):
				if value:
					name, axis = keys[index]
					ret[name] = ret[name].replace(axis, axis.upper())
			return ret
		return False

	def setTransformsLocks(self, position=None, rotation=None, scale=None, manipulation=True, keyability=False):

		if manipulation:

			position = 'XYZ' if position is True else position
			rotation = 'XYZ' if rotation is True else rotation
			scale = 'XYZ' if scale is True else scale

			position = 'xyz' if position is False else position
			rotation = 'xyz' if rotation is False else rotation
			scale = 'xyz' if scale is False else scale

			position = '' if position is None else position
			rotation = '' if rotation is None else rotation
			scale = '' if scale is None else scale

			flags = []
			initialFlags = mxs.getTransformLockFlags(self._nativePointer)

			for i, transform in enumerate((position, rotation, scale)):
				for j, key in enumerate(('x', 'y', 'z')):
					index = j+3*i
					if key.upper() in transform:
						flags.append(index+1)
					elif not key in transform:
						if initialFlags[index]:
							flags.append(index+1)

			return mxs.setTransformLockFlags(self._nativePointer, mxs.pyHelper.tobits(flags))

		return False

	def setBoxMode( self, state ):
		"""
			\remarks	implements the AbstractSceneObject.setBoxMode to set whether this object is in boxMode or not
			\sa			isBoxMode
			\return		<bool> success
		"""
		self._nativePointer.boxmode = state
		return True

	def setFrozen( self, state ):
		"""
			\remarks	implements the AbstractSceneObject.setFrozen to freezes(locks)/unfreezes(unlocks) this object
			\sa			freeze, isFrozen, unfreeze
			\param		state	<bool>
			\return		<bool> success
		"""
		self._nativePointer.isfrozen = state
		return True

	def setHidden( self, state ):
		"""
			\remarks	implements the AbstractSceneObject.setHidden to hides/unhides this object
			\sa			hide, isHidden, unhide
			\param		state	<bool>
			\return		<bool> success
		"""
		self._nativePointer.ishidden = state
		return True

	def setSelected( self, state ):
		"""
			\remarks	implements the AbstractSceneObject.setSelected to selects/deselects this object
			\sa			deselect, isSelected, select
			\param		state	<bool>
			\return		<bool> success
		"""
		self._nativePointer.isselected = state
		return True

	def uniqueId( self ):
		"""
			\remarks	implements the AbstractSceneObject.uniqueId to look up the unique name for this object and returns it
			\sa			displayName, setDisplayName, setName
			\return		<str> name
		"""
		return mxs.blurUtil.uniqueId( self._nativePointer )

	#------------------------------------------------------------------------------------------------------------------------
	# 												static methods
	#------------------------------------------------------------------------------------------------------------------------

	@classmethod
	def _typeOfNativeObject(cls, nativeObject):
		"""
			\remarks	reimplements the AbstractSceneObject._typeOfNativeObject method to returns the ObjectType of the nativeObject applied
			\param		<Py3dsMax.mxs.Object> nativeObject || None
			\return		<bool> success
		"""

		# Checking for model.
		if mxs.classOf(nativeObject) == mxs.Point:
			userProps = UserProps(nativeObject)
			if 'model' in userProps:
				return ObjectType.Model

		output = 	cls._nativeToAbstractObjectType.get(str(mxs.classOf(nativeObject)),
					cls._nativeToAbstractObjectType.get(str(mxs.superClassOf(nativeObject)),
					AbstractSceneObject._typeOfNativeObject(nativeObject)))
		return output

# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneObject', StudiomaxSceneObject )
