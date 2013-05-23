/*!
	helpers.ms
	
	this file defines a struct of methods designed to help out the python integration
	for methods that are not easily transferrable to python
*/
global blur3dhelper
(
	struct Blur3dHelperStruct (

		-- Visibility toggle for PC objects.
		function toggleCaches obj state = (
			_blurLibrary.load "blurPointCache"
			mods = obj.modifiers
			pcMods = #()
			for i = 1 to mods.count do
				if classOf mods[i] == Point_Cache do
					append PCMods mods[i] 		

			if pcMods.count > 0 do (
				for i = 1 to pcMods.count do (
					if state != pcMods[i].enabled do (
						if ( not state and _blurPointCache.canDisablePCObject obj ) then 	
							pcMods[i].enabled = false
						else 																
							pcMods[i].enabled = true
					)		
				)
			)
		)
	)

	blur3dhelper = Blur3dHelperStruct()
)