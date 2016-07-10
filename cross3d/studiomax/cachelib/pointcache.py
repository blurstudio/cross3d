##
#	\namespace	cross3d.studiomax.matlib
#
#	\remarks	This package contains material editing methods for Studiomax
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		01/06/11
#

from Py3dsMax import mxs

def canDisableCaches( object ):
	# make sure this is a valid node
	if ( not mxs.isValidNode( object ) ):
		return True
	
	# make sure this object is not hidden, or a HairFXView object
	if ( not object.ishidden or mxs.classof( object ) == mxs.HairFXView ):
		return False
	
	# make sure all instances of this object are hidden
	instances = mxs.pyhelper.getInstances( object )
	for inst in instances:
		if ( not inst.ishidden ):
			return False
		
	# make sure all children of this object can be disabled
	for child in object.children:
		if ( not canDisableCaches( child ) ):
			return False
	
	# check all dependent nodes of this object can be disabled
	for dep in mxs.refs.dependentNodes( object ):
		if ( not canDisableCaches( object ) ):
			return False
	
	return True

def toggleCaches( object, state ):
	"""
		\remarks	enables/disables the caches on the inputed object based on the given state
		\param		object		<Py3dsMax.mxs.Object>
		\param		state		<bool>
		\return		<bool> success
	"""
	Point_Cache 	= mxs.Point_Cache
	modifiers 		= list(object.modifiers)
	classof			= mxs.classof
	mods 			= [ mod for mod in modifiers if classof(mod) == Point_Cache ]
	
	# if there are no PC modifiers, then don't worry about this object
	if ( not mods ):
		return True
	
	# determine if this can be disabled
	candisable 		= canDisableCaches( object )
				
	# enable/disable point cache modifiers
	for mod in mods:
		mod.enabled = not candisable or state
	
	return True
