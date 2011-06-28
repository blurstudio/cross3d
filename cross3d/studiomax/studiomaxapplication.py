##
#	\namespace	blur3d.api.abstract.studiomaxapplication
#
#	\remarks	The StudiomaxApplication class will define all operations for application interaction. It is a singleton class, so calling blur3d.api.Application() will
#				always return the same instance of Application. One of its main functions is connecting application callbacks to blur3d.api.Dispatch.
#				
#				The StudiomaxApplication is a QObject instance and any changes to the scene data can be controlled by connecting to the signals defined here.
#
#				When subclassing the AbstractScene, methods tagged as @abstractmethod will be required to be overwritten.  Methods tagged with [virtual]
#				are flagged such that additional operations could be required based on the needs of the method.  All @abstractmethod methods MUST be implemented
#				in a subclass.
#	
#	\author		Mikeh@blur.com
#	\author		Blur Studio
#	\date		06/07/11
#

from blur3d.api.abstract.abstractapplication import AbstractApplication
from Py3dsMax import mxs
from blurdev import debug
dispatch = None

# initialize callback scripts
STUDIOMAX_CALLBACK_TEMPLATE = """
global blur3d
if ( blur3d == undefined ) then ( blur3d = python.import "blur3d" )
if ( blur3d != undefined ) then ( 
	local ms_args = (callbacks.notificationParam())
	blur3d.api.dispatch.%(function)s "%(signal)s" %(args)s 
)
"""

#class ConnectionDef:
#	def __init__(self, signal, callback, arguments = '', function = ''):
#		self.signal = signal
#		self.callback = callback
#		self.arguments = arguments
#		self.function = function
#
#	@staticmethod
#	def asDict(signal, callback, arguments = '', function = ''):
#		return {signal:ConnectionDef(signal, callback, arguments = '', function = '')}

class StudiomaxApplication(AbstractApplication):
	# create a mapping of callbacks to be used when connecting signals
