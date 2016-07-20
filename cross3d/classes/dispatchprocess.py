##
#	\namespace	cross3d.classes.dispatchprocess
#
#	\remarks	Responsible for handling processing of events in a secondary thread
#	
#	\author		Mikeh
#	\author		Blur Studio
#	\date		06/09/11
#

from PyQt4.QtCore import QThread
import time

class DispatchProcess(QThread):
	def __init__(self, parent = None):
		QThread.__init__(self, parent)
		self.exiting = False
		self._eventQueue = []
		
		# create connections to signals
		global Dispatch, Scene, SceneObject
		from cross3d	import dispatch
		from cross3d import Scene, SceneObject
		dispatch.eventCalled.connect(self.processEvent)
	
	def __del__(self):
		self.exiting = True
		self.wait()
	
	def processEvent(self, event, *args):
		"""
			\remarks	processes the signals emited from the application creates any objects neccissary, and emits the proper cross3d.Dispatch signal.
						This is designed to run in a secondary thread and emit signals that are processed on the main thread. It hopefully will create minimum
						slowdown.
			\param		event	<str>	Identifies the event type
			\param		*args, **kwargs any properties that need processed and emited by the signals
		"""
		print 'Processing event', event
		self._eventQueue.append((event, args))
	
	
	def dispatchEvent(self, signal, *args):
		print 'Dispatching event', signal
		if ( self.signalsBlocked() ):
			return
			
		# emit a defined pyqtSignal
		if ( hasattr(Dispatch,signal) and type(getattr(Dispatch,signal)).__name__ == 'pyqtBoundSignal' ):
			# this should identify the object type before emiting it if it needs to emit something
			getattr(Dispatch,signal).emit(SceneObject(Scene.instance(), args[0]))
		
		# elif process application specific signals like xsi's value changed
		
		# otherwise emit a custom signal
		else:
			from PyQt4.QtCore import SIGNAL
			self.emit( SIGNAL( signal ), *args )
		
		# emit linked signals
		if ( signal in self._linkedSignals ):
			for trigger in self._linkedSignals[signal]:
				self.dispatch( trigger )
	
	def run(self):
		#process items in the queue
		while not self.exiting:
			if self._eventQueue:
				item = self._eventQueue.pop(0)
				self.dispatchEvent(item[0], item[1])
			else:
				time.sleep(0.05)