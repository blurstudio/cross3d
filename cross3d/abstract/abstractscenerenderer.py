##
#	\namespace	blur3d.api.abstract.abstractscenerenderer
#
#	\remarks	The AbstractSceneRenderer class provides an interface to editing renderers in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

class AbstractSceneRenderer:
	def __eq__( self, other ):
		"""
			\remarks	compares this instance to another object
			\param		other	<variant>
			\return		<bool> equal
		"""
		if ( isinstance( other, AbstractSceneRenderer ) ):
			return other._nativePointer == self._nativePointer
		return False
		
	def __init__( self, scene, nativeRenderer ):
		"""
			\remarks	initialize the abstract scene renderer
		"""
		self._scene				= scene
		self._nativePointer		= nativeRenderer
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _nativeProperty( self, key, default = None ):
		"""
			\remarks	[abstract] return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty, AbstractScene._fromNativeValue
			\param		key			<str>
			\param		default		<variant>	(auto-converted from the application's native value)
			\return		<variant>
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return default
	
	def _setNativeProperty( self, key, nativeValue ):
		"""
			\remarks	[abstract] set the value of the property defined by the inputed key
			\sa			hasProperty, property, setProperty, AbstractScene._toNativeValue
			\param		key		<str>
			\param		value	<variant>	(pre-converted to the application's native value)
			\retrun		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def edit( self ):
		"""
			\remarks	[abstract] allow the user to edit the renderer
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
		
	def hasProperty( self, key ):
		"""
			\remarks	[abstract] check to see if the inputed property name exists for this renderer
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def rendererName( self ):
		"""
			\remarks	[abstract] return the name of this renderer instance
			\sa			setRendererName
			\return		<str> name
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return ''
	
	def rendererId( self ):
		"""
			\remarks	[abstract] return the unique id for this renderer instance
			\sa			setRendererId
			\return		<int> id
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return 0
	
	def rendererType( self ):
		"""
			\remarks	[abstract] return the renderer type for this instance
			\sa			setRendererType
			\return		<blur3d.constants.RendererType>
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return 0
	
	def nativePointer( self ):
		"""
			\remarks	return the pointer to the native renderer instance
			\return		<variant> nativeRenderer
		"""
		return self._nativePointer
	
	def property( self, key, default = None ):
		"""
			\remarks	return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty
			\param		key			<str>
			\param		default		<variant>		the default value to return if the property is not found
			\return		<variant>
		"""
		return self._scene._fromNativeValue( self._nativeProperty( key, default ) )
	
	def scene( self ):
		"""
			\remarks	return the scene instance that this renderer is linked to
			\return		<blur3d.api.Scene>
		"""
		return self._scene
	
	def setRendererName( self, rendererName ):
		"""
			\remarks	[abstract] set the name of this renderer instance
			\sa			rendererName
			\param		rendererName	<str>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def setRendererId( self, rendererId ):
		"""
			\remarks	[abstract] set the unique id for this renderer instance
			\sa			rendererId
			\param		rendererId <int>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def setRendererType( self, rendererType ):
		"""
			\remarks	[abstract] set the renderer type for this instance to the inputed type
			\sa			rendererType
			\param		rendererType	<blur3d.constants.RendererType>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
		
	def setProperty( self, key, value ):
		"""
			\remarks	set the value of the property defined by the inputed key
			\sa			hasProperty, property, _setNativeProperty
			\param		key		<str>
			\param		value	<variant>
			\retrun		<bool> success
		"""
		return self._setNativeProperty( key, self._scene._toNativeValue( value ) )
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneRenderer', AbstractSceneRenderer, ifNotFound = True )