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

def canDisableCaches( object ):
	# make sure this is a valid node
	if ( not mxs.isValidNode( object ) ):
		return True
	
	# make sure this object is not hidden, or a HairFXView object
	if ( not object.ishidden or mxs.classof( object ) == mxs.HairFXView ):
		return False
	
	# make sure all instances of this object are hidden
#	instances = mxs.pyhelper.getInstances( object )
#	for inst in instances:
#		if ( not inst.ishidden ):
#			return False
		
	# make sure all children of this object can be disabled
#	for child in object.children:
#		if ( not canDisableCaches( child ) ):
#			return False
	
	# check all dependent nodes of this object can be disabled
#	for dep in mxs.refs.dependentNodes( object ):
#		if ( not canDisableCaches( object ) ):
#			return False
	
	return True

def enableCaches( object, state ):
	"""
		\remarks	enables/disables the caches on the inputed object based on the given state
		\param		object		<Py3dsMax.mxs.Object>
		\param		state		<bool>
		\return		<bool> success
	"""
	candisable 		= canDisableCaches( object )
	Point_Cache 	= mxs.Point_Cache
	modifiers 		= list(object.modifiers)
	classof			= mxs.classof
				
	# enable/disable point cache modifiers
	for mod in modifiers:
		if ( classof(mod) == Point_Cache ):
			if ( candisable ):
				mod.enabled = state
			else:
				mod.enabled = True
	
	return True

def toggleSceneCaches():
	caches 		= mxs.getClassInstances( mxs.Point_Cache )
	depnodes 	= mxs.refs.dependentNodes
	
	for cache in caches:
		nodes 	= depnodes(cache)
		found	= False
		
		for node in nodes:
			if ( not node.ishidden ):
				cache.enabled = True
				found = True
				break
			
		if ( not found ):
			cache.enabled = False
	
	return True
		