##
#	\namespace	blur3d.api.classes.clipboard
#
#	\remarks	This file defines the clipboard class that allows to manipulate the clipboard.
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		09/11/11
#

#------------------------------------------------------------------------------------------------------------------------
		
#------------------------------------------------------------------------------------------------------------------------

class Clipboard( object ):
		
	def clear( self ):
		"""
			\remarks	Deletes the content of the clipboard.
			\return		<bool> success
		"""
		import win32clipboard
		win32clipboard.OpenClipboard()
		win32clipboard.EmptyClipboard()
		win32clipboard.CloseClipboard()
		return True
		
	def text( self ):
		"""
			\remarks	Returns the text hold in the clipboard.
			\return		<string> text
		"""
		import win32clipboard
		win32clipboard.OpenClipboard()
		try:
			value = win32clipboard.GetClipboardData( win32clipboard.CF_TEXT )
		except:
			value = ''
		win32clipboard.CloseClipboard()
		return value
		
	def setText( self, text ):
		"""
			\remarks	Sets the text hold by the clipboarc.
			\param		text <string>
			\return		<bool> success
		"""
		import win32clipboard
		win32clipboard.OpenClipboard()
		win32clipboard.SetClipboardText( text )
		win32clipboard.CloseClipboard()
		return True
		
	def appendText( self, text, separator = '' ):
		"""
			\remarks	Appends text to the clipboard.
			\return		<bool> success
		"""
		initialText = self.text()
		if initialText:
			self.setText( separator.join( [ initialText, text ] ) )
		else:
			self.setText( text )
		return True
		