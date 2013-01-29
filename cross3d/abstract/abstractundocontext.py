




from PyQt4.QtCore import QObject
from blur3d import api


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
api.registerSymbol('UndoContext', AbstractUndoContext, ifNotFound=True)
	