
from PyQt4.QtCore import QObject
from PySoftimage import xsi

import cross3d
from cross3d.abstract.abstractundocontext import AbstractUndoContext


class SoftimageUndoContext(AbstractUndoContext):
	
	def __enter__(self):
		xsi.OpenUndo(self.name)
		return None
	
	def __exit__(self, exc_type, exc_value, traceback):
		xsi.CloseUndo()
		return False
	
	@classmethod
	def openUndo(cls, name):
		xsi.OpenUndo(name)
	
	@classmethod
	def closeUndo(cls):
		xsi.CloseUndo()
	
# register the symbol
cross3d.registerSymbol('UndoContext', SoftimageUndoContext)
