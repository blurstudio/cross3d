##
#	\namespace	blurapi.libs.XML.xmlelement
#
#	\remarks	defines the XML Element wrapper instance for the blurapi system
#	
#	\author		beta@blur.com
#	\author		Blur Studio
#	\date		04/09/10
#

import xml.dom.minidom
# Load the monkey patched version to fix a known bug http://bugs.python.org/issue5752
import blurdev.XML.minidom
from blurdev.XML.minidom import escape, unescape

from Qt.QtCore	import QRect, QRectF, QPoint, QPointF, QSize, QSizeF, QDate, QDateTime, QString, QByteArray, Qt
from Qt.QtGui	import QColor, QFont

class XMLElement:
	"""Ease of use wrapper class for :class:`xml.dom.minidom.Element` 
	
	The XMLElement class is the root class for all blurdev XML types.  It wraps
	the :class:`xml.dom.minidom.Element` type provided in the standard library.
	The constructor allows it be initialized with a 
	:class:`xml.dom.minidom.Element` instance.
	
	"""
	def __eq__( self, other ):
		""" checks to see if the wrapper <xml.dom.minidom.Element> instance is the same """
		result = False
		if ( isinstance( other, XMLElement ) ):
			result = ( self._object == other._object )
		return result
		
	def __getattr__( self, key ):
		""" pass along all unknown attributes to the <xml.dom.minidom.Element> class instance """
		return getattr( self._object, key )
		
	def __init__( self, object, filename = '' ):
		""" initialize the class with an <xml.dom.minidom.Element> instance """
		if ( object == None ):
			object = xml.dom.minidom.Element(None)
		self._object = object
		self.__file__ = filename
		# Used to allow saving empty attributes.
		self.allowEmptyAttrs = False
	
	def _document( self ):
		""" recursese up the hierarchy to find the parent who is a <xml.dom.minidom.Document> class """
		out = self._object
		while ( out and not isinstance( out, xml.dom.minidom.Document ) ):
			out = out.parentNode
		return out
	
	def _children( self ):
		""" collects the minidom child nodes which are <xml.dom.minidom.Element> types """
		if ( self._object ):
			return [ child for child in self._object.childNodes if isinstance( child, xml.dom.minidom.Element ) ]
		return []
	
	def _findPoint(self, name, cls, method):
		child = self.findChild(name)
		if child:
			x = method(child.attribute('x', 0))
			y = method(child.attribute('y', 0))
			return cls(x, y)
		return cls()
	
	def _findRect( self, name, cls, method ):
		rect 	= cls()
		child 	= self.findChild( name )
		if ( child ):
			x = method( child.attribute( 'x', 0 ) )
			y = method( child.attribute( 'y', 0 ) )
			w = method( child.attribute( 'width', 0 ) )
			h = method( child.attribute( 'height', 0 ) )
		
			rect = cls( x, y, w, h )
			
		return rect
	
	def _findSize(self, name, cls, method):
		child = self.findChild(name)
		if child:
			w = method(child.attribute('width', 0))
			h = method(child.attribute('height', 0))
			return cls(w, h)
		return cls()
	
	def clear( self ):
		children = list( self._object.childNodes )
		for child in children:
			self._object.removeChild( child )
	
	def recordValue( self, value ):
		
		# Convert Qt basics to python basics where possible
		if ( type( value ) == QString ):
			value = unicode( value )
			
		valtype = type( value )
		
		# Record a list of properties
		if ( valtype in (list,tuple) ):
			self.setAttribute( 'type', 'list' )
			
			for val in value:
				entry = self.addNode( 'entry' )
				entry.recordValue( val )
		
		# Record a dictionary of properties
		elif ( valtype == dict ):
			self.setAttribute( 'type', 'dict' )
			
			for key, val in value.items():
				entry = self.addNode( 'entry' )
				entry.setAttribute( 'key', key )
				entry.recordValue( val )
			
		# Record a qdatetime
		elif ( valtype == QDateTime ):
			self.setAttribute( 'type', 'QDateTime' )
			self.setAttribute( 'value', value.toString( 'yyyy-MM-dd hh:mm:ss' ) )	
			
		# Record a qdate
		elif ( valtype == QDate ):
			self.setAttribute( 'type', 'QDate' )
			self.setAttribute( 'value', value.toString( 'yyyy-MM-dd' ) )
		
		# Record a qrect
		elif ( valtype in (QRect,QRectF) ):
			self.setAttribute( 'type', valtype.__name__ )
			self.setRect( 'rect', value )
		
		# Record a point
		elif ( valtype in (QPoint,QPointF) ):
			self.setAttribute( 'type', valtype.__name__ )
			self.setPoint( 'point', value )
		
		# record a QFont
		elif ( valtype == QFont ):
			self.setAttribute( 'type', 'QFont' )
			self.setAttribute( 'value', value.toString() )
		
		# Record a size
		elif valtype in (QSize, QSizeF):
			self.setAttribute( 'type', valtype.__name__ )
			self.setSize( 'size', value )
		
		# Record a qcolor
		elif ( valtype == QColor ):
			self.setAttribute( 'type', 'QColor' )
			self.setColor( 'color', value )
		
		# Record a QByteArray (Experimental)
		elif ( valtype == QByteArray ):
			self.setAttribute( 'type', 'QByteArray' )
			self.setAttribute( 'value', value.toPercentEncoding() )
		
		# Record a basic property
		else:
			self.setAttribute( 'value', value )
			typ = type( value ).__name__
			if ( typ == 'unicode' ):
				typ = 'str'
			self.setAttribute( 'type', typ )
	
	def restoreValue( self, fail = None ):
		
		valtype = self.attribute( 'type' )
		value	= None
			
		# Restore a list item
		if ( valtype == 'list' ):
			value = []
			for child in self.children():
				value.append( child.restoreValue() )
		
		# Restore a dictionary item
		elif ( valtype == 'dict' ):
			value = {}
			for child in self.children():
				value[ child.attribute( 'key' ) ] = child.restoreValue()
		
		# Record a qdatetime
		elif ( valtype == 'QDateTime' ):
			value = QDateTime.fromString( self.attribute( 'value' ), 'yyyy-MM-dd hh:mm:ss' )
			
		# Record a qdate
		elif ( valtype == 'QDate' ):
			value = QDate.fromString( self.attribute( 'value' ), 'yyyy-MM-dd' )
		
		# Restore a QRect
		elif ( valtype == 'QRect' ):
			value = self.findRect( 'rect' )
		
		# Restore a QRectF
		elif ( valtype == 'QRectF' ):
			value = self.findRectF( 'rect' )
		
		# Restore a QSize
		elif ( valtype == 'QSize' ):
			value = self.findSize( 'size' )
		
		# Restore a QSizeF
		elif ( valtype == 'QSizeF' ):
			value = self.findSizeF( 'size' )
		
		# Restore a QPoint
		elif ( valtype == 'QPoint' ):
			value = self.findPoint( 'point' )
		
		# Restore a QPointF
		elif ( valtype == 'QPointF' ):
			value = self.findPointF( 'point' )
		
		# Restore a QColor
		elif ( valtype == 'QColor' ):
			value = self.findColor( 'color' )
		
		# restore a QFont
		elif ( valtype == 'QFont' ):
			value = QFont()
			value.fromString(self.attribute('value'))
		
		# Restore a string
		elif ( valtype in ('str','unicode','QString') ):
			value = unicode(self.attribute( 'value' ))
		
		elif ( valtype == 'ViewMode' ):
			# If treated as a basic value would return fail
			value = int( self.attribute( 'value' ) )
		
		# Restore a QByteArray (Experimental)
		elif ( valtype == 'QByteArray' ):
			value = QByteArray.fromPercentEncoding( self.attribute( 'value', '' ) )
		
		# Restore a Qt.CheckState
		elif valtype == 'CheckState':
			value = Qt.CheckState(self.attribute('value', 0))
		
		# Restore a basic value
		else:
			try:
				value = eval( '%s(%s)' % (valtype,self.attribute('value')) )
			except:
				value = fail
			
		return value
		
	def addComment( self, comment ):
		d = self._document()
		if ( d ):
			out = d.createComment( comment )
			self._object.appendChild( out )
			return True
		return False
	
	def addNode( self, nodeName ):
		"""Adds a new node child to the current element with the given node name.
		
		:param nodeName: name of the child to add
		:type nodeName: str
		:rtype: :class:`XMLElement`

		"""
		d = self._document()
		if ( d ):
			out = d.createElement( nodeName )
			self._object.appendChild( out )
			return XMLElement( out, self.__file__ )
		return None
	
	def addChild( self, child, clone = True, deep = True ):
		if ( isinstance( child, XMLElement ) ):
			child = child._object
		
		if ( clone ):
			self._object.appendChild( child.cloneNode( deep ) )
		else:
			self._object.appendChild( child )
	
	def attribute( self, attr, fail = '' ):
		"""Gets the attribute value of the element by the given attribute id
		:param attr: Name of the atribute you want to recover.
		:param fail: If the atribute does not exist return this.
		"""
		out = unicode( self._object.getAttribute( attr ) )
		out = unescape(out)
		if ( out ):
			return out
		return fail
	
	def attributeDict(self):
		"""
			\Remarks	Returns a dictionary of attributes
			\Return		<dict>
		"""
		out = {}
		for item in self.attributes.values():
			out.update({item.name: item.value})
		return out
	
	def childAt( self, index ):
		"""Finds the child at the given index, provided the index is within the child range
		"""
		childList = self._children()
		if ( 0 <= index and index < len( childList ) ):
			return XMLElement( childList[index], self.__file__ )
		return None
	
	def childNames( self ):
		"""Collects all the names of the children of this element whose 
		child type is an :class:`xml.dom.minidom.Element`
		
		"""
		if ( self._object ):
			return [ child.nodeName for child in self._object.childNodes if isinstance( child, xml.dom.minidom.Element ) ]
		return []
		
	def children( self ):
		"""Collects all the child nodes of this element whose child type is an
		:class:`xml.dom.minidom.Element`, wrapping each child as an 
		:class:`XMLElement`.

		"""
		if ( self._object ):
			return [ XMLElement( child, self.__file__ ) for child in self._object.childNodes if isinstance( child, xml.dom.minidom.Element ) ]
		return []
		
	def index( self, object ):
		"""Finds the index of the inputed child object in this instance's 
		XMLElement children, returning -1 if it cannot be found.

		"""
		if ( self._object ):
			if ( isinstance( object, XMLElement ) ):
				if ( object._object in self._object.childNodes ):
					return self._object.childNodes.index( object._object )
			elif ( isinstance( object, xml.dom.minidom.Element ) ):
				if ( object in self._object.childNodes ):
					return self._object.childNodes.index( object )
		return -1
	
	def findChild( self, childName, recursive = False, autoCreate = False ):
		"""Finds the first instance of the child of this instance whose nodeName is the given child name.
		:param childName: Name to search for.
		:param recursive: Recursively search each child node for more child nodes. Default is False
		:param autoCreate: Create the node if it is not found.
		"""
		if ( self._object ):
			childList = self._object.getElementsByTagName( childName )
			if ( childList ):
				if ( not recursive ):
					for child in childList:
						if child.parentNode == self._object:
						 	return XMLElement( child, self.__file__ )
				else:
					return XMLElement( childList[0], self.__file__ )
		
		if ( autoCreate ):
			return self.addNode( childName )
		
		return None
	
	def findChildById( self, key ):
		import re
		key = '_'.join( re.findall( '[a-zA-Z0-9]*', key ) ).lower()
		for child in self.children():
			if ( key == child.getId() or key == '_'.join( re.findall( '[a-zA-Z0-9]*', child.nodeName ) ).lower() ):
				return child
		return None
	
	def findChildren( self, childName, recursive = False ):
		"""Finds all the children of this instance whose nodeName is the given child name.
		
		:param childName: The name of the child nodes to look for.
		:param recursive: Recursively search each child node for more child nodes. Default is False
		"""
		if ( self._object ):
			if ( recursive ):
				return [ XMLElement( child, self.__file__ ) for child in self._object.getElementsByTagName( childName ) ]
			else:
				return [ XMLElement( child, self.__file__ ) for child in self._object.childNodes if child.nodeName == childName ]
		return []
	
	def findColor( self, name, fail = None ):
		from Qt.QtGui	import QColor
		
		element = self.findChild( name )
		if ( element ):
			return QColor( float( element.attribute( 'red' ) ), float( element.attribute( 'green' ) ), float( element.attribute( 'blue' ) ), float( element.attribute( 'alpha' ) ) )
		elif ( fail ):
			return fail
		else:
			return QColor()
	
	def findFont( self, name, fail = None ):
		element = self.findChild( name )
		if ( element ):
			font = QFont()
			font.fromString( element.attribute( 'value' ) )
			return font
		elif ( fail ):
			return fail
		else:
			return QFont()
	
	def findProperty( self, propName, fail = '' ):
		child = self.findChild( propName )
		if ( child ):
			return child.value()
		return fail
	
	def findPoint(self, name):
		return self._findPoint(name, QPoint, int)
	
	def findPointF(self, name):
		return self._findPoint(name, QPointF, float)
	
	def findRect( self, name ):
		from Qt.QtCore import QRect
		return self._findRect( name, QRect, int )
	
	def findRectF( self, name ):
		from Qt.QtCore import QRectF
		return self._findRect( name, QRectF, float )
	
	def findSize(self, name):
		return self._findSize(name, QSize, int)
	
	def findSizeF(self, name):
		return self._findSize(name, QSizeF, float)
	
	def getId( self ):
		out = self.attribute( 'id' )
		if ( not out ):
			import re
			out = '_'.join( re.findall( '[a-zA-Z0-9]*', self.attribute( 'name' ) ) ).lower()
		return out
	
	def name(self):
		return self.nodeName

	def parent(self):
		if (self.parentNode and isinstance(self.parentNode, xml.dom.minidom.Element)):
			return XMLElement(self.parentNode, self.__file__)
		return None
	
	def recordProperty( self, name, value ):
		element = self.findChild( name )
		if ( element ):
			element.remove()
			
		element = self.addNode( name )
		element.recordValue( value )
	
	def restoreProperty( self, name, fail = None ):
		element = self.findChild( name )
		if ( element ):
			return element.restoreValue( fail )
		return fail
	
	def remove( self ):
		if ( self._object.parentNode ):
			self._object.parentNode.removeChild( self._object )
		return True
			
	def setAttribute( self, attr, val ):
		"""Sets the attribute of this instance to the inputed value, 
		automatically converting the value to a string to avoid errors 
		on the :class:`xml.dom.minidom.Element` object.

		"""
		if (self._object and (val != '' or self.allowEmptyAttrs)):
			val = unicode(val)
			val = escape(val)
			self._object.setAttribute(attr, val)
			return True
		return False
	
	def setColor( self, name, color ):
		element = self.addNode( name )
		if ( element ):
			element.setAttribute( 'red', 	color.red() )
			element.setAttribute( 'green', 	color.green() )
			element.setAttribute( 'blue', 	color.blue() )
			element.setAttribute( 'alpha',	color.alpha() )
	
	def setProperty( self, propName, val ):
		prop = self.findChild( propName )
		if ( not prop ):
			prop = self.addNode( propName )
		prop.setValue( val )
	
	def setFont( self, name, font ):
		element = self.addNode( name )
		element.setAttribute( 'value', font.toString() )
		return element
	
	def setPoint( self, name, point ):
		element = self.addNode( name )
		element.setAttribute( 'x', point.x() )
		element.setAttribute( 'y', point.y() )
		return element
	
	def setRect( self, name, rect ):
		element = self.addNode( name )
		element.setAttribute( 'x', 		rect.x() )
		element.setAttribute( 'y', 		rect.y() )
		element.setAttribute( 'width', 	rect.width() )
		element.setAttribute( 'height',	rect.height() )
		return element
	
	def setSize( self, name, size ):
		element = self.addNode( name )
		element.setAttribute( 'width', 	size.width() )
		element.setAttribute( 'height', size.height() )
		return element
	
	def setValue( self, val ):
		"""Sets the text value for this instance.  If it doesn't already 
		have a child who is of :class:`xml.dom.minidom.Text` type, then 
		it will add one and set the data of it to the inputed value.  The 
		inputed value will automatically be converted to a string value to 
		avoid errors as well.

		"""
		if ( self._object ):
			# find existing text node & update
			for child in self._object.childNodes:
				if ( isinstance( child, xml.dom.minidom.Text ) ):
					child.data = unicode( val )
					return True
			
			# create new text node
			text = self._document().createTextNode( unicode( val ) )
			self._object.appendChild( text )
			return True
		return False
	
	def uri( self ):
		out 	= []
		temp 	= self
		while ( temp ):
			name = temp.getId()
			if ( not name ):
				name = temp.nodeName
			out.insert(0,name)
			temp = temp.parent()
		
		return '::'.join( out )
		
	def value( self ):
		"""Returns the string value of the text node of this instance, 
		provided it has a child node of :class:`xml.dom.minidom.Text` type.  
		If no text node is found, a blank string is returned.

		"""
		if ( self._object ):
			for child in self._object.childNodes:
				if ( isinstance( child, xml.dom.minidom.Text ) ):
					return child.data
		return ''
