/*!
	helpers.ms
	
	this file defines a struct of methods designed to help out the python integration
	for methods that are not easily transferrable to python
*/
global blur3dhelper
(
	struct Blur3dHelperStruct (

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
							fount = true
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
						target.fov = source.fov
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