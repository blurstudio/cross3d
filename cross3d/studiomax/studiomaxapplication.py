##
#	\namespace	cross3d.abstract.studiomaxapplication
#
#	\remarks	The StudiomaxApplication class will define all operations for application interaction. It is a singleton class, so calling cross3d.Application() will
#				always return the same instance of Application. One of its main functions is connecting application callbacks to cross3d.Dispatch.
#
#				The StudiomaxApplication is a QObject instance and any changes to the scene data can be controlled by connecting to the signals defined here.
#
#				When subclassing the AbstractScene, methods tagged as @abstractmethod will be required to be overwritten.  Methods tagged with [virtual]
#				are flagged such that additional operations could be required based on the needs of the method.  All @abstractmethod methods MUST be implemented
#				in a subclass.
#
#	\author		Mikeh
#	\author		Blur Studio
#	\date		06/07/11
#

import cross3d
from cross3d.abstract.abstractapplication import AbstractApplication
from Py3dsMax import mxs
from cross3d.enum import EnumGroup, Enum
from Qt.QtCore import QTimer
_n = mxs.pyhelper.namify
dispatch = None

# initialize callback scripts
_STUDIOMAX_CALLBACK_TEMPLATE = """
global cross3d
if ( cross3d == undefined ) do ( cross3d = pymax.import "cross3d" )
if ( cross3d != undefined ) do (
	local ms_args = (callbacks.notificationParam())
	cross3d.%(cls)s.%(function)s "%(signal)s" %(args)s
)
"""
_STUDIOMAX_CALLBACK_TEMPLATE_NO_ARGS = """
global cross3d
if ( cross3d == undefined ) do ( cross3d = pymax.import "cross3d" )
if ( cross3d != undefined ) do (
	cross3d.%(cls)s.%(function)s "%(signal)s"
)
"""
_STUDIOMAX_VIEWPORT_TEMPLATE = """
fn blurfn_%(signal)s =
(
	if ( cross3d == undefined ) do ( cross3d = pymax.import "cross3d" )
	if ( cross3d != undefined ) do (
		cross3d.%(cls)s.%(function)s "%(signal)s"
	)
)
"""

class _ConnectionType(EnumGroup):
	General = Enum()
	Viewport = Enum()

class _ConnectionDef:
	""" Class that stores all neccissary info to connect cross3d.dispatch to StudioMax

	Args:
		signal str: The name of the cross3d.dispatch signal.
		callback str: The name of StudioMax callback.
		arguments str: A string of maxscript arguments passed to signal when the callback is emitted.
		function str: The name of the cross3d.dispatch function. Used in the callback maxscript.
		callbackType _ConnectionType: Controls how the callback is connected to StudioMax.
		cls str: The name of the class called in cross3d. Normally 'dispatch'.
		associated _ConnectionDef: When this signal is connected, all _ConnectionDef's in this list
			are also connected to. This is used by filePostMerge to disable all callbacks durring
			the opening of a file.
	"""
	def __init__(self, signal, callback, arguments='', function='dispatch', callbackType=_ConnectionType.General, cls='dispatch', associated=[]):
		self.signal = signal
		self.callback = callback
		self.arguments = arguments
		self.function = function
		self.callbackType = callbackType
		self.cls = cls
		self.associated = associated

	@staticmethod
	def asDict(signal, callback, arguments = '', function = 'dispatch', callbackType=_ConnectionType.General):
		return {signal:_ConnectionDef(signal, callback, arguments, function, callbackType)}

class _ConnectionStore(object):
	def __init__(self):
		self._store = []

	def update(self, connection):
		self._store.append(connection)

	def getConnectionsBySignalName(self, signal):
		return [c for c in self._store if c.signal == signal]

	def getSignalNames(self):
		return list(set([c.signal for c in self._store]))

