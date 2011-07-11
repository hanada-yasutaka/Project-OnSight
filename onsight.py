#!/usr/bin/env python

import os, sys
import getopt

#---------------------------------------------------------------------------
def main(argv):
	#TODO support command line application without GUI 
	try:
		opts, args = getopt.getopt(argv, "h:d", ["help"])
	except getopt.GetoptError:
		pass
	import OnSight.App
	
	app = OnSight.App.MainApp(False)
	app.MainLoop()
#---------------------------------------------------------------------------

#----------------------------------------------------------------------------
if __name__ == '__main__':
	__name__ = 'Main'
	main(sys.argv[:])
#----------------------------------------------------------------------------
