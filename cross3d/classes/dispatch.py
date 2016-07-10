"""
Handles conversion of signals between the host software and cross3d

TODO: Only enable or disable signals that have a connection to them
TODO: Only emit a single ScenePreInvalidated/SceneInvalidated signal on 
file operations, using a reference counter

"""

from PyQt4.QtCore import pyqtSignal, QObject

class Dispatch(QObject):
	# scene signals
	sceneClosed				 = pyqtSignal()
	sceneExportRequested	 = pyqtSignal()
	sceneExportFinished		 = pyqtSignal()
	sceneImportRequested	 = pyqtSignal()
	sceneImportFinished		 = pyqtSignal()
	scenePreInvalidated		 = pyqtSignal()			# linked signal before a import, open, or merge operation
	sceneInvalidated		 = pyqtSignal()
	sceneMergeRequested		 = pyqtSignal()
	sceneReferenceRequested	 = pyqtSignal()
	sceneMergeFinished		 = pyqtSignal()
	sceneReferenceFinished   = pyqtSignal()
	sceneNewRequested		 = pyqtSignal()
	sceneNewFinished		 = pyqtSignal()
	sceneOpenRequested		 = pyqtSignal(str)		# <str> The Filename
	sceneOpenFinished		 = pyqtSignal(str)		# <str> The Filename
	scenePreReset			 = pyqtSignal()
	sceneReset				 = pyqtSignal()
	sceneSaveRequested		 = pyqtSignal(str)		# <str> The Filename
	sceneSaveFinished		 = pyqtSignal(str)		# <str> The Filename

	# layer signals
	layerCreated			 = pyqtSignal()
	layerDeleted			 = pyqtSignal()
	layersModified			 = pyqtSignal()
	layerStateChanged		 = pyqtSignal()

	# object signals
	selectionChanged		 = pyqtSignal()
	objectFreeze			 = pyqtSignal(object)
	objectUnfreeze			 = pyqtSignal(object)
	objectHide				 = pyqtSignal(object)
	objectUnHide			 = pyqtSignal(object)
	objectRenamed			 = pyqtSignal(str, str, object)		# oldName, newName, Object
	valueChanged			 = pyqtSignal(object, str, object)
	# object signals that may need disabled during imports, merges, file opening
	newObject				 = pyqtSignal()		# linked signal for object creation
	objectCreated			 = pyqtSignal(object)
	objectCloned			 = pyqtSignal(object)
	objectAdded				 = pyqtSignal(object)
	objectDeleted			 = pyqtSignal(str)		# returns the name of the object that was just deleted
	objectPreDelete			 = pyqtSignal(object)
	objectPostDelete		 = pyqtSignal()
	objectParented			 = pyqtSignal(object)	# the object that had its parenting changed
	# User props changes
	customPropChanged		 = pyqtSignal(object)
	blurTagChanged			 = pyqtSignal(object)

	# render signals
	rednerFrameRequested	 = pyqtSignal(int)
	renderFrameFinished		 = pyqtSignal()
	renderSceneRequested	 = pyqtSignal(list)
	renderSceneFinished		 = pyqtSignal()

	# time signals
	currentFrameChanged		 = pyqtSignal(int)
	frameRangeChanged		 = pyqtSignal()

	# application signals
	startupFinished			 = pyqtSignal()
	shutdownStarted			 = pyqtSignal()

	# viewport signals
	viewportRedrawn			 = pyqtSignal()

	eventCalled = pyqtSignal(list)

	_instance = None

	_isConnected = False
	_connections = {}
	# these signals should never actualy be connected, The supplied function will instead be called directly. This is for when exicution order is critical.
	_functionSignals = (viewportRedrawn,)

	def __init__(self):
		QObject.__init__(self)

	def __del__(self):
		print 'Removing Dispatch with __del__'

	def __new__(cls, *args, **kwargs):
		if not cls._instance:
			cls._instance = super(Dispatch, cls).__new__(cls, *args, **kwargs)
			global cross3d, blurdev
			import blurdev
			cls._instance._linkedSignals = {}
			cls._instance._linkedTriggers = []
			cls._process = None
			import cross3d
		return cls._instance

	def disconnectSignals(self):
		"""
			\remarks	Handle cleanup of cross3d code, in this case disable any callbacks/events etc to cross3d.Dispatch
		"""
		try:
			cross3d.application.disconnect()
		except:
			pass
		import blurdev
		blurdev.core.aboutToClearPaths.disconnect(self.disconnectSignals)
		self._isConnected = False

	def connect(self, signal, function):
		"""
			\remarks	All connections to software callbacks should be handled through this function. It will be responsible for dynamicly creating callbacks
						in the application only if something cares about it.
			\param		signal	<str>	The name of the signal you wish to connect to
			\param		function	<function>	a pointer to the function needed to run
		"""
		# only connect the callbacks if a application actually requests them
		if not self._isConnected:
			self._isConnected = cross3d.application.connect()
			# Listen for changes to the blurdev environment, ie switching between beta, gold, or local
			blurdev.core.aboutToClearPaths.connect(self.disconnectSignals)
		# connect the signal
		if (hasattr(self, signal) and type(getattr(self, signal)).__name__ == 'pyqtBoundSignal'):
			if not signal in self._functionSignals:
				getattr(self, signal).connect(function)
			# keep track of what signals are connected to dispatch
			if signal in self._connections:
				self._connections[signal].append(function)
			else:
				self._connections[signal] = [function]
				if signal in self._linkedTriggers:
					for key in self._linkedSignals:
						if signal in self._linkedSignals[key]:
							# Note: if at some point we need two linked signals to share a signal, this may need to be revised to only connect once.
							cross3d.application.connectCallback(key)
				else:
					# create the application callback. this way callbacks that are not being used do not need to be processed
					cross3d.application.connectCallback(signal)

	def disconnect(self, signal, function):
		"""
			\remarks	All disconnections to software callbacks should be handled through this function. It will be responsible for dynamicly creating callbacks
						in the application only if something cares about it.
			\param		signal	<str>	The name of the signal you wish to connect to
			\param		function	<function>	a pointer to the function needed to run
		"""
		if (hasattr(self, signal) and type(getattr(self, signal)).__name__ == 'pyqtBoundSignal'):
			if not signal in self._functionSignals:
				try:
					getattr(self, signal).disconnect(function)
				except TypeError:
					pass
			# remove the signal from the connections list
			if signal in self._connections:
				if function in self._connections[signal]:
					self._connections[signal].remove(function)
					# if the signal is empty remove it
					if not len(self._connections[signal]):
						self._connections.pop(signal)
						if signal in self._linkedTriggers:
							for key in self._linkedSignals:
								if signal in self._linkedSignals[key]:
									# Note: if at some point we need two linked signals to share a signal, this may need to be revised to only disconnect once the last signal is disconnected.
									cross3d.application.disconnectCallback(key)
						else:
							# remove the application callback. this way callbacks that are not being used do not need to be processed
							cross3d.application.disconnectCallback(signal)
				else:
					cross3d.logger.debug('The function %s for signal %s has been disconnected, but was not recorded as connected' % (str(function), signal))
			else:
				
				cross3d.logger.debug('The signal %s has been disconnected, but was not recorded as connected.' % signal)
		# disconnect signals if nothing is connected
		if self._isConnected and not self._connections:
			# print "Trying to disconnect signals"
			self.disconnectSignals()

	def dispatch(self, signal, *args):
		"""
			\remarks	dispatches a string based signal through the system from an application
			\param		signal	<str>
			\param		*args	<tuple> additional arguments
		"""
		if cross3d.application.shouldBlockSignal(signal, self.signalsBlocked()):
			return

		# emit a defined pyqtSignal
		if (hasattr(self, signal) and type(getattr(self, signal)).__name__ == 'pyqtBoundSignal'):
			getattr(self, signal).emit(*args)

		# otherwise emit a custom signal
		else:
			from PyQt4.QtCore import SIGNAL
			self.emit(SIGNAL(signal), *args)

		# emit linked signals
		if (signal in self._linkedSignals):
			for trigger in self._linkedSignals[signal]:
				self.dispatch(trigger)

	def dispatchFunction(self, signal):
		"""
			\remarks	directly calls the function, this is used when the delay from a callback is not acceptable, for example when a viewport is rendering, it needs to draw in a specific order. The function should not expect any arguments.
			\param		signal	<str>	The name of th signal that is being called
		"""
		if signal in self._connections:
			for fn in self._connections[signal]:
				# call the function
				fn()

	def dispatchObject(self, signal, *args):
		"""
			\remarks	dispatches a string based signal through the system from an application
			\param		signal	<str>
			\param		*args	<tuple> additional arguments
		"""
		if cross3d.application.shouldBlockSignal(signal, self.signalsBlocked()):
			return

		# emit a defined pyqtSignal
		if (hasattr(self, signal) and type(getattr(self, signal)).__name__ == 'pyqtBoundSignal') and args[0]:
			getattr(self, signal).emit(cross3d.SceneObject(cross3d.Scene.instance(), args[0]))

		# otherwise emit a custom signal
		else:
			from PyQt4.QtCore import SIGNAL
			self.emit(SIGNAL(signal), *args)

		# emit linked signals
		if (signal in self._linkedSignals):
			for trigger in self._linkedSignals[signal]:
				self.dispatch(trigger)

	def dispatchRename(self, signal, *args):
		"""
			\remarks	dispatches a string based signal through the system from an application specificly for renaming
			\param		signal	<str>
			\param		*args	<tuple> additional arguments
		"""
		if args:
			if len(args) == 3:
				oldName = args[0]
				newName = args[1]
				node = args[2]
			else:
				oldName = args[0][0]
				newName = args[0][1]
				node = args[0][2]
			if node:
				so = cross3d.SceneObject(cross3d.Scene.instance(), node)
				self.objectRenamed.emit(oldName, newName, so)

	def isConnected(self, signal=''):
		"""
			\remarks	Returns if a specific signal is connected(cross3d.application.connectCallback). If signal is not provided return if the master connection is connected(cross3d.application.connect)
		"""
		if not signal:
			return self._isConnected
		return signal in self._connections

	def linkSignals(self, signal, trigger):
		"""
			\remarks	creates a dependency so that when the inputed signal is dispatched, the dependent trigger signal is also dispatched.  This will only work
						for trigger signals that do not take any arguments for the dispatch.
			\param		signal		<str>
			\param		trigger		<str>
		"""
		if (not signal in self._linkedSignals):
			self._linkedSignals[ signal ] = [trigger]
		elif (not trigger in self._linkedSignals[signal]):
			self._linkedSignals[signal].append(trigger)
		# keep a record of triggers so they can be connected
		if not trigger in self._linkedTriggers:
			self._linkedTriggers.append(trigger)

	def linkedSignals(self):
		return self._linkedSignals

	def linkedTriggers(self):
		return self._linkedTriggers

	def preDelete(self, callback, *args):
		cross3d.application.preDeleteObject(callback, *args)

	def postDelete(self, callback, *args):
		cross3d.application.postDeleteObject(callback, *args)

	def process(self):
		return self._process

	def setProcess(self, process):
		self._process = process
		self._process.start()
