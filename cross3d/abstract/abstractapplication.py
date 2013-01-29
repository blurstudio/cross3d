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
	def version(self):
		"""
		Returns the version major of the software.
		
		:return: version number
		:rtyp: int
	
		"""
		return 0

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
	
	

# register the symbol
api.registerSymbol('Application', AbstractApplication, ifNotFound=True)
