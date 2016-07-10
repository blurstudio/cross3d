import cross3d
from PyQt4.QtCore import QObject


class AbstractUndoContext(QObject):
	
	def __init__(self, name):
		super(AbstractUndoContext, self).__init__()
		self.name = name
	
	def __enter__(self):
		return None
	
	def __exit__(self, exc_type, exc_value, traceback):
		return False
	
	@classmethod
	def openUndo(cls, name):
		return None
	
	@classmethod
	def closeUndo(cls):
		return False
	
	
# register the symbol
cross3d.registerSymbol('UndoContext', AbstractUndoContext, ifNotFound=True)
	