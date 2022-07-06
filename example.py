#'''
# Created on 2022 by Gonzalo Simarro and Daniel Calvete
#'''
#
import os
import sys
#
sys.path.insert(0, 'ubasic') # or './ubasic/'
import ubasic as ubasic
#
pathFolderMain = 'example' # USER DEFINED
assert os.path.exists(pathFolderMain)
#
#''' --------------------------------------------------------------------------
# Calibration of the basis
#''' --------------------------------------------------------------------------
#
pathFolderBasis = os.path.join(pathFolderMain, 'basis') # USER DEFINED
eCritical, calibrationModel = 5., 'parabolic' # USER DEFINED (eCritical is in pixels, calibrationModel = 'parabolic', 'quartic' or 'full')
verbosePlot = True # USER DEFINED
#
print('Calibration of the basis')
ubasic.CalibrationOfBasisImages(pathFolderBasis, eCritical, calibrationModel, verbosePlot)
#
#''' --------------------------------------------------------------------------
# Generation of planviews
#''' --------------------------------------------------------------------------
#
pathFolderBasis = os.path.join(pathFolderMain, 'basis') # USER DEFINED
pathFolderPlanviews = os.path.join(pathFolderMain, 'planviews') # USER DEFINED
z0, ppm = 3.2, 1.0 # USER DEFINED
verbosePlot = True # USER DEFINED
#
print('Generation of planviews')
ubasic.PlanviewsFromImages(pathFolderBasis, pathFolderPlanviews, z0, ppm, verbosePlot)
#
#''' --------------------------------------------------------------------------
# Checking of the basis
#''' --------------------------------------------------------------------------
#
pathFolderBasisCheck = os.path.join(pathFolderMain, 'basis_check') # USER DEFINED
eCritical = 5. # USER DEFINED (eCritical is in pixels)
#
print('Checking of the basis')
ubasic.CheckGCPs(pathFolderBasisCheck, eCritical)
#
