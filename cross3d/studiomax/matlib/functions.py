##
#	\namespace	blur3d.api.studiomax.matlib
#
#	\remarks	This package contains material editing methods for Studiomax
#	
#	\author		beta@blur.com
#	\author		Blur Studio
#	\date		01/06/11
#

def createOverride( baseMaterial, overrideMaterial, options = None ):
	"""
		\remarks	generate a proper override material based on the inputed base material by preserving aspects of the
					base material based on the supplied options, while joining the main shader aspects of the override material
		\param		baseMaterial		<Py3dsMax.mxs.Material>
		\param		overrideMaterial	<Py3dsMax.mxs.Material>
		\param		options				<blur3d.constants.MaterialOverrideOptions>
	"""
	from blur3d.constants import MaterialOverrideOptions
	
	# use default options when none are supplied
	if ( options == None ):
		options = MaterialOverrideOptions.KeepOpacity | MaterialOverrideOptions.KeepDisplacement
	
	# calculate new options
	if ( not options ):
		return overrideMaterial
	
	print 'create advanced override'
	
	# return the new material
	return overrideMaterial