#	_connectionMap = {}
#	_connectionMap.update(ConnectionDef.asDict('sceneNewRequested', 'systemPreNew'))
#	_connectionMap.update(ConnectionDef.asDict('sceneNewFinished', 'systemPostNew'))
#	_connectionMap.update(ConnectionDef.asDict('sceneOpenRequested', 'filePreOpen', '""'))
#	_connectionMap.update(ConnectionDef.asDict('sceneOpenFinished', 'filePostOpen', '""'))
#	_connectionMap.update(ConnectionDef.asDict('sceneMergeRequested', 'filePreMerge'))
#	_connectionMap.update(ConnectionDef.asDict('sceneMergeRequested', 'objectXrefPreMerge'))
#	_connectionMap.update(ConnectionDef.asDict('sceneMergeRequested', 'sceneXrefPreMerge'))
#	_connectionMap.update(ConnectionDef.asDict('sceneMergeFinished', 'filePostMerge'))
#	_connectionMap.update(ConnectionDef.asDict('sceneMergeFinished', 'objectXrefPostMerge'))
#	_connectionMap.update(ConnectionDef.asDict('sceneMergeFinished', 'sceneXrefPostMerge'))
#	_connectionMap.update(ConnectionDef.asDict('sceneSaveRequested', 'filePreSave', '(if (ms_args != undefined) then (ms_args as string) else "")'))
#	_connectionMap.update(ConnectionDef.asDict('sceneSaveFinished', 'filePostSave', '(if (ms_args != undefined) then (ms_args as string) else "")'))
#	_connectionMap.update(ConnectionDef.asDict('scenePreReset', 'systemPreReset'))
#	_connectionMap.update(ConnectionDef.asDict('sceneReset', 'systemPostReset'))
#	_connectionMap.update(ConnectionDef.asDict('layerCreated', 'layerCreated'))
#	_connectionMap.update(ConnectionDef.asDict('layerDeleted', 'layerDeleted'))
#	_connectionMap.update(ConnectionDef.asDict('startupFinished', 'postSystemStartup'))
#	_connectionMap.update(ConnectionDef.asDict('shutdownStarted', 'preSystemShutdown'))
#	_connectionMap.update(ConnectionDef.asDict('sceneImportFinished', 'postImport'))
#	_connectionMap.update(ConnectionDef.asDict('selectionChanged', 'selectionSetChanged'))
#	_connectionMap.update(ConnectionDef.asDict('objectFreeze', 'nodeFreeze', 'ms_args', 'dispatchObject'))
#	_connectionMap.update(ConnectionDef.asDict('objectUnfreeze', 'nodeUnfreeze', 'ms_args', 'dispatchObject'))
#	_connectionMap.update(ConnectionDef.asDict('objectHide', 'nodeHide', 'ms_args', 'dispatchObject'))
#	_connectionMap.update(ConnectionDef.asDict('objectUnHide', 'nodeUnHide', 'ms_args', 'dispatchObject'))
#	_connectionMap.update(ConnectionDef.asDict('objectRenamed', 'nodeNameSet', '(if (ms_args != undefined) then (#(ms_args[1], ms_args[2], ms_args[3])) else #("", "", ""))', 'dispatchRename'))
#	_connectionMap.update(ConnectionDef.asDict('objectCreated', 'nodeCreated', 'ms_args', 'dispatchObject'))
#	_connectionMap.update(ConnectionDef.asDict('objectCloned', 'nodeCloned', 'ms_args', 'dispatchObject'))
#	_connectionMap.update(ConnectionDef.asDict('objectAdded', 'sceneNodeAdded', 'ms_args', 'dispatchObject'))
#	_connectionMap.update(ConnectionDef.asDict('objectPreDelete', 'nodePreDelete', 'ms_args', 'preDelete'))
#	_connectionMap.update(ConnectionDef.asDict('objectPostDelete', 'nodePostDelete', function = 'postDelete'))
#	_connectionMap.update(ConnectionDef.asDict('objectParented', 'nodeLinked', 'ms_args', 'dispatchObject'))
#	_connectionMap.update(ConnectionDef.asDict('objectUnparented', 'nodeUnlinked', 'ms_args', 'dispatchObject'))
	
	def connect(self):
		"""
			\remarks	connect application specific callbacks to <blur3d.api.Dispatch>, dispatch will convert the native object to a blur3d.api object
						and emit a signal.
						connect is called when the first <blur3d.api.Dispatch> signal is connected.
			\return		<bool>	The Connection was successfull
		"""
		global dispatch
		import blur3d.api
		dispatch = blur3d.api.dispatch
		super(StudiomaxApplication, self).connect()
		self.connectStudiomaxSignal( 'systemPreNew',		'sceneNewRequested' )
		self.connectStudiomaxSignal( 'systemPostNew',		'sceneNewFinished' )
		self.connectStudiomaxSignal( 'filePreOpen',			'sceneOpenRequested', 	'""'	)
		self.connectStudiomaxSignal( 'filePostOpen',		'sceneOpenFinished', 	'""' )
		self.connectStudiomaxSignal( 'filePreMerge',		'sceneMergeRequested' )
		self.connectStudiomaxSignal( 'objectXrefPreMerge', 'sceneMergeRequested' )
		self.connectStudiomaxSignal( 'sceneXrefPreMerge', 'sceneMergeRequested' )
		self.connectStudiomaxSignal( 'filePostMerge',		'sceneMergeFinished' )
		self.connectStudiomaxSignal( 'objectXrefPostMerge', 'sceneMergeFinished' )
		self.connectStudiomaxSignal( 'sceneXrefPostMerge', 'sceneMergeFinished' )
		self.connectStudiomaxSignal( 'filePreSave', 		'sceneSaveRequested', 	'(if (ms_args != undefined) then (ms_args as string) else "")' )
		self.connectStudiomaxSignal( 'filePostSave', 		'sceneSaveFinished', 	'(if (ms_args != undefined) then (ms_args as string) else "")' )
		self.connectStudiomaxSignal( 'systemPreReset',		'scenePreReset' )
		self.connectStudiomaxSignal( 'systemPostReset',		'sceneReset' )
		self.connectStudiomaxSignal( 'layerCreated',		'layerCreated' )
		self.connectStudiomaxSignal( 'layerDeleted',		'layerDeleted' )
		self.connectStudiomaxSignal( 'postSystemStartup',	'startupFinished' )
		self.connectStudiomaxSignal( 'preSystemShutdown',	'shutdownStarted' )
		self.connectStudiomaxSignal( 'postImport', 'sceneImportFinished' )
		self.connectStudiomaxSignal('selectionSetChanged', 'selectionChanged')
		self.connectStudiomaxSignal('nodeFreeze', 'objectFreeze', 'ms_args', function = 'dispatchObject')
		self.connectStudiomaxSignal('nodeUnfreeze', 'objectUnfreeze', 'ms_args', function = 'dispatchObject')
		self.connectStudiomaxSignal('nodeHide', 'objectHide', 'ms_args', function = 'dispatchObject')
		self.connectStudiomaxSignal('nodeUnHide', 'objectUnHide', 'ms_args', function = 'dispatchObject')
		self.connectStudiomaxSignal('nodeNameSet', 'objectRenamed', '(if (ms_args != undefined) then (#(ms_args[1], ms_args[2], ms_args[3])) else #("", "", ""))', function = 'dispatchRename')
		self.connectStudiomaxSignal('nodeCreated', 'objectCreated', 'ms_args', function = 'dispatchObject')
		self.connectStudiomaxSignal('nodeCloned', 'objectCloned', 'ms_args', function = 'dispatchObject')
		self.connectStudiomaxSignal('sceneNodeAdded', 'objectAdded', 'ms_args', function = 'dispatchObject')
		self.connectStudiomaxSignal('nodePreDelete', 'objectPreDelete', 'ms_args', function = 'preDelete')
		self.connectStudiomaxSignal('nodePostDelete', 'objectPostDelete', function = 'postDelete')
		self.connectStudiomaxSignal('nodeLinked', 'objectParented', 'ms_args', function = 'dispatchObject')
		self.connectStudiomaxSignal('nodeUnlinked', 'objectUnparented', 'ms_args', function = 'dispatchObject')
		return True
	
