##
#	\namespace	blur3d.api.studiomax.matlib
#
#	\remarks	This package contains material editing methods for Studiomax
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		01/06/11
#

from Py3dsMax import mxs

def canDisableCaches( control ):
	"""
		\remarks	checks to see if the inputed object can disable the transform cache on it
		\param		object		<Py3dsMax.mxs.Controller>
		\return		<bool> disableable
	"""
	objs 		= mxs.refs.dependentNodes( control )
	is_valid 	= mxs.isValidNode
	classof		= mxs.classof
	HairFXView	= mxs.HairFXView
	
	# check for visible descendnets
	def hasVisibleDescendent( object ):
		if ( not object ):
			return False
		
		if ( not object.ishidden ):
			return True
		
		for child in object.children:
			if ( hasVisibleDescendent( child ) ):
				return True
		
		return False
	
	#---------------------
	
	def hasVisibleRef( object ):
		if ( not object ):
			return False
		
		if ( not object.ishidden ):
			return True
		
		for obj in refs.dependentNodes( object ):
			if ( hasVisibleReference( obj ) ):
				return True
			
		return False
	
	#---------------------
	
	for obj in objs:
		if ( not is_valid(obj) ):
			continue
		
		if ( not obj.ishidden or classof(obj) == HairFXView ):
			return False
		
		if ( hasVisibleDescendent( obj ) ):
			return False
		
		if ( hasVisibleReference( obj ) ):
			return False
	
	return True
		
def toggleCaches( object, state ):
	"""
		\remarks	enables/disables the caches on the inputed object based on the given state
		\param		object		<Py3dsMax.mxs.Object>
		\param		state		<bool>
		\return		<bool> success
	"""
	is_prop = mxs.isproperty
	classof	= mxs.classof
	
	if ( is_prop( object, 'controller' ) and classof( object.controller ) == mxs.Transform_Cache ):
		control = object.controller
		if ( control.enabled != state ):
			control.enabled = not canDisableCaches( object ) and state
	
	return False