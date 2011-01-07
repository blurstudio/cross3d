##
#	\namespace	blur3d.classes.softimage.softimagenode
#
#	\remarks	Describes the base object class to use for a scene
#	
#	\author		beta@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from PySoftimage							import xsi
from blur3d.classes.abstract.abstractnode 	import AbstractNode

class SoftimageNode( AbstractNode ):
	def nativeParent( self ):
		return self._nativeObject.parent
		
	def isSelected( self ):
		return self.nativeObject().selected
		
	def isVisible( self ):
		return self._nativeObject.property( 'Visibility' ).viewvis.value
	
	def setObjectName( self, name ):
		AbstractNode.setObjectName( self, name )
		if ( not self.isNull() ):
			self._nativeObject.name = str( name )
			return True
		return False
	
	def setNativeObject( self, object ):
		AbstractNode.setNativeObject( self, object )
		if ( not self.isNull() ):
			AbstractNode.setObjectName( self, object.name )
			return True
		return False
	
	def setSelected( self, state = True ):
		self._nativeObject.selected = state
		
	def setVisible( self, state = True ):
		if ( not self.isNull() ):
			self._nativeObject.Properties( 'Visibility' ).viewvis.value = state
			return True
		return False
	
	def setWireColor( self, color ):
		if ( not self.isNull() ):
			display = self._nativeObject.Properties( 'Display' )
			if ( display ):
				from PySoftimage import constants
				xsi.MakeLocal( display, constants.siNodePropagation )
				
				display = self._nativeObject.Properties( 'Display' )
				display.wirecolorr.value = color.red() / 255.0
				display.wirecolorg.value = color.green() / 255.0
				display.wirecolorb.value = color.blue() / 255.0
				
				return True
		return False
	
	def wireColor( self ):
		from PyQt4.QtGui import QColor
		if ( not self.isNull() ):
			display = self._nativeObject.Properties( 'Display' )
			if ( display ):
				xsi.MakeLocal( display, constants.siNodePropagation )
				
				display = self._nativeObject.Properties( 'Display' )
				return QColor( display.wirecolorr.value * 255, display.wirecolorg.value * 255, display.wirecolorb.value * 255 )
		return QColor()
	
	@staticmethod
	def nativeChildren( node ):
		return node.children