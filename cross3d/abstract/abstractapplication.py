##
#	\namespace	blur3d.api.abstract.abstractapplication
#
#	\remarks	The AbstractApplication class will define all operations for application interaction. It is a singleton class, so calling blur3d.api.Application() will
#				always return the same instance of Application. One of its main functions is connecting application callbacks to blur3d.api.Dispatch.
#				
#				The AbstractApplication is a QObject instance and any changes to the scene data can be controlled by connecting to the signals defined here.
#
#				When subclassing the AbstractScene, methods tagged as @abstractmethod will be required to be overwritten.  Methods tagged with [virtual]
#				are flagged such that additional operations could be required based on the needs of the method.  All @abstractmethod methods MUST be implemented
#				in a subclass.
#	
#	\author		Mikeh@blur.com
#	\author		Blur Studio
#	\date		06/07/11
#

from blur3d import abstractmethod
from PyQt4.QtCore import QObject
dispatch = None

class AbstractApplication(QObject):
	_instance = None
	def __init__(self):
		QObject.__init__(self)
		self._objectToBeDeleted = None
	
#	def __new__(cls, *args, **kwargs):
#		if not cls._instance:
#			cls._instance = super(AbstractApplication, cls).__new__(cls, *args, **kwargs)
#		return cls._instance

	def connect(self):
		"""
			\remarks	responsible for seting up the application to connect to signals using <blur3d.api.dispatch.connectCallback>
						connect is called when the first <blur3d.api.Dispatch> signal is connected.
			\return		<bool>	the connection was successful
		"""
		# create a signal linking between 2 signals
		import blur3d.api
		global dispatch
		dispatch = blur3d.api.dispatch
		dispatch.linkSignals( 'sceneNewRequested', 'scenePreInvalidated' )
		dispatch.linkSignals( 'sceneOpenRequested', 'scenePreInvalidated' )
		dispatch.linkSignals( 'sceneMergeRequested', 'scenePreInvalidated' )
		dispatch.linkSignals( 'scenePreReset', 'scenePreInvalidated' )
		dispatch.linkSignals( 'sceneImportRequested', 'scenePreInvalidated' )
		
		dispatch.linkSignals( 'sceneNewFinished', 		'sceneInvalidated' )
		dispatch.linkSignals( 'sceneOpenFinished', 		'sceneInvalidated' )
		dispatch.linkSignals( 'sceneMergeFinished',		'sceneInvalidated' )
		dispatch.linkSignals( 'sceneReset',				'sceneInvalidated' )
		dispatch.linkSignals( 'sceneImportFinished',	'sceneInvalidated' )
		
		dispatch.linkSignals( 'objectCreated', 'newObject' )
		dispatch.linkSignals( 'objectCloned', 'newObject' )
		dispatch.linkSignals( 'objectAdded', 'newObject' )
		return True
	
	@abstractmethod
	def connectCallback(self, signal):
		"""
			\remarks	Connects a single callback. This allows blur3d to only have to respond to callbacks that tools actually
						need, instead of all callbacks.
						Called the first time a signal is connected to this callback.
		"""
		return
	
	def disconnect(self):
		"""
			\remarks	responsible for disabling all changes made in <blur3d.api.application.connect>.
						disconnect is called when the last <blur3d.api.Dispatch> signal is disconnected.
		"""
		return
	
	@abstractmethod
	def disconnectCallback(self, signal):
		"""
			\remarks	Disconnect a single callback when it is no longer used. Called when the last signal for this callback is disconnected.
		"""
		return
	
	def preDeleteObject(self, *args):
		"""
			\remarks	Pre-process the object that is going to be deleted.
		"""
		return
	
	def postDeleteObject(self, *args):
		"""
			\remarks	Emits the signal that a object has been deleted. This method is used for applications like max that generate a pre and post delete signal.
		"""
		
		dispatch.objectPostDelete.emit()
	
	@abstractmethod
	def version( self ):
		"""
			\remarks	Returns the version major of the software.
			\return		<int> version
		"""
		return 0
		
	@abstractmethod
	def name( self ):
		"""
			\remarks	returns the name of the software. added by douglas
			\return		<str> unique name
		"""
		return ''
		
	@abstractmethod
	def id( self ):
		"""
			\remarks	returns a unique version/bits string information that will represent the exact
									version of the software being run.
			\return		<str>
		"""
		return ''
		
	@abstractmethod
	def nameAndVersion( self ):
		"""
			\remarks	returns the name and version format needed for Assburner added by John Kosnik
			\return		<str> unique name
		"""
		return ''

# register the symbol
from blur3d import api
api.registerSymbol( 'Application', AbstractApplication, ifNotFound = True )