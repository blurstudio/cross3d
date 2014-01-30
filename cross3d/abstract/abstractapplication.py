"""
The AbstractApplication class will define all operations for application 
interaction. It is a singleton class, so calling blur3d.api.Application() will
always return the same instance of Application. One of its main functions 
is connecting application callbacks to blur3d.api.Dispatch.  The 
AbstractApplication is a QObject instance and any changes to the scene 
data can be controlled by connecting to the signals defined here.  When 
subclassing the AbstractScene, methods tagged as @abstractmethod will be 
required to be overwritten.  Methods tagged with [virtual] are flagged 
such that additional operations could be required based on the needs of 
the method.  All @abstractmethod methods MUST be implemented in a subclass.

"""



from PyQt4.QtCore import QObject
from blur3d import abstractmethod
from blur3d import api


dispatch = None


class AbstractApplication(QObject):
	"""
	The Application class will define all operations for application 
	interaction. It is a singleton class, so calling blur3d.api.Application() will
	always return the same instance of Application. One of its main functions 
	is connecting application callbacks to blur3d.api.Dispatch.  The 
	Application is a QObject instance and any changes to the scene 
	data can be controlled by connecting to the signals defined here.  When 
	subclassing the Scene, methods tagged as @abstractmethod will be 
	required to be overwritten.  Methods tagged with [virtual] are flagged 
	such that additional operations could be required based on the needs of 
	the method.  All @abstractmethod methods MUST be implemented in a subclass.
	
	"""

	_instance = None
	_blockRefresh = False

	def __init__(self):
		QObject.__init__(self)
		self._objectToBeDeleted = None

	def connect(self):
		"""
		Responsible for setting up the application to connect to signals 
		using :meth:`blur3d.api.Dispatch.connectCallback`.  Connect is 
		called when the first :class:`blur3d.api.Dispatch` signal is 
		connected.
		
		:return: connection success
		:rtype: bool
			
		"""
		# create a signal linking between 2 signals
		import blur3d.api
		global dispatch
		dispatch = blur3d.api.dispatch
		dispatch.linkSignals('sceneNewRequested', 'scenePreInvalidated')
		dispatch.linkSignals('sceneOpenRequested', 'scenePreInvalidated')
		dispatch.linkSignals('sceneMergeRequested', 'scenePreInvalidated')
		dispatch.linkSignals('scenePreReset', 'scenePreInvalidated')
		dispatch.linkSignals('sceneImportRequested', 'scenePreInvalidated')

		dispatch.linkSignals('sceneNewFinished', 'sceneInvalidated')
		dispatch.linkSignals('sceneOpenFinished', 'sceneInvalidated')
		dispatch.linkSignals('sceneMergeFinished', 'sceneInvalidated')
		dispatch.linkSignals('sceneReset', 'sceneInvalidated')
		dispatch.linkSignals('sceneImportFinished', 'sceneInvalidated')

		dispatch.linkSignals('objectCreated', 'newObject')
		dispatch.linkSignals('objectCloned', 'newObject')
		dispatch.linkSignals('objectAdded', 'newObject')
		return True

	@abstractmethod
	def connectCallback(self, signal):
		"""
		Connects a single callback. This allows blur3d to only have to
		respond to callbacks that tools actually need, instead of all 
		callbacks.  Called the first time a signal is connected to 
		this callback.
		
		"""
		return

	def disconnect(self):
		"""
		Responsible for disabling all changes made in 
		:meth:`blur3d.api.Application.connect`.  Disconnect is called when 
		the last :class:`blur3d.api.Dispatch` signal is disconnected.
		
		"""
		return

	@abstractmethod
	def disconnectCallback(self, signal):
		"""
		Disconnect a single callback when it is no longer used. Called 
		when the last signal for this callback is disconnected.
		
		"""
		return

	def preDeleteObject(self, *args):
		"""
		Pre-process the object that is going to be deleted.
		"""
		return

	def postDeleteObject(self, *args):
		"""
		Emits the signal that a object has been deleted. This method is 
		used for applications like max that generate a pre and post 
		delete signal.
		
		"""

		dispatch.objectPostDelete.emit()

	@abstractmethod
	def year(self):
		"""
			Returns the version year of the software.
			:return: version number
			:rtyp: int
		"""
		return 0

	@abstractmethod
	def version(self, major=True):
		"""
		Returns the version of the software.
		
		:return: version number
		:rtyp: various
	
		"""
		return 0 if major else '0.0.0'

	@abstractmethod
	def exportAlembic(self, filename, **kwargs):
		return False
	
	@abstractmethod
	def importAlembic(self, filename, **kwargs):
		return False
	
	@abstractmethod
	def installDir(self):
		""" Returns the path to the current application's install directory.
		
		:return: path string
		:rtyp: str
		"""
		import sys
		import os
		return os.path.dirname(sys.executable)
	
	def installDirForApplication(self, appName, version=None, bit=64, language='English'):
		""" Finds the install path for various software installations. Does not need to be
		:param appName: The name of the application
		:param version: The version of the software. Default is None
		:param bit: The bit type to query the registry for(32, 64). Default is 64
		:param language: Optional language that may be required for specific softwares.
		"""
		def registryValue(registry, key, value):
			# Do not want to import _winreg unless it is neccissary
			import _winreg
			aReg = _winreg.ConnectRegistry(None, getattr(_winreg, registry))
			if bit == 32:
				sam = _winreg.KEY_WOW64_32KEY
			else:
				sam = _winreg.KEY_WOW64_64KEY
			try:
				regKey = _winreg.OpenKey(aReg, key, 0, _winreg.KEY_READ | sam)
				return _winreg.QueryValueEx(regKey, value)
			except WindowsError:
				pass
			return ('', 0)
		
		if appName == '3ds Max':
			# map years to version numbers
			versionForYear = {'2008': '10.0', '2009': '11.0', '2010': '12.0', '2011': '13.0', '2012': '14.0', 
								'2013': '15.0', '2014': '16.0'}
			# map languages to ids
			languageIDs = {'English': ('409', 'en-US', 'ENU'), 'French': ('40C', 'fr-FR', 'FRA'), 'German': ('407', 'de-DE', 'DEU'), 
							'Japanese': ('411', 'ja-JP', 'JPN'), 'Korean': ('412', 'ko-KR', 'KOR'), 'Simplified Chinese': ('804', 'zh-CN', 'CHS')}
			version = versionForYear.get(unicode(version), unicode(version))
			langId = languageIDs.get(language, languageIDs['English'])
			# Ensure we get a valid version number
			version = '{}.0'.format(version[:version.find('.')])
			if float(version) >= 15:
				return registryValue('HKEY_LOCAL_MACHINE', r'Software\Autodesk\3dsMax\{version}'.format(version=version), 'Installdir')[0]
			else:
				return registryValue('HKEY_LOCAL_MACHINE', r'Software\Autodesk\3dsMax\{version}\MAX-1:{langId}'.format(version=version, langId=langId[0]), 'Installdir')[0]
		return ''
	
	@abstractmethod
	def name(self):
		"""
		Returns the unique name of the software.
		
		"""
		return ''

	@abstractmethod
	def refresh(self):
		return False

	@abstractmethod
	def id(self):
		"""
		Returns a unique version/bits string information that will 
		represent the exact version of the software being run.

		:rtype: str
		
		"""
		return ''

	@abstractmethod
	def nameAndVersion(self):
		"""
		Returns the unique name and version format needed for Assburner.
		
		:rtype: str
		
		"""
		return ''
		
	@abstractmethod
	def log( self, message ):
		pass
	
	def undoContext(self, name):
		"""
		Returns a context guard for the undo stack.  Everything that takes
		place within this context guard will appear as a single undo
		operation in the stack.
		
		"""
		return api.UndoContext(name)
	
	def openUndo(self, name):
		"""
		Opens a new undo context.  It is important that the user takes care
		to call closeUndo() to close the context, even if an error or
		exception occurs; otherwise, the undo stack will remain open and 
		unusable.		
		"""
		api.UndoContext.openUndo(name)
		
	def closeUndo(self):
		"""
			Close the undo context.  This call should always follw a call to
			openUndo().
		"""
		api.UndoContext.closeUndo()
	
	def blockRefresh(self):
		"""
			If returns true, the refresh method will not refresh.
		"""
		return self._blockRefresh

	def setBlockRefresh(self, blockRefresh):
		"""
			If set to true, the refresh method will not refresh.
		"""
		if self._blockRefresh != blockRefresh:
			self._blockRefresh = blockRefresh
			return True
		return False

# register the symbol
api.registerSymbol('Application', AbstractApplication, ifNotFound=True)

# Creating a single instance of Application for all code to use.
api.registerSymbol('application', AbstractApplication(), ifNotFound=True)