#	def connectCallback(self, signal):
#		if signal in self._connectionMap:
#			self.connectStudiomaxSignal(self._connectionMap[signal].callback, signal)
#		else:
#			debug.debugMsg('Signal %s has no signal map' % signal, debug.DebugLevel.Mid)
	
	def connectStudiomaxSignal(self, maxSignal, blurdevSignal, args = '', function = 'dispatch' ):
		# store the maxscript methods needed
		_n = mxs.pyhelper.namify
		mxs.callbacks.addScript( _n(maxSignal), STUDIOMAX_CALLBACK_TEMPLATE % { 'function':function, 'signal': blurdevSignal, 'args': args }, id = _n('blur3dcallbacks') )
	
	def disconnect(self):
		"""
			\remarks	disconnect application specific callbacks to <blur3d.api.Dispatch>. This will be called when <blur3d.api.Dispatch> is deleted,
						disconnect is called when the last <blur3d.api.Dispatch> signal is disconnected.
		"""
		blurdevid 	= mxs.pyhelper.namify('blur3dcallbacks')
		mxs.callbacks.removeScripts(id = blurdevid)
		# undefine the add callback function
		mxs.blur3daddcallback = None
		# remove the callback pointer to blur3d
		mxs.blur3d = None
		return
	
	def preDeleteObject(self, callback, *args):
		"""
			\remarks	Pre-process the object that is going to be deleted.
		"""
		if args:
			self._objectToBeDeleted = args[0].name
	
	def postDeleteObject(self, callback, *args):
		"""
			\remarks	Emits the signal that a object has been deleted. This method is used for applications like max that generate a pre and post delete signal.
		"""
		if self._objectToBeDeleted:
			dispatch.objectDeleted.emit(self._objectToBeDeleted)

	
# register the symbol
from blur3d import api
api.registerSymbol( 'Application', StudiomaxApplication)