##
#	\namespace	PySoftimage
#
#	\remarks	Defines the PySoftimage interface for basic Qt interaction with softimage using the blurdev package
#	
#	\author		beta@blur.com
#	\author		Blur Studio
#	\date		12/03/08
#

import os.path
import win32com.client

# Import Application Constants
from win32com.client import constants

# Dispatch the application
xsi 			= win32com.client.Dispatch( 'XSI.Application' ).Application
xsiFactory 		= win32com.client.Dispatch( 'XSI.Factory' )
xsiMath			= win32com.client.Dispatch( 'XSI.Math' )
xsiToolkit		= win32com.client.Dispatch( "XSI.UIToolkit" )
xsiProgressBar 	= xsiToolkit.ProgressBar
xsiPrint		= xsi.LogMessage

#-------------------------------------------------------------------------------------------------------------
# Define some api functionality

_flags = {}		 # Global flags to store & share

def enableCommandLog( state = True ):
	pref = None
	try:
		pref = xsi.Preferences.Categories( "scripting" ).cmdlog
	except:
		xsi.LogMessage( 'Cannot disable command logging.' )
		return False
	
	if ( pref ):
		if ( state ):
			pref.Value = 1
		else:
			pref.Value = 0
	
	return True

def flag( key, fail = None ):
	return _flags.get( str( key ), fail )

def setFlag( key, value ):
	_flags[ str( key ) ] = value

# Calculate the version number from the string
def version():
	from PySoftimage import xsi
	import re
	
	value 	= 7.0
	results = re.match( '[^\d]*\.?(\d+)\.(\d+)', xsi.Version() )
	if ( results ):
		value = float( '.'.join( results.groups() ) )
	else:
		print 'Softmage version is unknown!'
	
	return value
	
