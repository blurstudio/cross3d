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

def buildMaterialFrom( material, opacityMap = None, displacementMap = None ):
	"""
		\remarks	creates a new material using the properties from the inputed material as its base,
					creating the material with an inputed opacity and displacement map overrides
		\param		material		<Py3dsMax.mxs.Material>
		\param		opacityMap		<Py3dsMax.mxs.Map>
		\param		displacementMap	<Py3dsMax.mxs.Map>
		\return		<Py3dsMax.mxs.Material> builtMaterial
	"""
	# if there is no opacity of displacement map, then there is no need to modify the inputed material
	if ( not (opacityMap or displacementMap) ):	
		return material
	
	# store useful methods
	mcopy 		= mxs.copy
	class_of	= mxs.classof
	is_prop		= mxs.isproperty
	cls 		= class_of( material )
	
	# GK 02/05/10 if texture is nested in a "Displacement 3D" or "Height Map" texture, get the root map
	# and use it in the material's own displacement slot. (trying to maintain some comaptibility between vray and mental ray here.)
	# if not nested, we must convert to mr connection displacement and put it there anyway since max's displacement spinner
	# does not correlate correctly to mental ray displacement amounts.
	displacementTexture = None
	
	# extract from a Displacement_3d texture
	if ( class_of( displacementMap ) == mxs.Displacement_3D__3dsmax ):
		displacementTexture 	= displacementMap
		displacementMap 		= displacementMap.map
	
	# extract from a Height_Map texture
	elif ( class_of( displacementMap ) == mxs.Height_Map_Displacement__3dsmax ):
		displacementTexture = displacementMap
		displacementMap 	= displacementMap.heightMap
	
	# build a matte shadow reflection material
	if ( cls in (mxs.Matte_Shadow_Reflection__mi,mxs.mr_Matte_Shadow_Reflection_Mtl) ):
		matteMtl 					= mcopy( material )
		matteMtl.opacity_shader 	= opacityMap
		output						= mxs.mental_ray()
		output.surface				= mxs.Material_to_Shader()
		output.surface.material		= matteMtl
		
		if ( displacementTexture ):
			dispTexture 		= mxs.Displacement_3D__3dsmax()
			dispTexture.map 	= displacementMap
		
		output.displacement = displacementTexture
		return output
	
	# build a standard material
	elif ( cls == mxs.StandardMaterial ):
		output = mcopy( material )
		
		# use the opacity map
		if ( opacityMap ):
			output.opacityMap = opacityMap
		
		# use the displacement map
		if ( displacementMap ):
			output.displacementMap 			= displacementMap
			output.displacementMapEnable 	= True
			
			if ( is_prop( output, 'mental_ray__material_custom_attribute' ) ):
				if ( not displacementTexture ):
					displacementTexture = mxs.Displacement_3D__3dsmax()
					displacementTexture.map = displacementMap
					
				output.mental_ray__material_custom_attribute.displacement 		= displacementTexture
				output.mental_ray__material_custom_attribute.displacementLocked = False
		
		return output
	
	# build a Vray material
	elif ( cls == mxs.VrayMtl ):
		output = mcopy( material )
		
		# use the opacity map
		if ( opacityMap ):
			output.texmap_opacity 		= opacityMap
			output.texmap_opacity_on 	= True
		
		# use the displacementmap
		if ( displacementMap ):
			output.texmap_displacement 		= displacementMap
			output.texmap_displacement_on 	= True
		
		return output
	
	# build a Vray Light material
	elif ( cls == mxs.VrayLightMtl ):
		# light materials only need opacity maps
		if ( not opacityMap ):
			return material
		
		output = mcopy( material )
		output.opacity_texmap = opacityMap
		output.opacity_texmap_on = True
		return output
	
	# build a Arch_Design material
	elif ( cls == mxs.Arch___Design__mi ):
		output = mcopy( material )
		output.cutout_map = opacityMap
		
		# displace the texture
		if ( not displacementTexture ):
			output.displacementMap = displacementMap
		
		# displace the property
		elif ( is_prop( material, 'mental_ray__material_custom_attribute' ) ):
			output.mental_ray__material_custom_attribute.displacement 		= displacementTexture
			output.mental_ray__material_custom_attribute.displacementLocked	= False
		
		return output
	
	# build a blend material
	elif ( cls == mxs.Blend ):
		if ( displacementMap and is_prop( 'mental_ray__material_custom_attribute' ) ):
			output = mcopy( material )
			
			# create a displacement texture
			if ( not displacementTexture ):
				displacementTexture = mxs.Displacement_3D__3dsmax()
				displacementTexutre.map = displacementMap
			
			output.displace = displacementTexture
			return output
		return material
				
	# build a fast skin shader
	elif ( cls in (mxs.SSS_Fast_Skin_Material_Displace__mi,mxs.SSS_Fast_Skin___w__Disp___mi) ):
		if ( displacementMap ):
			output = mcopy( material )
			if ( not displacementTexture ):
				displacementTexture = mxs.Displacement_3D__3dsmax()
				displacementTexture.map = displacementMap
			output.displace = displacementTexture
			return output
		return material
	
	# build a mental_ray shader
	elif ( cls == mxs.Mental_Ray ):
		output = mcopy( material )
		
		# use displacement
		if ( displacementMap ):
			if ( not displacementTexture ):
				displacementTexture = mxs.Displacement_3D__3dsmax()
				displacementTexture.map = displacementMap
			output.displacement = displacementTexture
		
		# use opacity
		if ( opacityMap ):
			opacityMtl = mxs.Opacity__base()
			opacityMtl.input_shader 	= material.surface
			opacityMtl.opacity_shader	= opacityMap
			output.surface				= opacityMtl
		
		return output
	
	# build a multi/material
	elif ( cls == mxs.MultiMaterial ):
		output 			= mcopy( material )
		count			= material.numsubs
		output.numsubs 	= count
		
		for i in range(count):
			output[i] = buildMaterialFrom( material[i], opacityMap = opacityMap, displacementMap = displacementMap )
		
		return output
	
	# create a default material
	else:
		count = mxs.getNumSubMtls( material )
		if ( count ):
			output = mcopy( material )
			
			get_submtl = mxs.getSubMtl
			set_submtl = mxs.setSubMtl
			
			for i in range( output ):
				set_submtl( output, i + 1, buildMaterialFrom( get_submtl( material, i + 1 ), opacityMap = opacityMap, displacementMap = displacementMap ) )
			
			return output
	
	return material

