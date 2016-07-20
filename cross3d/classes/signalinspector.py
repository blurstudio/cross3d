##
#	\namespace	cross3d.classes.signalInspector
#
#	\remarks	[desc::commented]
#	
#	\author		Mikeh
#	\author		Blur Studio
#	\date		06/13/11
#

import blur3d
dispatch = cross3d.dispatch
from PyQt4.QtCore import QObject

class SignalInspector(QObject):
	def __init__(self):
		super(SignalInspector, self).__init__()
	
	def connect(self):
		for attr in dir(dispatch):
			if type(getattr(dispatch,attr)).__name__ == 'pyqtBoundSignal':
				self.output(attr)
	
	def disconnect(self):
		pass
	
	def output(self, name):
		def handler(*args, **kwargs):
			print '----Signal: %s ARGS:' % name, args, kwargs
		getattr(dispatch,name).connect(handler)