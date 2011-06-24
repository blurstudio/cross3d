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
			\remarks	connect application specific callbacks to <blur3d.api.Dispatch>, dispatch will convert the native object to a blur3d.api object
						and emit a signal.
						connect should only be called after blur3d has been initalized.
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
	
	def disconnect(self):
		"""
			\remarks	disconnect application specific callbacks to <blur3d.api.Dispatch>. This will be called when <blur3d.api.Dispatch> is deleted,
						Most likely on reload
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

# register the symbol
from blur3d import api
api.registerSymbol( 'Application', AbstractApplication, ifNotFound = True )