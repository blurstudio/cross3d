/*!
	helpers.ms
	
	this file defines a struct of methods designed to help out the python integration
	for methods that are not easily transferrable to python
*/
global blur3dhelper
(
	struct Blur3dHelperStruct (

		function turntableHelperBuilder cam startFrame endFrame = (
			helper = (dummy name:"TurntableHelper")
			numFrames = (endFrame - startFrame)
			mult = ((360.0 / numFrames) as string)
			fStart = (startFrame as string)
			fEnd = (endFrame as string)
			expr = "degToRad (" + mult + " * (F - " + fStart + "))"
			helper.rotation.z_rotation.controller = Float_Script()
			helper.rotation.z_rotation.controller.script = expr
			helper
		),

		function selectObjectsByNameFilter obj = ( obj.layer == (globalVars.get #FILTERLAYER) ),

		function selectObjectsByNameFromLayer layer = (
			global FILTERLAYER = layer
			local userObjs = selectByName title:"Select Objects" buttonText:"Select" filter:( selectObjectsByNameFilter )
			if ( userObjs != undefined ) then select userObjs
		),

		function appendToMultiMtl mtl = (
			current = mtl.materialList.count
			mtl.materialList.count = (current + 1)
			mtl.mapEnabled[(current + 1)] = on
			mtl.materialIDList[(current + 1)] = (current + 1)
			mtl.names[(current + 1)] = ""
		),

		function removeBitmapSubs bitmap = (
			tvps = getclassinstances bitmaptex asTrackViewPick:true
			for tvp in tvps do (
				if tvp.client[tvp.subNum].value == bitmap do (
					tvp.client[tvp.subNum].value = undefined
				)
			)
		),

		-- Visibility toggle for PC objects.
		function togglePointCaches mods state = (
			_blurLibrary.load "blurPointCache"
			pcMods = #()
			for i = 1 to mods.count do
				if classOf mods[i] == Point_Cache do
					append PCMods mods[i] 	
			for i = 1 to pcMods.count do (
				if state != pcMods[i].enabled do (
					if ( not state and _blurPointCache.canDisablePCObject obj ) then 	
						pcMods[i].enabled = false
					else 																
						pcMods[i].enabled = true
				)
			)
		),

		function hasVisibleDescendent obj = (
			local found = false
			if ( obj != undefined ) do (
				if ( not obj.isHidden ) then (
					found = true
				)
				else (
					for child in obj.children do (
						if ( blur3dhelper.hasVisibleDescendent child ) do (
							found = true
							exit
						)
					)
				)
			)
			found
		),
	
		function hasVisibleReference obj = (
			local found = false
			if ( obj != undefined ) do (
				if ( not obj.isHidden ) then (
					found = true
				)
				else (
					for obj in refs.dependentNodes obj do (
						if ( blur3dhelper.hasVisibleReference obj ) then (
							found = true
							exit
						)
					)
				)
			)
			found
		),
	
		function canDisableTMController ctrl = (
			local objs = refs.dependentNodes ctrl
			local success = true
			for obj in objs do (
				if ( isValidNode obj ) do (
					if ( not obj.isHidden or classOf obj == hairFxView ) do (
						success = false
						exit
					)
					if ( blur3dhelper.hasVisibleDescendent obj ) do (
						success = false
						exit
					)
					if ( blur3dhelper.hasVisibleReference obj ) do (
						success = false
						exit
					)
				)
			)
			success
		),

		function toggleSubDyn subDyn state = (
			subDyn.on = state
		),
	
		function toggleTransformCache obj state = (
			if ( isproperty obj #controller and classof obj.controller == transform_cache ) do (
				if ( obj.controller.enabled != state ) do (
					if ( not state and blur3dhelper.canDisableTMController obj.controller ) then (
						obj.controller.enabled = false
					)
					else (
						obj.controller.enabled = true
					)
				)
			)
		),

		function getTransformController object = (
			return object.transform.controller
		),

		function setTransformController object controller = (
			object.transform.controller = controller
		),

		function replaceTransformController source target frame = (
			at time frame (
				with animate on target.transform = source.transform
			)
		),

		function replaceCameraProperties source target frame = (
			targetClass = classof target
			sourceClass = classof source
			at time frame (
				with animate on (
					if targetClass == freecamera and sourceClass != VRayPhysicalCamera do (
						target.fov = source.fov
						target.nearclip = source.nearclip
						target.farclip = source.farclip
					)
					if sourceClass == VRayPhysicalCamera and targetClass == freecamera do (
						target.mpassEffect.focalDepth = source.focus_distance
						if source.specify_fov == on then (
							target.fov = source.fov
						)
						else (
							-- If the fov is not specified specifically then we have
							-- to compute it from the focal length and film gate width.
							target.fov = ((atan (source.film_width / 2.0 / source.focal_length)) * 2.0)
						)
					)
				)
			)
		),

		function objectIsAnimated object = (
			object.transform.isAnimated
		),

		function getFirstPositionKeyFrameNumber object = (
			if object.position.isAnimated do (
				try (
					return object.position.controller.keys[1].time.frame
				)
				catch()
			)
		),

		function getElementUsingFace obj faceID = (
			try (
				return (meshop.getElementsUsingFace obj #(faceID))
			)
			catch ()
		),
		
		function getVertsUsingFace obj faceList = (
			try (
				return (meshop.getVertsUsingFace obj faceList)
			)
			catch ()
		),
		
		function asArray thing = (
			try (
				return (thing as array)
			)
			catch ()
		),

		function asBitArray thing = (
			try (
				return (thing as bitArray)
			)
			catch ()
		),
		
		function asName thing = (
			try (
				return (thing as name)
			)
			catch()
		),
		
		function setMorpherChannelValue m c v = (
			try (
				WM3_MC_SetValue m c (v as float)
			)
			catch()
		),
		
		function setAnimate v = (
			if v then (
				set animate on
			)
			else (
				set animate off
			)
		),
		
		function layerNodes l = (
			l.nodes &theNodes
			return theNodes
		),
		
		function getLastPositionKeyFrameNumber object = (
			if object.position.isAnimated do (
				try (
					return object.position.controller.keys[object.position.controller.keys.count].time.frame
				)
				catch()
			)
		),

		-- get subdyn sets from a dynamic master tied to a thinking particle object
		function getSubDyns object = (
			local subdyns = #()
			subdyns = for sub = 1 to object.numsubs collect object[sub]
			subdyns
		)
	)

	blur3dhelper = Blur3dHelperStruct()
)
