##
#	\namespace	cross3d.softimage.motionbuilderscene
#
#	\remarks	The MotionBuilderScene class will define all the operations for Motion Builder scene interaction.  
#	
#	\author		douglas
#	\author		Blur Studio
#	\date		06/21/12
#

import pyfbsdk as mob
from cross3d.abstract.abstractscene import AbstractScene

#------------------------------------------------------------------------------------------------------------------------

class MotionBuilderScene( AbstractScene ):
	def __init__( self ):
		self._fbapp = mob.FBApplication()
		AbstractScene.__init__( self )

	def saveFileAs(self, filename=''):
		"""
		Implements AbstractScene.saveFileAs to save the current scene to the inputed name specified.  If no name is supplied, 
		then the user should be prompted to pick a filename
		:param filename: Name of the file to save
		:return	: Success, Bool
		"""		
		if not filename:
			# NOTE: This requires Qt.py 1.1.0.b3 or newer. PyQt4 is the only binding of QFileDialog
			# that does not include the selectedFilter in its return. The QtCompat fixes this.
			from Qt.QtCompat import QFileDialog
			filename, selectedFilter = QFileDialog.getSaveFileName(None, 'Save Motion Builder File', '', 'FBX (*.fbx);;All files (*.*)')
		print 'filename', filename, self._fbapp
		if filename:
			return self._fbapp.FileSave(unicode(filename).encode('utf8'))
		return False

	def retarget(self, inputRigPath, inputAnimationPath, outputRigPath, outputAnimationPath):
		return False

# register the symbol
import cross3d
cross3d.registerSymbol('Scene', MotionBuilderScene)