def createMaterialOverride( baseMaterial, overrideMaterial, options = None ):
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
		options = MaterialOverrideOptions.All
	
	# make sure we have at least some overriding options or a base material to work from
	if ( not options ):
		return overrideMaterial
	
	# make sure we have an overrideMaterial to work from
	if ( not (overrideMaterial and baseMaterial) ):
		return overrideMaterial
	
	# store maxscript values that we use more than once (faster)
	is_kindof 		= mxs.isKindOf
	multi_material	= mxs.MultiMaterial
	class_of		= mxs.classOf
	get_submtl		= mxs.getSubMtl
	set_submtl 		= mxs.setSubMtl
	get_numsubmtls	= mxs.getNumSubMtls
	
	# process XRef materials
	if ( is_kindof( baseMaterial, mxs.XRef_Material ) ):
		return createMaterialOverride( (baseMaterial.getSourceMaterial(True)), overrideMaterial, options )
	
	# process Multi/Sub Materials
	elif ( is_kindof( baseMaterial, multi_material ) ):
		outputMaterial 			= multi_material()
		count					= baseMaterial.numsubs
		outputMaterial.numsubs	= count
		
		for i in range( count ):
			# determine the actual overriding material based on if the override material is a multi/sub or not
			if ( is_kindof( overrideMaterial, multi_material ) ):
				replaceMaterial = multi_material[i]
			else:
				replaceMaterial = overrideMaterial
			subMaterial 	= baseMaterial[i]
			
			# check to see if this is a mental ray holder material
			if ( class_of( subMaterial ) == mxs.Mental_Ray and not subMaterial.surface ):
				outputMaterial[i] = subMaterial
			else:
				outputMaterial[i] = createMaterialOverride( subMaterial, replaceMaterial, options = options )
		
		return outputMaterial
	
	# GK 09/24/10 standard behavior for alt materials is to apply alternates within blend materials (i.e. multimaterials) instead of replacing them entirely.
	# this is so that the user has control over specific parts of the material (like with Multi-Subs).  this works for pretty much every situation,
	# however because we are now using VrayBlendMtls which are unsupported by renderers other than Vray, this method can create a situation where you're trying to render
	# a scanline alt material with scanline, but it is nested within a VrayBlendMtl so it renders incorrectly. also, VrayBlendMtls do not support standard materials anyway
	# so even rendering with Vray will not behave correctly.  below is code to handle this situation:
	elif ( class_of( overrideMaterial ) in (mxs.StandardMaterial,mxs.MatteShadow,mxs.Blur_Matte_mtl) ):
		if ( class_of( baseMaterial ) in (mxs.VrayBlendMtl,mxs.VrayOverrideMtl,mxs.VrayMtlWrapper) ):
			return createMaterialOverride( get_submtl( baseMaterial, 1 ), overrideMaterial, options = options )
	
	# process any non-multi/sub multi-materials
	elif ( get_numsubmtls( baseMaterial ) ):
		outputMaterial = mxs.copy( baseMaterial )
		
		count = get_numsubmtls( baseMaterial )
		for i in range( count ):
			if ( is_kindof( overrideMaterial, multi_material ) ):
				replaceMaterial = multi_material[i]
			else:
				replaceMaterial = overrideMaterial
			subMaterial		= get_submtl( baseMaterial, i + 1 )
			
			if ( subMaterial ):
				if ( class_of( subMaterial ) == mxs.Mental_Ray and not subMaterial.surface ):
					set_submtl( outputMaterial, i+1, subMaterial )
				else:
					set_submtl( outputMaterial, i+1, createMaterialOverride( subMaterial, replaceMaterial, options = options ) )
		
		return outputMaterial
	
	# process all other materials
	if ( options & MaterialOverrideOptions.KeepOpacity ):
		opacityMap 	= findOpacityMap( baseMaterial )
	else:
		opacityMap = None
		
	if ( options & MaterialOverrideOptions.KeepDisplacement ):
		displMap	= findDisplacementMap( baseMaterial )
	else:
		displMap 	= None
			
	# return the new material
	return buildMaterialFrom( overrideMaterial, opacityMap = opacityMap, displacementMap = displMap )

