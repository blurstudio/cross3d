"""
The AbstractApplication class will define all operations for application 
interaction. It is a singleton class, so calling cross3d.Application() will
always return the same instance of Application. One of its main functions 
is connecting application callbacks to cross3d.Dispatch.  The 
AbstractApplication is a QObject instance and any changes to the scene 
data can be controlled by connecting to the signals defined here.  When 
subclassing the AbstractScene, methods tagged as @abstractmethod will be 
required to be overwritten.  Methods tagged with [virtual] are flagged 
such that additional operations could be required based on the needs of 
the method.  All @abstractmethod methods MUST be implemented in a subclass.

"""

import re

import cross3d
from Qt.QtCore import QObject
from cross3d import abstractmethod
from contextlib import contextmanager

dispatch = None


class AbstractApplication(QObject):
	"""
	The Application class will define all operations for application 
	interaction. It is a singleton class, so calling cross3d.Application() will
	always return the same instance of Application. One of its main functions 
	is connecting application callbacks to cross3d.Dispatch.  The 
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
		using :meth:`cross3d.Dispatch.connectCallback`.  Connect is 
		called when the first :class:`cross3d.Dispatch` signal is 
		connected.
		
		:return: connection success
		:rtype: bool
			
		"""
		# create a signal linking between 2 signals
		import cross3d
		global dispatch
		dispatch = cross3d.dispatch
		dispatch.linkSignals('sceneNewRequested', 'scenePreInvalidated')
		dispatch.linkSignals('sceneOpenRequested', 'scenePreInvalidated')
		dispatch.linkSignals('sceneMergeRequested', 'scenePreInvalidated')
		# dispatch.linkSignals('sceneReferenceRequested', 'scenePreInvalidated')
		dispatch.linkSignals('scenePreReset', 'scenePreInvalidated')
		dispatch.linkSignals('sceneImportRequested', 'scenePreInvalidated')

		dispatch.linkSignals('sceneNewFinished', 'sceneInvalidated')
		dispatch.linkSignals('sceneOpenFinished', 'sceneInvalidated')
		dispatch.linkSignals('sceneMergeFinished', 'sceneInvalidated')
		# dispatch.linkSignals('sceneReferenceFinished', 'sceneInvalidated')
		dispatch.linkSignals('sceneReset', 'sceneInvalidated')
		dispatch.linkSignals('sceneImportFinished', 'sceneInvalidated')

		dispatch.linkSignals('objectCreated', 'newObject')
		dispatch.linkSignals('objectCloned', 'newObject')
		dispatch.linkSignals('objectAdded', 'newObject')
		return True

	@abstractmethod
	def imageSequenceRegex(self):
		return re.compile('')

	def conformObjectName(self, name):
		return re.sub('[^%s]' % self.allowedCharacters(), '_', name)

	@abstractmethod
	def allowedCharacters(self):
		return '.'

	def clipboardCopyText(self, text):
		""" Set the provided text to the system clipboard so it can be pasted
		
		This function is used because QApplication.clipboard sometimes deadlocks in some
		applications like XSI.
		
		Args:
			text (str): Set the text in the paste buffer to this text.
		"""
		from Qt.QtWidgets import QApplication
		QApplication.clipboard().setText(text)

	@abstractmethod
	def connectCallback(self, signal):
		"""
		Connects a single callback. This allows cross3d to only have to
		respond to callbacks that tools actually need, instead of all 
		callbacks.  Called the first time a signal is connected to 
		this callback.
		
		"""
		return

	def disconnect(self):
		"""
		Responsible for disabling all changes made in 
		:meth:`cross3d.Application.connect`.  Disconnect is called when 
		the last :class:`cross3d.Dispatch` signal is disconnected.
		
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
	def autokey(self):
		return False

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
	
	@abstractmethod
	def nameSpaceSeparator(self):
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
	def animationClipExtension(self):
		return ''

	@abstractmethod
	def sceneFileExtension(self):
		return ''

	@abstractmethod
	def modelFileExtension(self):
		return ''

	@abstractmethod
	def nameAndVersion(self):
		"""
		Returns the unique name and version format needed for Assburner.
		
		:rtype: str
		
		"""
		return ''
		
	@abstractmethod
	def log(self, message):
		print message

	def isSilent(self):
		"""
		Returns whether the application is currently running in silent mode.
		"""
		return False
	
	def undoContext(self, name):
		"""
		Returns a context guard for the undo stack.  Everything that takes
		place within this context guard will appear as a single undo
		operation in the stack.
		
		"""
		return cross3d.UndoContext(name)
	
	def openUndo(self, name):
		"""
		Opens a new undo context.  It is important that the user takes care
		to call closeUndo() to close the context, even if an error or
		exception occurs; otherwise, the undo stack will remain open and 
		unusable.		
		"""
		cross3d.UndoContext.openUndo(name)
		
	def closeUndo(self):
		"""
			Close the undo context.  This call should always follw a call to
			openUndo().
		"""
		cross3d.UndoContext.closeUndo()
	
	@contextmanager
	def blockRefreshContext(self, blockRefresh=True):
		orig_blockRefresh = self.blockRefresh()
		self.setBlockRefresh(blockRefresh)
		yield
		self.setBlockRefresh(orig_blockRefresh)
		
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
			cross3d.Scene().setUpdatesEnabled(not blockRefresh)
			return True
		return False

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
		return default

# register the symbol
cross3d.registerSymbol('Application', AbstractApplication, ifNotFound=True)

# Creating a single instance of Application for all code to use.
cross3d.registerSymbol('application', AbstractApplication(), ifNotFound=True)
