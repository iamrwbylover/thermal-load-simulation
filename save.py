class Save:
	def __init__(self, latitude, longitude, altitude,
				date, swReflCoeff, lwReflCoeff, lwEmiss,
				thickness, spec_heat,thermCon, conv_heat, density,
				swAbs, wlwEmiss, length, width, height,
				direction, initTemp, comfTemp):
		self.lat = latitude
		self.long = longitude
		self.alt = altitude
		self.date = date
		self.swRC = swReflCoeff
		self.lwRC = lwReflCoeff
		self.lwEmiss = lwEmiss
		self.thickness = thickness
		self.spec_heat = spec_heat
		self.thermCon = thermCon
		self.convC = conv_heat
		self.density = density
		self.swAbs = swAbs
		self.wlwEm = wlwEmiss
		self.length = length
		self.width = width
		self.height = height
		self.direction = direction
		self.initTemp = initTemp
		self.comfTemp = comfTemp