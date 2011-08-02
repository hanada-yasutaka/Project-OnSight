#!/usr/bin/env python

import os, sys
import getopt

#---------------------------------------------------------------------------
def main(argv):
	basepath=os.path.dirname(os.path.abspath(__file__))
	sys.path.append(os.path.join(basepath,'OnSight'))
	os.chdir(basepath)
	
	#TODO support command line application without GUI 
	try:
		opts, args = getopt.getopt(argv, "h:d", ["help"])
	except getopt.GetoptError:
		pass
	import OnSight.App
	
	app = OnSight.App.MainApp(False)
	app.SetDEBUG(False)
	app.MainLoop()
#---------------------------------------------------------------------------

#----------------------------------------------------------------------------
if __name__ == '__main__':
	__name__ = 'Main'
	main(sys.argv[:])
#----------------------------------------------------------------------------