class StudiomaxApplication(AbstractApplication):
	# create a mapping of callbacks to be used when connecting signals
	_connectionMap = _ConnectionStore()
	_connectionMap.update(_ConnectionDef('sceneNewRequested', 'systemPreNew'))
	_connectionMap.update(_ConnectionDef('sceneNewFinished', 'systemPostNew'))
	_connectionMap.update(
		_ConnectionDef(
			'sceneOpenRequested',
			'filePreOpen',
			'""',
			function='_prePostCallback',
			cls='application'
		)
	)
	_connectionMap.update(
		_ConnectionDef(
			'sceneOpenFinished',
			'filePostOpen',
			'""',
			function='_prePostCallback',
			cls='application',
			associated=_connectionMap.getConnectionsBySignalName('sceneOpenRequested')
		)
	)
	_connectionMap.update(
		_ConnectionDef(
			'sceneMergeRequested',
			'filePreMerge',
			function='_prePostCallback',
			cls='application'
		)
	)
	_connectionMap.update(_ConnectionDef('sceneReferenceRequested', 'objectXrefPreMerge'))
	_connectionMap.update(_ConnectionDef('sceneReferenceRequested', 'sceneXrefPreMerge'))
	_connectionMap.update(
		_ConnectionDef(
			'sceneMergeFinished',
			'filePostMerge',
			function='_prePostCallback',
			cls='application',
			associated=_connectionMap.getConnectionsBySignalName('sceneMergeRequested')
		)
	)
	_connectionMap.update(_ConnectionDef('sceneReferenceFinished', 'objectXrefPostMerge'))
	_connectionMap.update(_ConnectionDef('sceneReferenceFinished', 'sceneXrefPostMerge'))
	_connectionMap.update(_ConnectionDef('sceneSaveRequested', 'filePreSave', '(if (ms_args != undefined) then (ms_args as string) else "")'))
	_connectionMap.update(_ConnectionDef('sceneSaveFinished', 'filePostSave', '(if (ms_args != undefined) then (ms_args as string) else "")'))
	_connectionMap.update(_ConnectionDef('scenePreReset', 'systemPreReset'))
	_connectionMap.update(_ConnectionDef('sceneReset', 'systemPostReset'))
	_connectionMap.update(_ConnectionDef('layerCreated', 'layerCreated'))
	_connectionMap.update(_ConnectionDef('layerDeleted', 'layerDeleted'))
	_connectionMap.update(_ConnectionDef('startupFinished', 'postSystemStartup'))
	_connectionMap.update(_ConnectionDef('shutdownStarted', 'preSystemShutdown'))
	_connectionMap.update(_ConnectionDef('sceneImportFinished', 'postImport'))
	_connectionMap.update(_ConnectionDef('selectionChanged', 'selectionSetChanged'))
	_connectionMap.update(_ConnectionDef('objectFreeze', 'nodeFreeze', 'ms_args', 'dispatchObject'))
	_connectionMap.update(_ConnectionDef('objectUnfreeze', 'nodeUnfreeze', 'ms_args', 'dispatchObject'))
	_connectionMap.update(_ConnectionDef('objectHide', 'nodeHide', 'ms_args', 'dispatchObject'))
	_connectionMap.update(_ConnectionDef('objectUnHide', 'nodeUnHide', 'ms_args', 'dispatchObject'))
	_connectionMap.update(_ConnectionDef('objectRenamed', 'nodeNameSet', '(if (ms_args != undefined) then (#(ms_args[1], ms_args[2], ms_args[3])) else #("", "", ""))', 'dispatchRename'))
	_connectionMap.update(_ConnectionDef('objectCreated', 'nodeCreated', 'ms_args', 'dispatchObject'))
	_connectionMap.update(_ConnectionDef('objectCloned', 'nodeCloned', 'ms_args', 'dispatchObject'))
	_connectionMap.update(_ConnectionDef('objectAdded', 'sceneNodeAdded', 'ms_args', 'dispatchObject'))
	_connectionMap.update(_ConnectionDef('objectPreDelete', 'nodePreDelete', 'ms_args', 'preDelete'))
	_connectionMap.update(_ConnectionDef('objectPostDelete', 'nodePostDelete', function = 'postDelete'))
	_connectionMap.update(_ConnectionDef('objectParented', 'nodeLinked', 'ms_args', 'dispatchObject'))
	_connectionMap.update(_ConnectionDef('objectUnparented', 'nodeUnlinked', 'ms_args', 'dispatchObject'))
	_connectionMap.update(_ConnectionDef('viewportRedrawn', '', function='dispatchFunction', callbackType=_ConnectionType.Viewport))

	def __init__(self):
		super(StudiomaxApplication, self).__init__()
		self._sceneMergeFinishedTimer = QTimer(self)
		self._sceneMergeFinishedTimer.setSingleShot(True)
		self._sceneMergeFinishedTimer.timeout.connect(self._sceneMergeFinishedTimeout)
		# Variable used to prevent emiting signals when a file is being opened.
		self._openingScene = False
		self._disconnectNames = set()

	def _connectStudiomaxSignal(self, connDef, cross3dSignal):
		"""
			\remarks	Responsible for connecting a signal to studiomax
		"""
		# store the maxscript methods needed
		if connDef.callbackType == _ConnectionType.Viewport:
			signal = _STUDIOMAX_VIEWPORT_TEMPLATE % {
				'cls':'dispatch',
				'function':connDef.function,
				'signal':cross3dSignal
			}
			# Ensure that if the old signal existed it is removed before redefining it.
			# If function is undefined it will do nothing
			mxs.unregisterRedrawViewsCallback(getattr(mxs, 'blurfn_%s' % cross3dSignal))
			mxs.execute(signal)
			mxs.registerRedrawViewsCallback(getattr(mxs, 'blurfn_%s' % cross3dSignal))
		else:
			# Connect the callback
			self._addCallback(connDef, cross3dSignal)
			# Connect any associated callbacks using a diffrent ID name allows us to disconnect
			# this signal without affecting any direct connections to the associated callbacks
			for reqDef in connDef.associated:
				self._addCallback(reqDef, reqDef.signal, 'cross3dcallbacks_{}'.format(connDef.callback))

	def _addCallback(self, connDef, cross3dSignal, callbackName='cross3dcallbacks'):
		if connDef.arguments:
			script = _STUDIOMAX_CALLBACK_TEMPLATE % {
				'cls':connDef.cls,
				'function':connDef.function,
				'signal': cross3dSignal,
				'args': connDef.arguments
			}
		else:
			script = _STUDIOMAX_CALLBACK_TEMPLATE_NO_ARGS % {
				'cls':connDef.cls,
				'function':connDef.function,
				'signal': cross3dSignal
			}
		mxs.callbacks.addScript( _n(connDef.callback), script, id = _n(callbackName) )
		self._disconnectNames.add(callbackName)

	def _prePostCallback(self, signal, *args):
		""" Handle pre\post callbacks intelegently to reduce the number of callbacks.
		"""
		if self.shouldBlockSignal(signal, dispatch.signalsBlocked()):
			# Ignore this callback if signals are blocked.
			return
		if signal == 'sceneMergeFinished':
			# Don't just emit this callback. The timer is used to allow the application
			# to call sceneMergeRequested if there is another merge request.
			# This prevents a single merge action emitting 3 sceneMergeFinished callbacks
			self._sceneMergeFinishedTimer.start(1000)
			return
		elif signal == 'sceneMergeRequested':
			# Stop the timer because we started on a new merge.
			# This prevents a single merge action emitting 3 sceneMergeFinished callbacks
			self._sceneMergeFinishedTimer.stop()
			return
		elif signal == 'sceneOpenFinished':
			# Re-Enable sending signals at a application level.
			self._openingScene = False
		elif signal == 'sceneOpenRequested':
			# Disable signals at the application level. This prevents sceneMerge signals
			# from being emitted durring the open process.
			self._openingScene = True
		# Emit the signal as normal.
		dispatch.dispatch(signal, *args)
		# Note: This code doesn't handle custom functions, so if its needed by this system
		# it will have to be added.

	def _sceneMergeFinishedTimeout(self):
		""" Emit the sceneMergeFinished when the timeout expires. """
		dispatch.dispatch('sceneMergeFinished')

	def allowedCharacters(self):
		return 'A-Za-z0-9_. /+*<>=|-'

	def connect(self):
		"""
			\remarks	connect application specific callbacks to <cross3d.Dispatch>, dispatch will convert the native object to a cross3d object
						and emit a signal.
						connect is called when the first <cross3d.Dispatch> signal is connected.
			\return		<bool>	The Connection was successfull
		"""
		global dispatch
		import cross3d
		dispatch = cross3d.dispatch
		return super(StudiomaxApplication, self).connect()

	def connectCallback(self, signal):
		"""
			\remarks	Connects a single callback. This allows cross3d to only have to respond to callbacks that tools actually
						need, instead of all callbacks.
		"""
		if signal in self._connectionMap.getSignalNames():
			connections = self._connectionMap.getConnectionsBySignalName(signal)
			for object in connections:
				self._connectStudiomaxSignal(object, signal)
		else:
			cross3d.logger.debug('Connect: Signal %s has no signal map' % signal)

	def disconnectCallback(self, signal):
		"""
			\remarks	Disconnect a single callback when it is no longer used.
		"""
		if signal in self._connectionMap.getSignalNames():
			connections = self._connectionMap.getConnectionsBySignalName(signal)
			for connDef in connections:
				if connDef.callbackType == _ConnectionType.Viewport:
					mxs.unregisterRedrawViewsCallback(getattr(mxs, 'blurfn_%s' % connDef.signal))
				else:
					mxs.callbacks.removeScripts(_n(connDef.callback), id = _n('cross3dcallbacks'))
					for reqDef in connDef.associated:
						mxs.callbacks.removeScripts(_n(reqDef.callback), id = _n('cross3dcallbacks_{}'.format(connDef.callback)))
		else:
			cross3d.logger.debug('Disconnect: Signal %s has no signal map' % signal)

	def disconnect(self):
		"""
			\remarks	disconnect application specific callbacks to <cross3d.Dispatch>. This will be called when <cross3d.Dispatch> is deleted,
						disconnect is called when the last <cross3d.Dispatch> signal is disconnected.
		"""
		# remove all normal callbacks
		for name in self._disconnectNames:
			mxs.callbacks.removeScripts(id = _n(name))
		self._sceneMergeFinishedTimer.stop()
		# undefine the add callback function
		mxs.cross3daddcallback = None
		# remove the callback pointer to cross3d
		mxs.cross3d = None
		# remove viewport callbacks
		self.disconnectCallback('viewportRedraw')
		return

	def log(self, message):

		# TODO: Can't seem to access the native log message.
		print message
		return True

	def installDir(self):
		""" Returns the path to the application's install directory

		:return: path string
		:rtyp: str
		"""
		return mxs.pathConfig.resolvePathSymbols('$max')

	def isSilent(self):
		"""Returns whether 3ds Max is running in silent mode."""
		return mxs.GetQuietMode()

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

	def name( self ):
		return "StudioMax"

	def version(self, major=True):
		version = mxs.maxVersion()
		if major:
			return int(version[0] / 1000)
		else:
			return '.'.join([unicode(token) for token in version])

	def refresh(self):
		if not self._blockRefresh:
			mxs.completeRedraw()
			return True
		return False

	def year(self):
		return 1998 + self.version()

	def nameSpaceSeparator(self):
		return '.'

	def animationClipExtension(self):
		return 'xaf'

	def sceneFileExtension(self):
		return 'max'

	def shouldBlockSignal(self, signal, default):
		""" Allows the Application to conditionally block a signal.

		Normally you should pass cross3d.dispatch.signalsBlocked() to default.
		In general if default is True this method should just return True. This will
		prevent unexpected signal emits when a script called
		cross3d.dispatch.blockSignals(True) to block all signals.

		Args:
			signal (str): The name of the signal to check if it should be blocked.
			default (bool): Returned if signal doesn't match any requirements.

		Returns:
			bool: If the signal should be blocked.
		"""
		if default:
			# If signals are blocked assume all signals should be blocked
			return default
		if signal == 'sceneOpenFinished':
			return False
		return self._openingScene

	def modelFileExtension(self):
		return self.sceneFileExtension()

	def nameAndVersion( self ):
		version = mxs.maxVersion()
		jobTypeDic = {
				'5100' : "Max5",
				'6000':	 "Max6",
				'7000':	 "Max7",
				'8000':  "Max8",
				'9000':  "Max9",
				'10000': "Max10",
				'11000': "Max2009",
				'12000': "Max2010",
				'14000': "Max2012",
				'16000': "Max2014",
				'18000': "Max2016",
				'default': "Max2014"}
		if jobTypeDic.has_key(str(version[0])):
			jobType = jobTypeDic[str(version[0])]
		else:
			jobType = jobTypeDic['default']

		return jobType

	def id(self):
		"""
			\remarks	implements AbstractScene.softwareId to return a unique version/bits string information that will represent the exact
									version of the software being run.
			\return		<str>
		"""
		mversion 	= mxs.maxVersion()[0]/1000
		sixtyfour	= ''
		if ( mversion > 10 ):
			mversion = 2009 + (mversion-11)		# shifted to years at version 11
		if ( mxs.is64BitApplication() ):
			sixtyfour = '_64'
		return 'MAX%i%s' % (mversion,sixtyfour)

# register the symbol
cross3d.registerSymbol( 'Application', StudiomaxApplication)

# Creating a single instance of Application for all code to use.
cross3d.registerSymbol( 'application', StudiomaxApplication())
