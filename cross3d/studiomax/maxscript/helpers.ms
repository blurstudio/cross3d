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
		)
	)

	blur3dhelper = Blur3dHelperStruct()
)