def findDisplacementMap( material ):
	"""
		\remarks	looks for the displacement map for the inputed material based on its type
		\param		material	<Py3dsMax.mxs.Material>
		\return		<Py3dsMax.mxs.Map> opacityMap || None
	"""
	cls = mxs.classof( material )
	
	is_prop = mxs.isproperty
	
	# return a standard material's displacement map
	if ( cls == mxs.StandardMaterial ):
		if ( material.displacementMap and material.displacementMapEnable ):
			return material.displacementMap
		elif ( is_prop( material, 'mental_ray__material_custom_attribute' ) ):
			mrattr = material.mental_ray__material_custom_attribute
			if ( mrattr.displacementOn and not mrattr.displacementLocked ):
				return mrattr.displacement
		return None
	
	# return a vray material's displacement map
	elif ( cls == mxs.VrayMtl ):
		if material.texmap_displacement_on:
			return material.texmap_displacement 
		else:
			return None
	
	# return an arch design's material
	elif ( cls == mxs.Arch___Design__mi ):
		outMap = None
		
		# first check for mental ray properties
		if ( is_prop( material, 'mental_ray__material_custom_attribute' ) ):
			mrattr = material.mental_ray__material_custom_attribute
			if ( mrattr.displacementOn and not mrattr.displacementLocked ):
				outMap = mrattr.displacement
			else:
				outMap = None
		
		# create a custom output material to match the output amount
		if ( not outMap and material.displacementMap and material.displacement_map_on ):
			if ( material.displacement_map_amt ):
				outMap 						= mxs.Output()
				outMap.map1 				= mtl.displacementMap
				outMap.map1Enabled 			= True
				outMap.output.Output_Amount = material.displacement_map_amt
			else:
				outMap = material.displacementMap
		
		return outMap
	
	# return a blend's displacement
	elif ( cls == mxs.Blend ):
		if ( is_prop( material, 'mental_ray__material_custom_attribute' ) ):
			mrattr = material.mental_ray__material_custom_attribute
			if ( mrattr.displacementOn and not mrattr.displacementLocked ):
				return mrattr.displacement
		return None
	
	# return skin shader displacements
	elif ( cls in (mxs.SSS_Fast_Skin_Material_Displace__mi,mxs.SSS_Fast_Skin___w__Disp___mi) ):
		return material.displace
	
	# return a mental ray displacement
	elif ( cls == mxs.mental_ray ):
		if material.displaceOn:
			return material.displacement
	
	return None
	
def findOpacityMap( material ):
	"""
		\remarks	looks for the opacity map for the inputed material based on its type
		\param		material	<Py3dsMax.mxs.Material>
		\return		<Py3dsMax.mxs.Map> opacityMap || None
	"""
	cls = mxs.classof( material )
	
	# return a standard material's opacity map
	if ( cls == mxs.StandardMaterial ):
		if material.opacityMapEnable:
			return material.opacityMap
	
	# return a vray material's opacity map
	elif ( cls == mxs.VrayMtl ):
		if material.texmap_opacity_on:
			return material.texmap_opacity
	
	# return a vray light material's opacity map
	elif ( cls == mxs.VrayLightMtl ):
		if material.opacity_texmap_on:
			return material.opacity_texmap
	
	# return a matte's opactiy map
	elif ( cls in (mxs.Matte_Shadow_Reflection_mi,mxs.mr_Matte_Shadow_Reflection_Mtl) ):
		if material.opacity_connected:
			return material.opacity_shader
	
	# return an arch design's opacity map
	elif ( cls == mxs.Arch___Design__mi ):
		if material.cutoutmap_on:
			return material.cutout_map
	
	return None