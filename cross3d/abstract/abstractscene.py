##
#	\namespace	cross3d.abstract.abstractscene
#
#	\remarks	The AbstractScene class will define all the operations for scene interaction.  Everything for the 3d abstraction layer of the cross3d
#				package will access information from a Scene instance.  This way, you can have a reference to a Studiomax scene, a Softimage scene, a
#				Proxy scene, whatever, and access all generic object, layer, material information in the same way
#
#				The AbstractScene is a QObject instance and any changes to scene data can be controlled by connecting to the signals defined here.
#
#				When subclassing the AbstractScene, methods tagged as @abstractmethod will be required to be overwritten.  Methods tagged with [virtual]
#				are flagged such that additional operations could be required based on the needs of the method.  All @abstractmethod methods MUST be implemented
#				in a subclass.
#
#				The term NativeObject will be used when referring to methods and pointers referencing an application specific instance (Studiomax vs. Softimage
#				for example) vs. one of the cross3d's wrapper objects (SceneObject,SceneLayer,etc.)
#	
#	\author		eric
#	\author		Blur Studio
#	\date		03/15/10
#

import collections as _collections

import cross3d
from Qt.QtCore import QObject, Signal
from cross3d import abstractmethod, constants

class AbstractScene(QObject):
	# layer signals
	layerStateChanged			 = Signal()
	layerCreated				 = Signal(object)
	layerRenamed				 = Signal(object)
	layerRemoved 				 = Signal(object)
	layerGroupCreated			 = Signal(str)
	layerGroupRemoved			 = Signal(str)

	# generic signals
	progressUpdated				 = Signal(str, int, str)		# section, % complete (0-100), message
	progressErrored				 = Signal(str, str)			# section, error message

	# submit signals
	submitSuccess				 = Signal()
	submitError					 = Signal(str)

	# create the scene instance
	_instance = None
	_currentFileName = ''
	
	_updatesDisabled = 0

	def __init__(self):
		QObject.__init__(self)

		# create custom properties
		self._materialCache		 = None
		self._mapCache			 = None
		self._metaData 		     = None
		self._buffer             = {}
		self._state		    	 = {}

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	@abstractmethod
	def _cacheNativeMap(self, cacheType, nativeMap):
		"""Cache the inputed native map in the scene.
		
		:type cacheType: :class:`cross3d.constants.MapCacheType`
		:param nativeMap: variant?
		:return: True if successful, False otherwise
		:rtype: bool
		"""
		return nativeMap

	@abstractmethod
	def _cacheNativeMaterial(self, cacheType, nativeMaterial):
		"""Cache the inputed native material in the scene.
		
		:type cacheType: :class:`cross3d.constants.MaterialCacheType`
		:param nativeMaterial: variant
		:return: True if successful, False otherwise
		:rtype: bool
		"""
		return False

	@abstractmethod
	def _cachedNativeMap(self, cacheType, uniqueId, default=None):
		"""Return the cached native map for the inputed material id.
		
		:type cacheType: :class:`cross3d.constants.MapCacheType`
		:type uniqueId: str
		:param default: value to return if the id was not found
		:rtype: <variant> nativeMap || None
		"""
		return default

	@abstractmethod
	def _cachedNativeMaterial(self, cacheType, uniqueId, default=None):
		"""Return the cached native material for the inputed material id.
		
		:type cacheType: :class:`cross3d.constants.MaterialCacheType`
		:type uniqueId: str
		:param default: value to return if the id was not found
		:rtype: <variant> nativeMaterial || None
		"""
		return default

	@abstractmethod
	def _cachedNativeMaps(self, cacheType):
		"""Return the cached native maps for the inputed cache type.
		
		:type cacheType: :class:`cross3d.constants.MapCacheType`
		:rtype: list of nativeMaps [<variant> nativeMap, ..]
		"""
		return []

	@abstractmethod
	def _cachedNativeMaterials(self, cacheType):
		"""Return the cached native materials for the inputed cache type.
		
		:type cacheType: :class:`cross3d.constants.MaterialCacheType`
		:rtype: list of nativeMaterials [<variant> nativeMaterial, ..]
		"""
		return []

	@abstractmethod
	def _clearNativeMaterialOverride(self, nativeObjects):
		"""Clear the native objects of any material overrides.
		
		:type nativeObjects: list [<variant> nativeObject, ..]
		:return: True if successful, False otherwise
		:rtype: bool
		"""
		return False

	@abstractmethod
	def _clearNativePropSetOverride(self, nativeObjects):
		"""Clear the native objects of any property set overrides
		
		:type nativeObjects: list [<variant> nativeObject, ..]
		:return: True if successful, False otherwise
		:rtype: bool
		"""
		return False

	@abstractmethod
	def _createNativeLayer(self, name, nativeObjects=[]):
		"""Creates a new native layer in this scene based on the inputed name 
		with the given objects.
		
		:type name: str
		:type: nativeObjects: list [<variant> nativeObject, ..]
		:rtype: <variant> nativeLayer || None
		"""
		return None

	@abstractmethod
	def _createNativeLayerGroup(self, name, nativeLayers=[]):
		"""Create a new native layer group in this scene based on the inputed 
		name with the given layers.
		
		:type name: str
		:rtype: <variant> nativeLayerGroup || None
		"""
		return None

	@abstractmethod
	def _createNativeModel(self, name='Model', nativeObjects=[], referenced=False):
		"""
			\remarks	creates and returns a new native 3d model with the inputed name and objects
			\param		name			<str>
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<variant> nativeObject || None
		"""
		return None

	@abstractmethod
	def _createNativeCamera(self, name='Camera', type='Standard', target=None, rotationOrder=None):
		""" Creates and returns a new native 3d camera with the inputed name and objects.
			
			Args:
				name: the name of the camera
				type: The type of camera. Defaults to Standard
				target: The target object. Defaults to None
				rotationOrder: The rotation order of the camera. Defaults to SceneCamera.defaultRotationOrder
			
			Returns:
				nativeCamera || None
		"""
		return None

	@abstractmethod
	def _createNativeRenderer(self, rendererType):
		"""
			\remarks	creates a new native renderer based on the inputed renderer type for this scene
			\param		rendererType	<cross3d.constants.RendererType>
			\return		<variant> nativeRenderer || None
		"""
		return None

	@abstractmethod
	def _createNativeTarget(self, name='Camera.Target'):
		"""
			\remarks	creates a new target object
			\param		name <str>
			\return 	<variant> nativeObject || None
		"""
		return None

	@abstractmethod
	def _currentNativeCamera(self):
		"""
			\remarks	return the current active native camera in the viewport for the scene
			\return		<variant> nativeCamera
		"""
		return None

	@abstractmethod
	def _currentNativeRenderer(self):
		"""
			\remarks	return the current native renderer for this scene instance
			\return		<variant> nativeRenderer || None
		"""
		return None

	@abstractmethod
	def _exportNativeObjects(self, nativeObjects):
		"""
			\remarks	exports the inputed native objects to the given filename
			\param		nativeObjects		<list> [ <variant> nativeObject, .. ]
			\param		filename			<str>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _NativeAtmospheric(self, name='', uniqueId=0):
		"""
			\remarks	look up the native atmospheric from this scene instance
			\param		name	<str>
			\return		<variant> nativeAtmospheric || None
		"""
		return None

	@abstractmethod
	def _NativeFx(self, name='', uniqueId=0):
		"""
			\remarks	look up the native fx from this scene instance
			\param		name	<str>
			\return		<variant> nativeFx || None
		"""
		return None

	@abstractmethod
	def _findNativeObject(self, name='', uniqueId=0):
		"""
			\remarks	looks up a native object based on the inputed name
			\sa			findNativeObject
			\param		name	<str>
			\return		<variant> nativeObject || None
		"""
		return None

	@abstractmethod
	def _findNativeCamera(self, name='', uniqueId=0): # new douglas
		"""
			\remarks	looks up a native camera based on the inputed name
			\sa			findNativeCamera
			\param		name	<str>
			\return		<variant> nativeCamera || None
		"""
		return None

	@abstractmethod
	def _findNativeLayer(self, name='', uniqueId=0):
		"""
			\remarks	looks up a native layer based on the inputed name
			\sa			findNativeLayer
			\param		name	<str>
			\return		<variant> nativeLayer || None
		"""
		return None

	@abstractmethod
	def _findNativeLayerGroup(self, name='', uniqueId=0):
		"""
			\remarks	look up a native layer group based on the inputed name
			\sa			findNativeLayer
			\param		name	<str>
			\return		<variant> nativeLayerGroup || None
		"""
		return None

	@abstractmethod
	def _findNativeMaterial(self, name='', uniqueId=0):
		"""
			\remarks	looks up a native material based on the inputed name
			\sa			findNativeMaterial
			\param		name	<str>
			\return		<variant> nativeMaterial || None
		"""
		return None

	@abstractmethod
	def _findNativeMap(self, name='', uniqueId=0):
		"""
			\remarks	looks up a native map based on the inputed name
			\sa			findNativeMap
			\param		name	<str>
			\return		<variant> nativeMap || None
		"""
		return None

	@abstractmethod
	def _freezeNativeObjects(self, nativeObjects, state):
		"""
			\remarks	freeze(lock)/unfreeze(unlock) a list of native objects
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _fromNativeValue(self, nativeValue):
		"""
			\remarks	converts the inputed value from a native value from whatever application we're in
			\param		nativeValue		<variant>
			\return		<variant>
		"""
		# by default, we assume all conversions have already occurred
		return nativeValue

	@abstractmethod
	def _getNativeObject(self):
		"""
			\remarks	invokes the native application's ability to let a user select a Object from the scene
			\return		<variant> nativeObject || None
		"""
		return None

	@abstractmethod
	def _getNativeMaterial(self):
		"""
			\remarks	invokes the native application's ability to let a user select a Material from the scene
			\return		<variant> nativeMaterial || None
		"""
		return None

	@abstractmethod
	def _getNativeMap(self):
		"""
			\remarks	invokes the native application's ability to let a user select a Map from the scene
			\return		<variant> nativeMap || None
		"""
		return None

	@abstractmethod
	def _hideNativeObjects(self, nativeObjects, state):
		"""
			\remarks	hide/unhide a list of native objects
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _isolateNativeObjects(self, nativeObjects):
		"""
			\remarks	isolate (hide all other objects) or unisolate the inputed objects in the native scene
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _loadNativeMaterialsFromLibrary(self, filename=''):
		"""
			\remarks	loads a bunch of materials from the inputed library location, or prompts the user to select a library when not provided
			\param		filename	<str>
			\return		<list> [ <variant> nativeMaterial, .. ]
		"""
		return []

	@abstractmethod
	def _saveNativeMaterialsToLibrary(self, filename=''):
		"""
			\remarks	saves materials to the given library path
			\param		filename	<str>
			\return		<bool>		success
		"""
		return False

	@abstractmethod
	def _nativeActiveLayer(self):
		"""
			\remarks	returns the native active layer from the scene
			\param		name			<str>
			\return		<variant> nativeLayer || None
		"""
		return None

	@abstractmethod
	def _nativeAtmospherics(self):
		"""
			\remarks	return the native atmospheric instances for this scene
			\return		<list> [ <variant> nativeAtmospheric, .. ]
		"""
		return []

	@abstractmethod
	def _nativeFx(self):
		"""
			\remarks	return the native fx instances for this scene
			\return		<list> [ <variant> nativeFx, .. ]
		"""
		return []

	@abstractmethod
	def _exportNativeModel(self, nativeModel, path):
		"""
			\remarks	exports a specified model to a specific path. added by douglas
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _importNativeModel(self, path, name='', referenced=False, resolution='', load=True, createFile=False):
		"""
			\remarks	import and return a model in the scene. added by douglas
			\return		<PySoftimage.xsi.X3DObject> nativeObject || None
		"""
		return False

	@abstractmethod
	def _nativeCustomProperty(self, key, default=None):
		"""
			\remarks	return the native property for the inputed key
			\param		key			<str>
			\param		default		<variant>
			\return		<variant>
		"""
		return default

	@abstractmethod
	def _nativeEnvironmentMap(self):
		"""
			\remarks	return the current scene environment map
			\return		<variant> nativeMap || None
		"""
		return None

	@abstractmethod
	def _nativeEnvironmentMapOverride(self):
		"""
			\remarks	return the current scene environment map override
			\return		<variant> nativeMap || None
		"""
		return None

	@abstractmethod
	def _nativeLayers(self, wildcard=''):
		"""
			\remarks	returns a list of the native layers in this scene
			\return		<list> [ <variant> nativeLayer, .. ]
		"""
		return []

	@abstractmethod
	def _nativeLayerGroups(self):
		"""
			\remarks	collect all the native layer groups and their corresponding layers
			\sa			layerGroups
			\return		<list> [ <variant> nativeLayerGroup, .. ]
		"""
		return []

	@abstractmethod
	def _nativeMaterials(self, baseMaterials=False):
		"""
			\remarks	collect all the native materials in this scene
			\sa			materials
			\return		<list> [ <variant> nativeMaterial, .. ]
		"""
		return []

	@abstractmethod
	def _nativeMaps(self):
		"""
			\remarks	collect all the native maps in this scene
			\sa			maps
			\return		<list> [ <variant> nativeMap, .. ]
		"""
		return []

	@abstractmethod
	def _nativeObjects(self, getsFromSelection=False, wildcard='', objectType=0):
		""" Returns the native objects from the scene
			:param wildcard: <string>
			:param objectType: cross3d.constants.ObjectType
			:return: <list> [ <variant> nativeObject, .. ]
		"""
		return []

	@abstractmethod
	def _nativeRootObject(self):
		"""
			\remarks	returns the native root object of the scen
			\return		<variant> nativeObject || None
		"""
		return []

	@abstractmethod
	def _nativeWorldLayer(self):
		"""
			\remarks	returns the native world layer from the scene
			\param		name			<str>
			\return		<variant> nativeLayer
		"""
		return None

	@abstractmethod
	def _removeNativeObjects(self, nativeObjects):
		"""
			\remarks	removes the inputed objects from the scene
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _renameNativeObjects(self, nativeObjects, names, display=True):
		"""
			\remarks	removes the inputed objects from the scene
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		names			<list> [ <str> name, .. ]
			\param		display		<bool> 	flags whether or not the names are display names or object names
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setCachedNativeMaps(self, cacheType, nativeMaps):
		"""
			\remarks	set the currently cached maps for the inputed cache type
			\param		cacheType	<cross3d.constants.MapCacheType>
			\param		nativeMaps	<list> [ <variant> nativeMap, .. ]
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setCachedNativeMaterials(self, cacheType, nativeMaterials):
		"""
			\remarks	set the currently cached materials for the inputed cache type
			\param		cacheType			<cross3d.constants.MaterialCacheType>
			\param		nativeMaterials		<list> [ <variant> nativeMaterial, .. ]
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setCurrentNativeCamera(self, nativeCamera):
		"""
			\remarks	set the current viewport camera in the scene to the inputed camera
			\param		<variant> nativeCamera
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setCurrentNativeRenderer(self, nativeRenderer):
		"""
			\remarks	set the current renderer to the inputed native renderer
			\param		nativeRenderer	<variant>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeCustomProperty(self, key, value):
		"""
			\remarks	set the custom property on this scene to the inputed value
			\param		key		<str>
			\param		value	<variant>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeMaterialOverride(self, nativeObjects, nativeMaterial, options=None, advancedState=None):
		"""
			\remarks	set the material override for the inputed objects
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		nativeMaterial	<variant>
			\param		options			<cross3d.constants.MaterialOverrideOptions>
			\param		advancedState	<dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeEnvironmentMap(self, nativeMap):
		"""
			\remarks	set the current environment map in the scene
			\param		nativeMap	<variant>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeEnvironmentMapOverride(self, nativeMap):
		"""
			\remarks	set the current environment map override in the scene
			\param		nativeMap	<variant>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativePropSetOverride(self, nativeObjects, nativePropSet):
		"""
			\remarks	set the overriding property set for the inputed objects to the given property set
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		nativePropSet	<variant>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeSelection(self, nativeObjects):
		"""
			\remarks	selects the inputed native objects in the scene
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeFocus(self, objects):
		"""
			\remarks	sets viewport camera to focus on object
			\param		objects	<list>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _addToNativeSelection(self, nativeObjects):
		"""
			\remarks	add the inputed native objects to the selection in the scene. added by douglas
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _highlightNativeObjects(self, nativeObjects, color=None, tme=.2, branch=True):
		"""
			Highlight the provided objects and their children with a specified color.
		"""
		return False

	@abstractmethod
	def _setNativeUpdatesEnabled(self, state):
		"""
			\remarks	enables/disables scene updates
			\param		state		<bool>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _toggleNativeVisibleState(self, nativeObjects=None, options=None):
		"""
			\remarks	toggle the inputed object's visibility settings based on the inputed options
			\param		nativeObjects	<list> [ <variant> nativeObject, .. ]
			\param		options			<cross3d.constants.VisibilityToggleOptions>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _visibleNativeObjects(self):
		"""
			\remarks	returns the visible objects in the scene
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		return []

	@abstractmethod
	def _nativeRenderPasses(self):
		"""
			\remarks	returns the render passes in the scene. added by douglas
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		return []

	@abstractmethod
	def _findNativeRenderPass(self, displayName=''):
		"""
			\remarks	returns a render pass by it's name. added by douglas. would not need to do that if SceneObject and SceneRenderPass were inheriting from a common lower level class
			\param		<str> displayName
			\return		<variant> nativeObject
		"""
		return None

	@classmethod
	def _findUniqueName(cls, name, names, incFormat='{name}{count:03}', sanityCount=9999999):
		"""
		A generic method to find a unique name in a given set of names.
		:param name: The name to search for in the scene
		:param names: The set of strings to check for a unique name
		:param incFormat: Used to increment the name. Defaults to '{name}{count:03}'
		:param sanityCount: Used to prevent a runaway while loop. Allows you to increase the maximum number of
							objects above 9,999,999 if you really need that.
		"""
		count = 0
		ret = name
		while ret in names:
			count += 1
			ret = incFormat.format(name=name, count=count)
			if sanityCount and count > sanityCount:
				raise Exception('Unable to find a unique name in {} tries, try a diffrent format.'.format(sanityCount))
		return ret

	@abstractmethod
	def _currentNativeRenderPass(self):
		"""
			\remarks	returns the currently active render pass in the scene. added by douglas
			\return		<variant> nativeObject
		"""
		return None

	@abstractmethod
	def _setCurrentNativeRenderPass(self, nativeRenderPass):
		"""
			\remarks	sets the current render pass in the scene. added by douglas
			\param		nativeRenderPass <variant>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _removeNativeRenderPasses(self , nativeRenderPasses):
		"""
			\remarks	removes a render pass in the scene. added by douglas
			\param		nativeRenderPass <variant>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _createNativeRenderPass(self, displayName):
		"""
			\remarks	creates a render pass in the scene. added by douglas
			\param		displayName <str>
			\return		<variant> nativeRenderPass | None
		"""
		return None

	@abstractmethod
	def _removeNativeModels(self, models):
		"""
			\remarks	deletes provided native models. Addded by douglas
			\param		models [ <SceneModel>, ... ]
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def cacheXmesh(self, path, objList, start, end, worldLock, stack=3, saveVelocity=True, ignoreTopology=True):
		"""
			\remarks	deletes provided models. Added by John K.
			\param		models [ <SceneModel>, ... ]
			\return		<bool> success
		"""
		return False

	def _toNativeValue(self, pyValue):
		"""
			\remarks	[virtual] 	converts the inputed value from Qt/Python to whatever value is required for the native application
			\param		pyValue	<variant>
			\return		<variant>
		"""
		from Qt.QtCore import QString

		# we should not pass back QString value's to an application, as they will not expect it.  Standard python strings/unicodes will be auto-converted
		if (type(pyValue) == QString):
			return unicode(pyValue)

		# by default, we assume that any other type can be naturally processed
		return pyValue

	@abstractmethod
	def _viewNativeObjectTrajectory(self, obj):
		"""
			\remarks 	creates a null that allows the user to view an objects trajectory
			\param 		<scene object>	object to get trajectory of
			\return 	<bool> 			success
		"""
		return False

	@abstractmethod
	def _unisolate(self):
		r"""
			\remarks	Exits the isolation mode if it is enabled and returns if it had to exit.
			\return		<bool>
		"""
		return False

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def applyTimeController(self, controller, cachesFrameRate=None, include='', exclude='', bake=False, rnd=0.0):
		""" Applies a controller to all the time controller found in the scene.

		The expected controller should express time in seconds and will be applied as is to alembic modifiers/controllers.
		Any PC, TMC, XMesh or RayFireCache modifiers/controllers will be wired to the alembic ones through a float script that will both reference the alembic controller
		and the frame rate at which we know these point cache have been made. Unfortunately this information cannot be deduced from parsing the PC or TMC file.

		Args:
			controller(SceneAnimationController|FCurve): The controller we want to use for controlling time.
			cacheFrameRate(float): For TMCs, PCs, RayFireCaches there is currently no way to detect the frame rate at which they have been created.
			So if it happens to differ from the one set for that scene, the user will have to provide one.
			include(str): All the objects which name can be found by that regex will be included.
			exclude(str): All the objects which name can be found byt that regex will be excluded.
			bake(bool): If true the PC, TMC, XMesh and RayFireCache stuff will be baked to a curve instead of referencing the curve that drives alembic.
			rnd(float):

		Return:
			boolean: Wherther or not retime was applied with success.
		"""
		if isinstance(controller, api.FCurve):
			fCurve = controller
			nativeController = api.SceneAnimationController._abstractToNativeTypes.get(constants.ControllerType.BezierFloat)()
			controller = api.SceneAnimationController(self, nativeController)
			controller.setFCurve(fCurve)

		elif not isinstance(controller, api.SceneAnimationController):
			raise Exception('Argument 1 should be an instance of SceneAnimationController or FCurve.')

		return self._applyNativeTimeController(controller.nativePointer(), cachesFrameRate=cachesFrameRate, include=include, exclude=exclude, bake=bake, rnd=rnd)

	@abstractmethod
	def _applyNativeTimeController(self, nativeController, cachesFrameRate=None, include='', exclude='', bake=False, rnd=0.0):
		return False

	@abstractmethod
	def undo(self):
		"""
			\remarks    undoes last action
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def retime(self, offset, scale, activeRange, pivot):
		"""
			\remarks    retimes the scene
			\param		offset <int> 
			\param		scale <float>
			\param		activeRange ( <int>, <int> )
			\param		pivot <int>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def setRotation(self, objects, axes, relative=False):
		"""
		Rotates the provided objects in the scene
		:param objects: Rotate these objects
		:param axes: A list with a length of 3 floats representing x, y, z
		:param relative: Apply the rotation as relative or absolute. Absolute by default.
		"""
		return False

	@abstractmethod
	def setSilentMode(self, switch):
		"""
			\remarks	Makes the application silent during intense calls.
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def setTimeControlPlay(self, switch, fromStart=False):
		"""
			\remarks	sets the status of the timeline playback
			\param		switch <bool>
			\param		fromStart <bool>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def setTimeControlLoop(self, switch):
		"""
			\remarks	sets the loop mode of the playback
			\param		switch <bool>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def isTimeControlLoop(self):
		"""
			\remarks	returns if loop mode is active
			\return		<bool> success
		"""
		return False

	@classmethod
	@abstractmethod
	def animationFPS(cls):
		"""
			\remarks	returns the current frame per second rate
			\return		<float> fps
		"""
		return 0.0

	def centerOfObjects(self, objs):
		""" Calculates the center of the bounding boxes of the provided list of SceneObjects
		:param objs: A list of SceneObjects
		:return: A blur3d.lib.cartesian.Point object
		"""
		from blur3d.lib.cartesian import BoundingBox
		aggregateBBox = None
		for obj in objs:
			# We don't care what the bbox coordinates are relative to,
			# so using an identity matrix is fine.
			if aggregateBBox:
				aggregateBBox = BoundingBox.union(
					aggregateBBox,
					obj.boundingBox()
				)
			else:
				aggregateBBox = obj.boundingBox()
		return aggregateBBox.boundingSphere()[0]

	@abstractmethod
	def cloneObjects(self, objects, cloneHierarchy=False, cloneType=constants.CloneType.Copy):
		""" Duplicates the provided objects, optionally keeping the heierarchy.
		:param objects: A list of objects to clone
		:param cloneHierarchy: Duplicate parent child structure in clones. Defaults to False
		:param cloneType: Create clones as copy, instance, etc. Defaults to Copy.
		..seealso:: modules `cross3d.constants.CloneType`
		"""
		return []

	@abstractmethod
	def currentFrame(self):
		"""
			\remarks	returns the current frame
			\return		<int> frame
		"""
		return 0

	@abstractmethod
	def setCurrentFrame(self, frame):
		"""
			\remarks	sets the current frame
			\param		frame <int>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def viewports(self):
		"""
			\remarks	returns all the visible viewports
			\return	  	[ <cross3d.SceneViewport>, ... ]
		"""
		return []

	@abstractmethod
	def animationRange(self):
		"""
			\remarks	return the start and end frames for the animation range for the scene
			\return		<cross3d.FrameRange>
		"""
		from cross3d import FrameRange
		return FrameRange()
	
	@abstractmethod
	def globalRange(self):
		""" Returns a FrameRange of the global start and end range. """
		from cross3d import FrameRange
		return FrameRange()

	@abstractmethod
	def checkForSave(self):
		"""
			\remarks	checks the state of the current scene and queries the user to save if the scene is modified.  If the user cancels the operation,
						this method will return false.  Returns true if the scene is saved, or otherwise is approved by the user to continue the next operation
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def closeRenderSceneDialog(self):
		"""
			\remarks	closes an open render scene dialog
			\sa			openRenderSceneDialog
			\return		<bool> success
		"""
		return False

	@classmethod
	def currentFileName(cls):
		"""
			\remarks	returns the current filename for the scene that is active in the application
			\return		<str>
		"""
		return cls._currentFileName

	@abstractmethod
	def deleteSceneState(self, stateName):
		"""
			\reamrks 	deletes a scene state based on the name given
			\param 		<str>	stateName
			\return 	<boo>	Success
		"""
		return False
	@abstractmethod
	def faceFromMouseClick(self):
		"""Summary
			finds the geometry and face clicked by the user in the viewport
		Returns:
		    TYPE: <tuple> Collision Object and Face Index of Collision
		"""
		return False
	@abstractmethod
	def exportFile(self):
		"""
			\remarks	exports objects from the scene to a file on disk
			\return		N/A
		"""
		pass

	@abstractmethod
	def fileType(self):
		"""
			\remarks	returns the main file type for this type of application
			\return		<str>
		"""
		return ''

	@abstractmethod
	def fileTypes(self):
		"""
			\remarks	returns the associated file types for this type of application
			\return		<list> [ <str>, .. ]
		"""
		return []

	@abstractmethod
	def getSceneState(self, shotName):
		"""
			\remarks	gets the scene state based on name
			\param 		<string> shotName
			\return		<string> name of scene state
		"""
		return False

	@abstractmethod
	def holdCurrentState(self):
		"""
			\remarks	protects the current scene as it is to allow for manipulation and provide a restore point
			\sa			restoreHeldState
		"""
		pass

	@abstractmethod
	def isIsolated(self):
		r"""
			\remarks	Returns if the scene is isolated.
			\return		<bool>
		"""
		return False

	@abstractmethod
	def isSlaveMode(self):
		"""
			\remarks	return whether or not the application is currently being run as a slave
			\return		<bool> state
		"""
		return False

	@abstractmethod
	def keyInTangentType(self):
		"""
			\remarks	return the current in tangent type of the scene
			\return		name
		"""
		pass

	@abstractmethod
	def keyOutTangentType(self):
		"""
			\remarks	return the current out tangent type of the scene
			\return		name
		"""
		pass

	@abstractmethod
	def loadFile(self, filename='', confirm=True):
		"""
			\remarks	loads the inputed filename into the application, returning true on success
			\param		filename	<str>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def openRenderSceneDialog(self):
		"""
			\remarks	opens a render scene dialog
			\sa			closeRenderSceneDialog
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def property(self, key, default=None):
		"""
			\remarks	returns a global scene value
			\param		key			<str> || <QString>
			\param		default		<variant>	default value to return if no value was found
			\return		<variant>
		"""
		return default

	@abstractmethod
	def realizeTimeControllers(self, cachesFrameRate='None'):
		""" Makes all cache play in real time.

		Formats like PCs, TMCs, RayFireCaches, XMeshes are frame based.
		Therefore they will not take scene frame rate into account and preserve duration when playing back.
		This function forces these guys to play in real time by sticking a script in their playback controllers.

		Args:
			cacheFrameRate(float): For TMCs, PCs, RayFireCaches there is currently no way to detect the frame rate at which they have been created.
		"""
		return False

	@abstractmethod
	def renderOutputPath(self):
		"""
			\remarks	return the render output file path for the scene
			\return		<str>
		"""
		return ''

	@abstractmethod
	def renderSavesFile(self):
		"""
			\remarks	return whether render output will be saved to disk
			\sa			setRenderSavesFile
			\return		<bool>
		"""
		return False

	@abstractmethod
	def resetTimeControllers(self):
		""" Removes any alteration done to time controllers.

		This currently supports Alembic, TMCs, PCs, XMeshes, and RayFireCaches caches.

		Returns: 
			boolean: Whether or not the operation was a success.
		"""
		return False

	@abstractmethod
	def rendererType(self):
		return 0

	@abstractmethod
	def renderSize(self):
		"""
			\remarks	return the render output size for the scene
			\return		<QSize>
		"""
		from Qt.QtCore import QSize
		return QSize()

	@abstractmethod
	def reset(self, silent=False):
		"""
			\remarks	resets this scene for all the data and in the application
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def restoreHeldState(self):
		"""
			\remarks	restores a held state after processing code
			\sa			holdCurrentState
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def restoreSceneState(self, stateName, parts):
		"""
			\reamrks 	restores the given aspects of a scene state with the given name
			\param 		<string> 	stateName
			\param 		<list> 		list of apects of state to restore
			\return 	<boo>		success
		"""
		return False

	@abstractmethod
	def setKeyInTangentType(self, tangentType):
		"""
			\remarks	sets the in tangent type for the scene
			\sa			setKeyOutTangentType, keyInTangentType, keyOutTangentType
			\return		N/A
		"""
		pass

	@abstractmethod
	def saveFileAs(self, filename=''):
		"""
			\remarks	saves the current scene to the inputed name specified.  If no name is supplied, then the user should be prompted to pick a filename
			\param		filename 	<str>
			\return		<bool> success
		"""
		return False
		
	@abstractmethod
	def saveCopy( self, path ):
		"""
			\remarks	Saves a copy of the current scene to the inputed name specified.
			\param		filename 	<str>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def saveSceneState(self, stateName, parts):
		"""
			\remarks	Saves the current scene state with the name given
			\param 		<string> stateName
			\return 	<bool> success
		"""
		return False

	@abstractmethod
	def setAnimationFPS(self, fps, changeType=constants.FPSChangeType.Seconds, callback=None):
		"""
			\remarks	Updates the scene's fps to the provided value and scales existing keys as specified.
						If you have any code that you need to run after changing the fps and plan to use it in
						3dsMax you will need to pass that code into the callback argument.
			\param		fps 		<float>
			\param		changeType	<constants.FPSChangeType>	Defaults to constants.FPSChangeType.Frames
			\param		callback	<funciton>					Code called after the fps is changed.
			\return		<bool> success
		"""
		return False

	def setFocus(self, objects):
		"""
			\remarks	sets viewport camera to focus on object
			\param		objects	<list>
			\return		N/A
		"""
		return self._setNativeFocus([obj.nativePointer() for obj in objects])


	@abstractmethod
	def setRenderSavesFile(self, state):
		"""
			\remarks	sets whether render output will be saved to disk
			\sa			renderSavesFile
			\param		state	<bool>
			\return		N/A
		"""
		return False
		
	@abstractmethod
	def storeState( self ):
		"""
			\remarks	stores the state of the scene.
			\return		<bool> success
		"""
		return False
		
	@abstractmethod		
	def restoreState( self ):
		"""
			\remarks	restores the state of the scene based on previously stored state.
			\return		<bool> success
		"""
		return False
		
	@abstractmethod
	def setAnimationRange(self, animationRange, globalRange=None):
		"""
			\remarks	return the start and end frames for the animation range for the scene
			\param		animationRange 	<tuple> ( <int> start, <int> end )
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def setProperty(self, key, value):
		"""
			\remarks	sets the global scene property to the inputed value
			\param		key			<str> || <QString>
			\param		value		<variant>
			\return		<bool>
		"""
		return False

	@abstractmethod
	def setRenderOutputPath(self, outputPath):
		"""
			\remarks	set the render output path for the scene
			\param		outputPath	<str>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def setRenderSize(self, size):
		"""
			\remarks	set the render output size for the scene
			\param		size	<QSize>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def snapKeysToNearestFrames(self):
		"""
			Snaps all keyframes to the nearest frame.
		"""
		return False
		
	@abstractmethod
	def setRenderFrameRange(self, frameRange):
		"""
			\remarks	set the render frame range of the scene
			\param		size	<cross3d.FrameRange>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def setRenderPixelAspect(self, pixelAspect):
		"""
			\remarks	set the render pixel aspect of the scene
			\param		pixelAspect	<int>
			\return		<bool> success
		"""
		return False
		
	@abstractmethod
	def renderPixelAspect(self, ):
		"""
			\remarks	returns the render pixel aspect of the scene
			\return		<int> pixelAspect
		"""
		return 1.0
		
	@abstractmethod
	def setRenderMissingFramesOnly(self, renderMissingFramesOnly ):
		"""
			\remarks	sets if the renderer is rendering missing frames only.
			\param		renderMissingFramesOnly	<bool>
			\return		<bool> success
		"""
		return False
	
	@abstractmethod
	def renderMissingFramesOnly(self):
		"""
			\remarks	gets if the renderer is rendering missing frames only.
			\return		<bool> renderMissingFramesOnly
		"""
		return False

	@abstractmethod
	def exportObjectsToOBJ(self, objects, path, **options):
		return False

	@abstractmethod	
	def _exportNativeObjectsToFBX(self, nativeObjects, path, frameRange=None, showUI=False, frameRate=None, upVector=constants.UpVector.Y, **kwargs):
		"""
			\remarks	exports a given set of nativeObjects as FBX.
			\return		<bool> success
		"""
		return False

	def activeLayer(self):
		"""
			\remarks	returns the currently active layer of the scene
			\return		<cross3d.SceneLayer> || None
		"""
		lay = self._nativeActiveLayer()
		if (lay):
			from cross3d import SceneLayer
			return SceneLayer(self, lay)
		return None

	@abstractmethod
	def animationMixers(self):
		"""Finds all mixers present in the Scene.

		Returns:
					list: A list of Mixer instances for each Mixer in the Scene.
		"""
		return []

	def atmospherics(self):
		"""
			\remarks	returns the atmospheric instances from this scene
			\return		<list> [ <cross3d.SceneAtmospheric>, .. ]
		"""
		from cross3d import SceneAtmospheric
		nativeAtmos = self._nativeAtmospherics()
		return [ SceneAtmospheric(self, atmos) for atmos in nativeAtmos ]

	def cacheMap(self, cacheType, sceneMap):
		"""
			\remarks	cache the inputed map in the scene for the given cache type
			\sa			_cacheNativeMap
			\param		cacheType	<cross3d.constants.MapCacheType>
			\param		sceneMap	<cross3d.SceneMap>
			\return		<bool> success
		"""
		return self._cacheNativeMap(cacheType, sceneMap.nativePointer())
	
	def cacheMaterial(self, cacheType, material):
		"""
			\remarks	cache the inputed material in the scene for the given cache type
			\sa			_cacheNativeMaterial
			\param		cacheType	<cross3d.constants.MaterialCacheType>
			\param		material	<cross3d.SceneMaterial>
			\return		<bool> success
		"""
		return self._cacheNativeMaterial(cacheType, material.nativePointer())

	def cachedMap(self, cacheType, uniqueId, default=None):
		"""
			\remarks	return the cached map given the inputed id
			\sa			_cachedNativeMap
			\param		cacheType	<cross3d.constants.MapCacheType>
			\param		uniqueId		<str>
			\param		default		<variant>	default return value if not found
			\return		<cross3d.SceneMap> || None
		"""
		nativeMap = self._cachedNativeMap(cacheType, uniqueId)
		if (nativeMap):
			from cross3d import SceneMap
			return SceneMap(self, nativeMap)
		return None

	def cachedMaps(self, cacheType):
		"""
			\remarks	return the cached maps for this scene for the given cache type
			\sa			_cachedNativeMaps
			\param		cacheType		<cross3d.constants.MapCacheType>
			\return		<list> [ <cross3d.SceneMap> map, .. ]
		"""
		from cross3d import SceneMap
		return [ SceneMap(self, nativeMap) for nativeMap in self._cachedNativeMaps(cacheType) ]

	def cachedMaterial(self, cacheType, uniqueId, default=None):
		"""
			\remarks	return the cached material given the inputed id
			\sa			_cachedNativeMaterial
			\param		cacheType	<cross3d.constants.MaterialCacheType>
			\param		uniqueId	<str>
			\param		default		<variant>	default return value if not found
			\return		<cross3d.SceneMaterial> || None
		"""
		nativeMaterial = self._cachedNativeMaterial(cacheType, uniqueId, default=default)
		if (nativeMaterial):
			from cross3d import SceneMaterial
			return SceneMaterial(self, nativeMaterial)
		return None

	def cachedMaterials(self, cacheType):
		"""
			\remarks	return the cached materials for this scene given the inputed cache type
			\sa			_cachedNativeMaterials
			\param		cacheType		<cross3d.constants.MaterialCacheType>
			\return		<list> [ <cross3d.SceneMaterial> material, .. ]
		"""
		from cross3d import SceneMaterial
		return [ SceneMaterial(self, material) for material in self._cachedNativeMaterials(cacheType) if material != None ]

	@abstractmethod
	def importFBX(self, path, **kwargs):
		return False

	@abstractmethod
	def importMocapToBiped(self, path, bipedCtrl):
		"""
			\remarks	imports mocap bip file to selected biped
			\param 		path	<string> file path to bip
			\param 		bipedCtrl	<Biped_Object> any part of the biped rig
			\return		<bool> success
		"""
		return False

	def importModel(self, path, name='', referenced=False, resolution='', load=True, createFile=False):
		"""
			\remarks	import and return a model in the scene. added by douglas
			\sa			_importNativeModel
			\return		<cross3d.SceneModel>
		"""
		nativeModel = self._importNativeModel(path, name, referenced, resolution, load, createFile)
		if nativeModel:
			from cross3d import SceneModel
			return SceneModel(self, nativeModel)
		return None

	def clearMaterialOverride(self, objects):
		"""
			\remarks	clear the inputed objects of any material overrides that are applied
			\param		objects		<list> [ <cross3d.SceneObject>, .. ]
			\return		<bool> success
		"""
		return self._clearNativeMaterialOverride([ obj.nativePointer() for obj in objects ])

	def clearPropSetOverride(self, objects):
		"""
			\remarks	clear the inputed objects of any property set overrides that are applied
			\param		objects		<list> [ <cross3d.SceneObject>, .. ]
			\return		<bool> success
		"""
		return self._clearNativePropSetOverride([ obj.nativePointer() for obj in objects ])

	def clearSelection(self):
		"""
			\remarks	clears the selection in the scene
			\sa			setSelection
			\return		<bool> success
		"""
		return self.setSelection([])

	def createObject(self, tpe=constants.ObjectType.Null, name=''):
		from cross3d import SceneObject
		return SceneObject(self, self._createNativeObject(tpe, constants.ObjectType.labelByValue(tpe)))

	@abstractmethod
	def _createNativeObject(self, tpe=constants.ObjectType.Null, name=''):
		return False

	def createRenderer(self, rendererType):
		"""
			\remarks	create a new renderer of the inputed type
			\param		rendererType	<cross3d.constants.RendererType>
			\return		<cross3d.Renderer>
		"""
		nativeRenderer = self._createNativeRenderer(rendererType)
		if (nativeRenderer):
			from cross3d import SceneRenderer
			return SceneRenderer(self, nativeRenderer)
		return None

	def createLayer(self, name, objects=[]):
		"""
			\remarks	creates a new layer with the inputed name and returns it
			\param		name 		<str>
			\param		objects		<list> [ <cross3d.SceneObject>, .. ]
			\return		<cross3d.SceneLayer> || None
		"""
		lay = self._createNativeLayer(name, nativeObjects=[ obj.nativePointer() for obj in objects ])
		if (lay):
			from cross3d import SceneLayer
			layer = SceneLayer(self, lay)
			self.layerCreated.emit(layer)
			return layer
		return None

	def createLayerGroup(self, name, layers=[]):
		"""
			\remarks	create a new group of layers with the inputed names
			\sa			layerGroups, _createNativeLayerGroup
			\param		name		<str>
			\param		layers		<list> [ <cross3d.SceneLayer>, .. ]
			\return		<cross3d.SceneLayerGroup> || None
		"""
		nativeGroup = self._createNativeLayerGroup(name, nativeLayers=[ layer.nativePointer() for layer in layers ])
		if (nativeGroup):
			from cross3d import SceneLayerGroup
			return SceneLayerGroup(self, nativeGroup)
		return None

	def createModel(self, name='Model', objects=[], referenced=False):
		"""
			\remarks	creates a new layer with the inputed name and returns it
			\return		<cross3d.SceneObject> || None
		"""
		nativeModel = self._createNativeModel(name=name, nativeObjects=[obj.nativePointer() for obj in objects], referenced=referenced)
		if (nativeModel):
			from cross3d import SceneObject
			model = SceneObject(self, nativeModel)
			return model
		return None

	def createCamera(self, name='Camera', type='Standard', target=None, rotationOrder=None):
		""" Creates a new camera in the scene.
		
		Args:
			name (str): The name of the camera. Defaults to 'Camera'
			type (str): the type of camera. Defaults to 'Standard'
			target (cross3d.SceneObject): Used as the target of the camera. Defaults to None
			rotationOrder (cross3d.constants.RotationOrder): Rotation order for the camera. Defaults
				to None. If None, it will use the value of SceneCamera.defaultRotationOrder.
		
		Returns:
			cross3d.SceneCamera: The created camera.
		"""
		if target:
			nativeCamera = self._createNativeCamera(
				name=name,
				type=type,
				target=target.nativePointer(),
				rotationOrder=rotationOrder
			)
		else:
			nativeCamera = self._createNativeCamera(name, type, rotationOrder=rotationOrder)
		if (nativeCamera):
			from cross3d import SceneCamera
			return SceneCamera(self, nativeCamera, target=target)
		return None

	def createTurntableCamera(self, name='TurntableCamera', objects=[], type='V-Ray', startFrame=0, endFrame=100):
		"""
			\remarks	creates a new camera that rotates around the given objects
			\return		<cross3d.SceneCamera> || None
		"""
		tName = '{base}.Target'.format(base=name)
		nativeTarget = self._createNativeTarget(name=tName)
		if nativeTarget:
			from cross3d import SceneObject
			target = SceneObject(self, nativeTarget)
			camera = self.createCamera(
				name=name,
				type=type,
				target=target,
			)
		else:
			camera = self.createCamera(
				name=name,
				type=type,
			)
		if not camera:
			return None
		camera.animateTurntable(
			objects=objects,
			startFrame=startFrame,
			endFrame=endFrame,
		)
		return camera

	def currentCamera(self):
		"""
			\remarks	return a SceneCamera instance containing the currently active camera in the scene
			\return		<cross3d.SceneCamera> || None
		"""
		nativeCamera = self._currentNativeCamera()
		if nativeCamera:
			from cross3d import SceneCamera
			return SceneCamera(self, nativeCamera)
		return None

	def currentLayerState(self):
		"""
			\remarks	records the current layer state to xml and returns the string
			\return		<str> layerState
		"""
		from cross3d.migrate.XML import XMLDocument
		doc = XMLDocument()
		self.recordLayerState(doc)
		return doc.toxml()

	def currentRenderer(self):
		"""
			\remarks	return the current renderer assigned to this scene
			\return		<cross3d.SceneRenderer> || None
		"""
		nativeRenderer = self._currentNativeRenderer()
		if (nativeRenderer):
			from cross3d import SceneRenderer
			return SceneRenderer(self, nativeRenderer)
		return None

	def customProperty(self, key, default=None):
		"""
			\remarks	return a custom property in the scene with the given key
			\return		<variant>
		"""
		return self._fromNativeValue(self._nativeCustomProperty(key, default))

	def emitLayerStateChanged(self):
		"""
			\remarks	emits the layerStateChanged signal provided signals are not blocked
		"""
		if (not self.signalsBlocked()):
			self.layerStateChanged.emit()

	def emitProgressUpdated(self, section, percent=100, message=''):
		"""
			\remarks	emits the progress updated signal provided signals are not blocked
			\param		section		<str>	progress section
			\param		percent		<int>	(0-100)
			\param		message		<str>	message to display
		"""
		if (not self.signalsBlocked()):
			self.progressUpdated.emit(section, percent, message)

	def emitProgressErrored(self, section, error):
		"""
			\remarks	emits the progress errored signal to update the error information
			\param		section		<str>		progress section
			\param		error		<str>		error information
		"""
		if (not self.signalsBlocked()):
			self.progressErrored.emit(section, error)

	def emitSubmitError(self, error, progressSection='Submitting Job'):
		"""
			\remarks	emits the submit success signal if the signals are not blocked and cleans the submit process
			\param		error				<str>	resulting error feedback
			\param		progressSection		<str>	the name of the progress section to be updated using emitProgressUpdated
		"""
		from Qt.QtCore import Qt
		from Qt.QtGui import QApplication

		QApplication.instance().restoreOverrideCursor()

		if (not self.signalsBlocked()):
			self.progressErrored.emit(progressSection, error)
			self.submitError.emit(error)

	def emitSubmitSuccess(self, progressSection='Submitting Job'):
		"""
			\remarks	emits the submit success signal if the signals are not blocked and cleans the submit process
			\param		progressSection		<str>	the name of the progress section to be updated using emitProgressUpdated
		"""
		from Qt.QtGui import QApplication

		QApplication.instance().restoreOverrideCursor()

		if (not self.signalsBlocked()):
			self.emitProgressUpdated(progressSection)
			self.submitSuccess.emit()

	def environmentMap(self):
		"""
			\remarks	return the current environment map from the scene
			\sa			setEnvironmentMap, _nativeEnvironmentMap
			\return		<cross3d.SceneMap> || None
		"""
		nativeMap = self._nativeEnvironmentMap()
		if (nativeMap):
			from cross3d import SceneMap
			return SceneMap(self, nativeMap)
		return None

	def environmentMapOverride(self):
		"""
			\remarks	return the current environment map override for this scene
			\sa			setEnvironmentMapOverride, _nativeEnvironmentOverride
			\return		<cross3d.SceneMap> || None
		"""
		nativeMap = self._nativeEnvironmentMapOverride()
		if (nativeMap):
			from cross3d import SceneMap
			return SceneMap(self, nativeMap)
		return None

	def freezeObjects(self, objects, state):
		"""
			\remarks	locks/freezes the inputed nodes based on the state
			\sa			_freezeNativeObjects
			\param		objects		<list> [ <cross3d.SceneObject>, .. ]
			\param		state		<bool>
			\return		<bool> success
		"""
		return self._freezeNativeObjects([ obj.nativePointer() for obj in objects ], state)

	def findAtmospheric(self, name='', uniqueId=0):
		"""
			\remarks	look up an atmospheric based on the inputed name
			\sa			_findNativeAtmospheric
			\param		name	<str>
			\return		<cross3d.SceneAtmospheric> || None
		"""
		nativeAtmos = self._findNativeAtmospheric(name, uniqueId)
		if (nativeAtmos):
			from cross3d import SceneAtmospheric
			return SceneAtmospheric(self, nativeAtmos)
		return None

	def findLayer(self, name='', uniqueId=0):
		"""
			\remarks	looks up a layer based on the inputed name
			\sa			_findNativeLayer
			\param		name	<str>
			\return		<cross3d.SceneLayer> || None
		"""
		nativeLayer = self._findNativeLayer(name, uniqueId)
		if (nativeLayer):
			from cross3d import SceneLayer
			return SceneLayer(self, nativeLayer)
		return None

	def findLayerGroup(self, name='', uniqueId=0):
		"""
			\remarks	look up a layer group based on the inputed name
			\sa			_findNativeLayerGroup
			\param		name	<str>
			\return		<cross3d.SceneLayerGroup> || None
		"""
		nativeLayerGroup = self._findNativeLayerGroup(name, uniqueId)
		if (nativeLayerGroup):
			from cross3d import SceneLayerGroup
			return SceneLayerGroup(self, nativeLayerGroup)
		return None

	def findObject(self, name='', uniqueId=0):
		"""
			\remarks	looks up an individual object by its name
			\sa			_findNativeObject
			\param		name	<str>
			\return		<cross3d.SceneObject> || None
		"""
		nativeObject = self._findNativeObject(name, uniqueId)
		if (nativeObject):
			from cross3d import SceneObject
			return SceneObject(self, nativeObject)
		return None

	def findCamera(self, name='', uniqueId=0): # new douglas
		"""
			\remarks	looks up an individual camera by its name
			\sa			_findNativeCamera
			\param		name	<str>
			\return		<cross3d.SceneCamera> || None
		"""
		nativeCamera = self._findNativeCamera(name, uniqueId)
		if (nativeCamera):
			from cross3d import SceneCamera
			return SceneCamera(self, nativeCamera)
		return None

	def findMaterial(self, name='', uniqueId=0):
		"""
			\remarks	looks up an individual material by its name
			\sa			_findNativeMaterial
			\param		name	<str>
			\return		<cross3d.SceneMaterial> || None
		"""
		if (self._materialCache != None):
			mtl = self._materialCache['id'].get(uniqueId)
			if (not mtl):
				mtl = self._materialCache['name'].get(name)
			return mtl
		else:
			nativeMaterial = self._findNativeMaterial(name, uniqueId)
			if (nativeMaterial):
				from cross3d import SceneMaterial
				return SceneMaterial(self, nativeMaterial)
			return None

	def findMap(self, name='', uniqueId=0):
		"""
			\remarks	looks up an individual map by its name
			\sa			_findNativeMap
			\param		name	<str>
			\return		<cross3d.SceneMap> || None
		"""
		if (self._mapCache != None):
			m = self._mapCache['id'].get(uniqueId)
			if (not m):
				m = self._mapCache['name'].get(name)
			return m
		else:
			nativeMap = self._findNativeMap(name, uniqueId)
			if (nativeMap):
				from cross3d import SceneMap
				return SceneMap(self, nativeMap)
			return None

	def findUniqueObjectName(self, name, incFormat='{name}{count:03}', sanityCount=9999999):
		"""
		Checks the names of the objects in the scene for duplicate names and returns a unique name.lower
		:param name: The name to search for in the scene
		:param incFormat: Used to increment the name. Defaults to '{name}{count:03}'
		:param sanityCount: Used to prevent a runaway while loop. Allows you to increase the maximum number of
							objects above 9,999,999 if you really need that.
		"""
		objects = self.objects(wildcard='{}*'.format(name))
		names = set([o.name() for o in objects])
		return self._findUniqueName(name, names, incFormat=incFormat, sanityCount=sanityCount)

	def fxs(self):
		"""
			\remarks	returns the fx instances from this scene
			\return		<list> [ <cross3d.SceneFx>, .. ]
		"""
		from cross3d import SceneFx
		nativeFxs = self._nativeFxs()
		return [ SceneFx(self, fx) for fx in nativeFxs ]

	def getObject(self):
		"""
			\remarks	invokes the application's ability to let a user select an Object from the scene
			\return		<cross3d.Object> || None
		"""
		from cross3d import SceneObject
		obj = self._getNativeObject()
		if obj:
			return SceneObject(self, obj)
		return None

	def getMaterial(self):
		"""
			\remarks	invokes the application's ability to let a user select a Material from the scene
			\return		<cross3d.SceneMaterial> || None
		"""
		from cross3d import SceneMaterial
		mtl = self._getNativeMaterial()
		if (mtl):
			return SceneMaterial(self, mtl)
		return None

	def getMap(self):
		"""
			\remarks	invokes the application's ability to let a user select a Material from the scene
			\return		<cross3d.SceneMaterial> || None
		"""
		from cross3d import SceneMap
		nativeMap = self._getNativeMap()
		if (nativeMap):
			return SceneMap(self, nativeMap)
		return None

	def hideObjects(self, objects, state):
		"""
			\remarks	hides the inputed objects based on the given state
			\sa			_hideNativeObjects
			\param		objects		<list> [ <cross3d.SceneObject>, .. ]
			\param		state		<bool>
			\return		<bool> success
		"""
		return self._hideNativeObjects([ obj.nativePointer() for obj in objects ], state)

	def highlightObjects(self, objects, color=None, tme=.2, branch=True):
		"""
			\remarks	Hightlight provided object with provided color.
			\sa			_highlightNativeObjects
			\param		objects		<list> [ <cross3d.SceneObject>, .. ]
			\param		color		<QColor>
			\param		state		<bool>
			\return		<bool> success
		"""
		return self._highlightNativeObjects([obj.nativePointer() for obj in objects], color, tme, branch)

	def isEnvironmentMapOverridden(self):
		"""
			\remarks	checks to see if the current environment map is in an overridden state
			\return		<bool> overridden
		"""
		return self._nativeEnvironmentMapOverride() != None

	def isolateObjects(self, objects):
		"""
			\remarks	isolates (hides all other objects) or unisolates the inputed objects in the scene
			\sa			_isolateNativeObjects
			\param		objects		<list> [ <cross3d.SceneObject>, .. ]
			\return		<bool> success
		"""
		return self._isolateNativeObjects([ obj.nativePointer() for obj in objects ])

	def layers(self, wildcard=''):
		"""
			\remarks	collects all the layers in the scene and returns them
			\sa			createLayer, findLayer
			\return		<list> [ <cross3d.SceneLayer>, .. ]
		"""
		from cross3d import SceneLayer
		return [ SceneLayer(self, nativeLayer) for nativeLayer in self._nativeLayers(wildcard) ]

	def layerGroups(self):
		"""
			\remarks	collect all the layer groups and their corresponding layers
			\sa			createLayerGroup, findLayerGroup
			\return		<dict> { <str> name: <list> [ <cross3d.SceneLayer>, .. ], .. }
		"""
		from cross3d import SceneLayerGroup
		return [ SceneLayerGroup(self, nativeLayerGroup) for nativeLayerGroup in self._nativeLayerGroups() ]

	def loadMaterialsFromLibrary(self, filename=''):
		"""
			\remarks	loads all the materials from a given material library file
			\param		filename	<str>
			\return		<list> [ <cross3d.SceneMaterial> ]
		"""
		from cross3d import SceneMaterial
		return [ SceneMaterial(self, nativeMaterial) for nativeMaterial in self._loadNativeMaterialsFromLibrary(filename) ]

	def materials(self, baseMaterials=False):
		"""
			\remarks	returns a list of all the materials in the scene wrapped as SceneMaterials
			\return		<list> [ <cross3d.SceneMaterial>, .. ]
		"""
		from cross3d import SceneMaterial
		return [ SceneMaterial(self, obj) for obj in self._nativeMaterials(baseMaterials) ]

	def maps(self):
		"""
			\remarks	returns a list of all the maps in the scene wrapped as SceneMaps
			\return		<list> [ <cross3d.SceneMap>, .. ]
		"""
		from cross3d import SceneMap
		return [ SceneMap(self, obj) for obj in self._nativeMaps() ]

	@abstractmethod
	def mergeScene(self, path, **options):
		"""
			\remarks	merges a scene file with the current scene.
			\return		<bool> success
		"""
		return None

	def _objects(self, getsFromSelection=False, wildcard='', type=0):
		"""
			\remarks	returns a list of all the objects in the scene wrapped as api objects
			\param		getsFromSelection <bool>
			\param		wildcard <string>
			\param		type <cross3d.constants.ObjectType>
			\return		<list> [ <cross3d.Variant>, .. ]
		"""
		from cross3d import SceneObject
		return [SceneObject(self, obj) for obj in self._nativeObjects(getsFromSelection, wildcard, objectType=type)]

	def saveMaterialsToLibrary(self, filename=''):
		"""
			\remarks	saves materials to a given material library
			\param		filename	<str>
			\return		<bool>		success
		"""
		return self._saveNativeMaterialsToLibrary(filename)

	@abstractmethod
	def select(self):
		"""
			\remarks	launches the application's selection dialog and returns the selected objects
			\return		<list> [<cross3d.Variant>, ..]
		"""
		pass

	def selection(self, wildcard='', type=0):
		"""
			\remarks	returns the currently selected objects from the scene
			\param		wildcard <string>
			\param		type <cross3d.constants.ObjectType>
			\return		<list> [ <cross3d.Variant>, .. ]
		"""
		return self._objects(True, wildcard, type)

	def objects(self, wildcard='', type=0):
		"""
			\remarks	returns a list of all the objects in the scene wrapped as api objects
			\param		wildcard <string>
			\param		type <cross3d.constants.ObjectType>
			\return		<list> [ <cross3d.Variant>, .. ]
		"""
		return self._objects(False, wildcard, type)

	@abstractmethod
	def objectsKeyedFrames(self, objects, start=None, end=None):
		return []

	def recordLayerState(self, xml):
		"""
			\remarks	records the layer state to XML text
			\sa			restoreLayerState, SceneLayer.recordLayerState
			\return		<str>
		"""
		layerState 	 = xml.addNode('layerState')
		layers		 = self.layers()
		for layer in layers:
			layer.recordLayerState(layerState)

	def restoreLayerState(self, xml):
		"""
			\remarks	restores the layer state from the inputed XML text
			\sa			recordLayerState, SceneLayer.restoreLayerState
			\return		<bool> success
		"""
		layerState = xml.findChild('layerState')
		if (not layerState):
			return False

		# create a layer mapping
		layers 			 = self.layers()
		layernamemap 	 = {}
		layeridmap		 = {}
		for layer in layers:
			layernamemap[ str(layer.name()) ] 	 = layer
			layeridmap[ str(layer.uniqueId()) ] 		 = layer

		# create a material caching
		materials		 = self.materials()
		materialcache	 = { 'name': {}, 'id': {} }
		for material in materials:
			materialcache[ 'name' ][ material.name() ] 	 = material
			materialcache[ 'id' ][ material.uniqueId() ] 		 = material

		self._materialCache = materialcache

		# create a map caching
		maps			 = self.maps()
		mapcache		 = { 'name': {}, 'id': {} }
		for m in maps:
			mapcache[ 'name' ][ m.name() ] 	 = map
			mapcache[ 'id' ][ m.uniqueId() ] 		 = map

		self._mapCache = mapcache

		# create the progress dialog
		from Qt.QtGui import QProgressDialog
		progress = QProgressDialog('Loading State', '', 0, len(layers) + 1)
		progress.setWindowTitle('Loading Layer State')
		progress.show()

		# go through the layers in the xml layer state mapping found layers to the scene layers
		processed = []
		for i, layerXml in enumerate(layerState.children()):
			# store the recorded name
			name = layerXml.attribute('name')

			# update the progress dialog
			progress.setValue(i)
			progress.setLabelText('Loading %s...' % name)

			# lookup the layer by name
			if (name in layernamemap):
				layer = layernamemap[name]
				layer.restoreLayerState(layerXml)
				processed.append(layer)
				continue

			# lookup the layer by id
			lid = layerXml.attribute('id')
			if (name in layeridmap):
				layer = layeridmap[name]
				layer.restoreLayerState(layerXml)
				processed.append(layer)
				continue

		# next hide all the layers taht are not part of the state
		unprocessed = [ layer for layer in layers if not layer in processed ]
		progress.setValue(1)
		progress.setMaximum(len(unprocessed) + 1)
		for i, layer in enumerate(unprocessed):
			progress.setValue(i + 1)
			progress.setLabelText('Hiding %s...' % layer.name())

			layer.setHidden(True, affectObjects=True)

		self._materialCache = None
		self._mapCache 		 = None

		return True

	def removeObjects(self, objects):
		"""
			\remarks	removes the objects from the scene
			\sa			_removeNativeObjects
			\param		objects		<list> [ <cross3d.SceneObject>, .. ]
			\return		<bool> success
		"""
		return self._removeNativeObjects([ obj.nativePointer() for obj in objects if not obj.isDeleted()])

	def renameObjects(self, objects, names, display=True):
		"""
			\remarks	renames the inputed objects to the inputed names
			\sa			_renameNativeObjects
			\param		objects		<list> [ <cross3d.SceneObject>, .. ]
			\param		names		<list> [ <str>, .. ]
			\param		display		<bool> 	flags whether or not the names are display names or object names
			\return		<bool> success
		"""
		return self._renameNativeObjects([ object.nativePointer() for object in objects ], names, display=display)

	def rootObject(self):
		"""
			\remarks	returns the root object of the scene
			\return		<cross3d.SceneObject> || None
		"""
		native = self._nativeRootObject()
		if (native):
			from cross3d import SceneObject
			return SceneObject(self, native)
		return None

	def saveFile(self):
		"""
			\remarks	saves the current file
			\return		<bool> success
		"""
		return self.saveFileAs(self.currentFileName())

	@abstractmethod
	def saveSelected(self, path, **options):
		return None

	def setEnvironmentMap(self, sceneMap):
		"""
			\remarks	set the current environment map in the scene to the inputed map
			\sa			environmentMap, _setNativeEnvironmentMap
			\param		sceneMap		<cross3d.SceneMap>
			\return		<bool> success
		"""
		nativeMap = None
		if (sceneMap):
			nativeMap = sceneMap.nativePointer()

		return self._setNativeEnvironmentMap(nativeMap)

	def setEnvironmentMapOverride(self, sceneMap):
		"""
			\remarks	override the current environment map in the scene to the inputed map
			\sa			setEnvironmentMap, _setNativeEnvironmentMapOverride
			\param		sceneMap		<cross3d.SceneMap>
			\return		<bool> success
		"""
		nativeMap = None
		if (sceneMap):
			nativeMap = sceneMap.nativePointer()

		return self._setNativeEnvironmentMapOverride(nativeMap)

	def setCachedMapAt(self, cacheType, index, sceneMap):
		"""
			\remarks	set the cached map for this scene at the inputed index to the given map
			\param		cacheType		<cross3d.constants.MapCacheType>
			\param		index			<int>
			\param		sceneMap		<cross3d.SceneMap> || None
			\return		<bool> success
		"""
		nativeMaps = self._cachedNativeMaps(cacheType)
		if (0 <= index and index < len(nativeMaps)):
			nativeMap = None
			if (sceneMap):
				nativeMap = sceneMap.nativePointer()

			nativeMaps[index] = sceneMap
			self._setCachedNativeMaps(cacheType, nativeMaps)
			return True
		return False

	def setCachedMaps(self, cacheType, sceneMaps):
		"""
			\remarks	set the cached maps for this scene for the given cacheType
			\param		cacheType		<cross3d.constants.MapCacheType>
			\param		sceneMaps		<list> [ <cross3d.SceneMap> map, .. ]
			\return		<bool> success
		"""
		return self._setCachedNativeMaps([sceneMap.nativePointer() for sceneMap in sceneMaps])

	def setCachedMaterialAt(self, cacheType, index, material):
		"""
			\remarks	set the cached material for this scene at the inputed index to the given material
			\param		cacheType		<cross3d.constants.MaterialCacheType>
			\param		index			<int>
			\param		material		<cross3d.SceneMaterial> || None
			\return		<bool> success
		"""
		nativeMaterials = self._cachedNativeMaterials(cacheType)
		if (0 <= index and index < len(nativeMaterials)):
			nativeMaterial = None
			if (material):
				nativeMaterial = material.nativePointer()

			nativeMaterials[index] = material
			self._setCachedNativeMaterials(cacheType, nativeMaterials)
			return True
		return False

	def setCachedMaterials(self, cacheType, materials):
		"""
			\remarks	set the cached materials for this scene for the given cacheType
			\param		cacheType		<cross3d.constants.MaterialCacheType>
			\param		materials		<list> [ <cross3d.SceneMaterial> material, .. ]
			\return		<bool> success
		"""
		return self._setCachedNativeMaterials(cacheType, [ material.nativePointer() for material in materials ])

	def setCurrentCamera(self, camera):
		"""
			\remarks	return a SceneCamera instance containing the currently active camera in the scene
			\param		camera	<cross3d.SceneCamera> || None
			\return		<bool> success
		"""
		nativeCamera = None
		if (camera):
			nativeCamera = camera.nativePointer()

		return self._setCurrentNativeCamera(nativeCamera)

	def setCurrentLayerState(self, layerState):
		"""
			\remarks	restore the layer state from the inputed xml string
			\param		layerState	<str>
			\return		<bool> success
		"""
		from cross3d.migrate.XML import XMLDocument
		doc = XMLDocument()

		doc.parse(layerState)
		
		result = self.restoreLayerState(doc)
		
		return result

	def setCurrentRenderer(self, renderer):
		"""
			\remarks	set the current scene renderer to this class type
			\param		renderer	<cross3d.SceneRenderer>
			\return		<bool> success
		"""
		nativeRenderer = None
		if (renderer):
			nativeRenderer = renderer.nativePointer()
		return self._setCurrentNativeRenderer(nativeRenderer)

	def setCustomProperty(self, key, value):
		"""
			\remarks	set the custom property value for the inputed key in this scene to the given value
			\param		key		<str>
			\param		value	<variant>
			\return		<bool> success
		"""
		return self._setNativeCustomProperty(key, self._toNativeValue(value))

	def setPropSetOverride(self, objects, propSet):
		"""
			\remarks	set the override property set for the inputed objects to the given propset
			\param		objects		<list> [ <cross3d.SceneObject> object, .. ]
			\param		propSet		<cross3d.ScenePropSet>
			\return		<bool> success
		"""
		nativePropSet = None
		if (propSet):
			nativePropSet = propSet.nativePointer()

		return self._setNativePropSetOverride([ obj.nativePointer() for obj in objects ], nativePropSet)

	def setMaterialOverride(self, objects, material, options=None, advancedState=None):
		"""
			\remarks	set the override material for the inputed objects to the given material
			\param		objects		<list> [ <cross3d.SceneObject> object, .. ]
			\param		material	<cross3d.SceneMaterial>
			\param		options		<cross3d.constants.MaterialOverrideOptions>
			\param		advancedState	<dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
		"""
		nativeMaterial = None
		if (material):
			nativeMaterial = material.nativePointer()

		return self._setNativeMaterialOverride([obj.nativePointer() for obj in objects], nativeMaterial, options=options, advancedState=advancedState)

	def setSelection(self, objects, additive=False):
		"""
			\remarks	selects the inputed objects in the scene
			\param		objects		<list> [ <cross3d.SceneObject>, .. ]
			\return		<bool> success
		"""
		if isinstance(objects, basestring):
			return self._addToNativeSelection(objects) if additive else self._setNativeSelection(objects)
		elif isinstance(objects, _collections.Iterable):
			nativeObjects = [obj.nativePointer() for obj in objects]
			return self._addToNativeSelection(nativeObjects) if additive else self._setNativeSelection(nativeObjects)
		raise TypeError('Argument 1 must be str or list of cross3d.SceneObjects')

	def addToSelection(self, objects):
		"""
			\remarks	add the inputed objects to the selection in the scene
			\param		objects		<list> [ <cross3d.SceneObject>, .. ]
			\return		<bool> success
		"""
		if isinstance(objects, basestring):
			return self._addToNativeSelection(objects)
		elif isinstance(objects, _collections.Iterable):
			return self._addToNativeSelection([obj.nativePointer() for obj in objects])
		raise TypeError('Argument 1 must be str or list of cross3d.SceneObjects')

	def setUpdatesEnabled(self, state):
		"""
			\remarks	turns on/off the updating flag for the scene
			\sa			_setNativeUpdatesEnabled, updatesEnabled, update
			\param		state	<bool>
			\return		<bool> whehter or not updates are enabled
		"""
		if (state):
			# dequeue an update call
			self.__class__._updatesDisabled -= 1

			# if the updates have been fully dequeued
			if not self.__class__._updatesDisabled:
				self._setNativeUpdatesEnabled(True)
		else:
			# if the scene is still able to update
			if not self.__class__._updatesDisabled:
				self._setNativeUpdatesEnabled(False)

			self.__class__._updatesDisabled += 1

		return self.updatesEnabled()

	def setUserProps(self, newDict):
		"""
		Ovewrites the current custom properties with the provided dict. You should always build this dict from userProps,
		if you don't it may be possible you will overwrite data stored by other plugins, users, etc.
		:param newDict: dict
		"""
		from cross3d import FileProps
		props = self.userProps()
		props.clear()
		props.update(newDict)

	def toggleVisibleState(self, objects=None, options=None):
		"""
			\remarks	toggle the visible options for the inputed objects
			\param		objects		<list> [ <cross3d.SceneObject> object, .. ]
			\param		options		<cross3d.constants.VisibilityToggleOptions>
			\return		<bool> success
		"""
		nativeObjects = None
		if (objects != None):
			nativeObjects = [ obj.nativePointer() for obj in objects ]

		return self._toggleNativeVisibleState(nativeObjects, options)

	@abstractmethod
	def translate(self, objects, axes, relative=False):
		"""
		Translates the object in the scene
		:param objects: Translate these objects
		:param axes: A list with a length of 3 floats representing x, y, z
		:param relative: Apply the translation as relative or absolute. Absolute by default.
		"""
		return False

	@classmethod
	def updatesEnabled(cls):
		"""
			\remarks	returns whether or not the scene has updates enabled
			\return		<bool> state
		"""
		return cls._updatesDisabled == 0

	def uniqueLayerName(self, basename):
		"""
			\remarks	returns a unique name for a layer in this scene based on the inputed base layer name
			\param		basename	<str>
			\return		<str> unique name
		"""
		names 	 = [ str(layer.name()) for layer in self.layers() ]
		index 	 = 2
		name 	 = basename
		while (name in names):
			name = '%s%02i' % (basename, index)
			index += 1
		return name

	def unisolate(self):
		"""
			\remarks	Ends Isolation mode
			\sa			_unisolate
			\return		<bool> success
		"""
		return self._unisolate()

	def userProps(self):
		"""Returns the FileProps object associated with this file
		:return; :class:`cross3d.FileProps`
		"""
		from cross3d import FileProps
		# Note currentFileName is ignored by most software specific implementations. It is used only
		# for the abstract implementation as we have no application to ask for the current file
		return FileProps(self.currentFileName())

	def viewObjectTrajectory(self, obj):
		"""
			\remarks 	calls the native object trajectory method
			\param 		<scene object>	object to get trajectory of
			\return 	<bool> 			success
		"""
		return self._viewNativeObjectTrajectory(obj.nativePointer())

	def visibleObjects(self):
		"""
			\remarks	returns the objects that are currently visible in the scene
			\return		<list> [ <cross3d.SceneObject>, .. ]
		"""
		from cross3d import SceneObject
		return [ SceneObject(self, nativeObject) for nativeObject in self._visibleNativeObjects() ]

	def worldLayer(self):
		"""
			\remarks	[virtual]	returns the base world layer for the scene
			\return		<cross3d.SceneLayer> || None
		"""
		lay = self._nativeWorldLayer()
		if (lay):
			from cross3d import SceneLayer
			return SceneLayer(self, lay)
		return None

	def renderPasses(self):
		"""
			\remarks	returns render passes of the scene
			\return		<list> [ <cross3d.SceneRenderPass>, .. ]
		"""
		from cross3d import SceneRenderPass
		return [ SceneRenderPass(self, nativeRenderPass) for nativeRenderPass in self._nativeRenderPasses() ]

	def findRenderPass(self, displayName=''):
		"""
			\remarks	returns a render pass based on it's name. would not need to do that if SceneObject and SceneRenderPass were inheriting from a common lower level class
			\return		<cross3d.SceneRenderPass> || None
		"""
		from cross3d import SceneRenderPass
		nativeRenderPass = self._findNativeRenderPass(displayName)
		if nativeRenderPass:
			return SceneRenderPass(self, nativeRenderPass)
		return None

	def currentRenderPass(self):
		"""
			\remarks	returns the active render pass
			\return		<cross3d.SceneRenderPass> || None
		"""
		from cross3d import SceneRenderPass
		return SceneRenderPass(self, self._currentNativeRenderPass())

	def setCurrentRenderPass(self, renderPass):
		"""
			\remarks	sets the active render pass
			\param		renderPass <cross3d.SceneRenderPass>
			\return		<bool> success
		"""
		self._setCurrentNativeRenderPass(renderPass.nativePointer())
		return True

	def removeRenderPasses(self, renderPasses):
		"""
			\remarks	deletes specified render passes
			\param		renderPasses [ <cross3d.SceneRenderPass> ]
			\return		<bool> success
		"""
		return self._removeNativeRenderPasses([ renderPass.nativePointer() for renderPass in renderPasses ])

	def createRenderPass(self, displayName):
		"""
			\remarks	creates a renderpass
			\param		displayName	<str>
			\return		<bool> success
		"""
		from cross3d import SceneRenderPass
		return SceneRenderPass(self, self._createNativeRenderPass(displayName))

	def removeModels(self, models):
		"""
			\remarks	deletes provided models
			\param		models [ <SceneModel>, ... ]
			\return		<bool> success
		"""
		return self._removeNativeModels([ model.nativePointer() for model in models ])

	@abstractmethod
	def retarget(self, inputRigPath, inputAnimationPath, outputRigPath, outputAnimationPath):
		return False

	def viewport(self, viewportID=0):
		"""
			\remarks	returns the specified viewport
			\param		viewportName <string>
			\return	  	<cross3d.SceneViewport> viewport | None
		"""
		from cross3d import SceneViewport
		return SceneViewport(self, viewportID)

	def isAvalaibleName(self, name):
		"""
			\remarks	returns weather a name is already used in a scene
			\param		name <string>
			\return	  	<bool> answer
		"""
		if self._findNativeObject(name):
			return False
		else:
			return True

	def exportObjectsToFBX(self, objects, path, frameRange=None, showUI=True, frameRate=None, upVector=constants.UpVector.Y, **kwargs):
		"""
			\remarks	exports a given set of objects as FBX.
			\return		<bool> success
		"""
		return self._exportNativeObjectsToFBX([obj.nativePointer() for obj in objects], path, frameRange, showUI, frameRate, upVector)

	#------------------------------------------------------------------------------------------------------------------------
	# 												static methods
	#------------------------------------------------------------------------------------------------------------------------

	@staticmethod
	def instance():
		if (not AbstractScene._instance):
			from cross3d import Scene
			AbstractScene._instance = Scene()
		return AbstractScene._instance

	@staticmethod
	def clearInstance():
		AbstractScene._instance = None

# register the symbol
cross3d.registerSymbol('Scene', AbstractScene, ifNotFound=True)
