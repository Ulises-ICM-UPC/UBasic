#'''
# Created on 2022 by Gonzalo Simarro and Daniel Calvete
#'''
#
import cv2
import numpy as np
import os
#
import ulises_ubasic as ulises
#
def CalibrationOfBasisImages(pathBasis, errorTCritical, model, verbosePlot):
    #
    # manage model
    model2SelectedVariablesKeys = {'parabolic':['xc', 'yc', 'zc', 'ph', 'sg', 'ta', 'k1a', 'sca'], 'quartic':['xc', 'yc', 'zc', 'ph', 'sg', 'ta', 'k1a', 'k2a', 'sca'], 'full':['xc', 'yc', 'zc', 'ph', 'sg', 'ta', 'k1a', 'k2a', 'p1a', 'p2a', 'sca', 'sra', 'oc', 'or']}
    if model not in model2SelectedVariablesKeys.keys():
        print('*** Invalid calibration model {:}'.format(model))
        print('*** Choose one of the following calibration models: {:}'.format(list(model2SelectedVariablesKeys.keys()))); exit()
    selectedVariablesKeys = model2SelectedVariablesKeys[model]
    #
    # obtain calibrations
    fnsImages = sorted([item for item in os.listdir(pathBasis) if os.path.splitext(item)[1] in ['.jpeg', '.JPEG', '.jpg', '.JPG', '.png', '.PNG']])
    for posFnImage, fnImage in enumerate(fnsImages):
        #
        print('... calibration of {:}'.format(fnImage), end='', flush=True)
        pathCalTxt = os.path.join(pathBasis, os.path.splitext(fnImage)[0] + 'cal.txt')
        #
        # load nr, nc and dataBasic
        nr, nc = cv2.imread(os.path.join(pathBasis, fnImage)).shape[0:2]
        dataBasic = ulises.LoadDataBasic0(options={'nc':nc, 'nr':nr, 'selectedVariablesKeys':model2SelectedVariablesKeys[model]})
        #
        # load GCPs
        pathCdgTxt = os.path.join(pathBasis, os.path.splitext(fnImage)[0] + 'cdg.txt')
        cs, rs, xs, ys, zs = ulises.ReadCdgTxt(pathCdgTxt, options={'readCodes':False, 'readOnlyGood':True})[0:5]
        #
        # load horizon points
        pathCdhTxt = os.path.join(pathBasis, os.path.splitext(fnImage)[0] + 'cdh.txt')
        if os.path.exists(pathCdhTxt):
            chs, rhs = ulises.ReadCdhTxt(pathCdhTxt, options={'readOnlyGood':True})
        else:
            chs, rhs = [np.asarray([]) for item in range(2)]
        #
        # load mainSetSeeds
        if os.path.exists(pathCalTxt):
            mainSetSeeds = [ulises.ReadMainSetFromCalTxt(pathCalTxt, options={})]
        else:
            mainSetSeeds = []
        #
        # load dataForCal (aG, aH, mainSetSeeds are in dataForCal)
        dataForCal = {'nc':nc, 'nr':nr, 'cs':cs, 'rs':rs, 'xs':xs, 'ys':ys, 'zs':zs, 'aG':1.}
        if len(chs) == len(rhs) > 0:
            dataForCal['chs'], dataForCal['rhs'], dataForCal['aH'] = chs, rhs, 1.
        if len(mainSetSeeds) > 0:
            dataForCal['mainSetSeeds'] = mainSetSeeds
        #
        # obtain subsetVariablesKeys and subCsetVariablesDictionary (given parameters)
        subCsetVariablesDictionary = {}
        pathParTxt = os.path.join(pathBasis, os.path.splitext(fnImage)[0] + 'par.txt')
        if os.path.exists(pathParTxt):
            openedFile = open(pathParTxt, 'r')
            listOfLines = openedFile.readlines()
            openedFile.close()
            for line in listOfLines:
                if line.split()[1] in selectedVariablesKeys:
                    subCsetVariablesDictionary[line.split()[1]] = float(line.split()[0])
        subsetVariablesKeys = {item for item in selectedVariablesKeys if item not in subCsetVariablesDictionary.keys()}
        #
        # obtain calibration
        mainSet, errorT = ulises.NonlinearManualCalibration(dataBasic, dataForCal, subsetVariablesKeys, subCsetVariablesDictionary, options={})
        #
        # inform and write
        if errorT <= 1. * errorTCritical:
            print(' success')
            # check errorsG
            csR, rsR = ulises.XYZ2CDRD(mainSet, xs, ys, zs, options={})[0:2]
            errorsG = np.sqrt((csR - cs) ** 2 + (rsR - rs) ** 2)
            for pos in range(len(errorsG)):
                if errorsG[pos] > errorTCritical:
                    print('*** the error of GCP at x = {:8.2f}, y = {:8.2f} and z = {:8.2f} is {:5.1f} > critical error = {:5.1f}: consider to check or remove it'.format(xs[pos], ys[pos], zs[pos], errorsG[pos], errorTCritical))
            # write pathCalTxt
            ulises.WriteCalTxt(pathCalTxt, mainSet['allVariables'], mainSet['nc'], mainSet['nr'], errorT)
            # manage verbosePlot
            if verbosePlot:
                pathTMP = os.path.join(pathBasis, '..', 'TMP', fnImage.replace('.', 'cal_check.'))
                ulises.MakeFolder(os.path.split(pathTMP)[0])
                ulises.PlotMainSet(os.path.join(pathBasis, fnImage), mainSet, cs, rs, xs, ys, zs, chs, rhs, pathTMP)
        else:
            print(' failed (error = {:6.1f})'.format(errorT))
            print('*** re-run and, if it keeps failing, check quality of the GCP or try another calibration model ***')
    #
    return None
#
def PlanviewsFromImages(pathBasis, pathPlanviews, z0, ppm, verbosePlot):
    #
    # obtain the planview domain from the cloud of points
    if not os.path.exists(pathPlanviews):
        print('*** folder {:} not found'.format(pathPlanviews)); exit()
    if not os.path.exists(os.path.join(pathPlanviews, 'xy_planview.txt')):
        print('*** file xy_planview.txt not found in {:}'.format(pathPlanviews)); exit()
    rawData = np.asarray(ulises.ReadRectangleFromTxt(os.path.join(pathPlanviews, 'xy_planview.txt'), options={'c1':2, 'valueType':'float'}))
    xsCloud, ysCloud = rawData[:, 0], rawData[:, 1]
    angle, xUL, yUL, H, W = ulises.Cloud2Rectangle(xsCloud, ysCloud)
    dataPdfTxt = ulises.LoadDataPdfTxt(options={'xUpperLeft':xUL, 'yUpperLeft':yUL, 'angle':angle, 'xYLengthInC':W, 'xYLengthInR':H, 'ppm':ppm})
    csCloud, rsCloud = ulises.XY2CR(dataPdfTxt, xsCloud, ysCloud)[0:2] # only useful if verbosePlot
    #
    # write the planview domain
    fileout = open(os.path.join(pathPlanviews, 'crxyz_planview.txt'), 'w')
    for pos in range(4):
        fileout.write('{:6.0f} {:6.0f} {:8.2f} {:8.2f} {:8.2f}\t c, r, x, y and z\n'.format(dataPdfTxt['csC'][pos], dataPdfTxt['rsC'][pos], dataPdfTxt['xsC'][pos], dataPdfTxt['ysC'][pos], z0))
    fileout.close()
    #
    # obtain and write planviews
    fnsImages = sorted([item for item in os.listdir(pathBasis) if os.path.splitext(item)[1] in ['.jpeg', '.JPEG', '.jpg', '.JPG', '.png', '.PNG']])
    for fnImage in fnsImages:
        #
        print('... planview of {:}'.format(fnImage), end='', flush=True)
        #
        # obtain pathPlw and check if already exists
        pathPlw = os.path.join(pathPlanviews, fnImage.replace('.', 'plw.'))
        if os.path.exists(pathPlw):
            print(' already exists'); continue
        #
        # load calibration and obtain and write planview
        pathCalTxt = os.path.join(pathBasis, os.path.splitext(fnImage)[0] + 'cal.txt')
        if os.path.exists(pathCalTxt):
            # load calibration
            mainSet = ulises.ReadMainSetFromCalTxt(pathCalTxt, options={})
            # obtain and write planview
            imgPlanview = ulises.CreatePlanview(ulises.PlanviewPrecomputations({'01':mainSet}, dataPdfTxt, z0), {'01':cv2.imread(os.path.join(pathBasis, fnImage))})
            ulises.MakeFolder(os.path.split(pathPlw)[0])
            cv2.imwrite(pathPlw, imgPlanview)
            print(' success')
            # manage verbosePlot
            if verbosePlot:
                pathTMP = os.path.join(pathPlanviews, '..', 'TMP')
                ulises.MakeFolder(pathTMP)
                imgTMP = ulises.DisplayCRInImage(imgPlanview, csCloud, rsCloud, options={'colors':[[0, 255, 255]], 'size':10})
                cv2.imwrite(os.path.join(pathTMP, fnImage.replace('.', 'plw_check.')), imgTMP)
                #
                cs, rs, possGood = ulises.XYZ2CDRD(mainSet, xsCloud, ysCloud, z0*np.ones(len(xsCloud)), options={'returnGoodPositions':True}) # WATCH OUT DANI
                cs, rs = [item[possGood] for item in [cs, rs]] # WATCH OUT DANI
                img = cv2.imread(os.path.join(pathBasis, fnImage))
                imgTMP = ulises.DisplayCRInImage(img, cs, rs, options={'colors':[[0, 255, 255]], 'size':10})
                cv2.imwrite(os.path.join(pathTMP, fnImage.replace('.', '_checkplw.')), imgTMP)
        else:
            print(' failed')
    #
    return None
#
def CheckGCPs(pathBasisCheck, errorCritical):
    #
    eRANSAC, pRANSAC, ecRANSAC, NForRANSACMax = 0.8, 1-1.e-6, errorCritical, 50000
    #
    # check GCPs
    fnsImages = sorted([item for item in os.listdir(pathBasisCheck) if os.path.splitext(item)[1] in ['.jpeg', '.JPEG', '.jpg', '.JPG', '.png', '.PNG']])
    for posFnImage, fnImage in enumerate(fnsImages):
        #
        print('... checking of {:}'.format(fnImage))
        #
        # load image information and dataBasic
        nr, nc = cv2.imread(os.path.join(pathBasisCheck, fnImage)).shape[0:2]
        oca, ora = [(item - 1) / 2 for item in [nc, nr]]
        #
        # load GCPs
        pathCdgTxt = os.path.join(pathBasisCheck, os.path.splitext(fnImage)[0] + 'cdg.txt')
        cs, rs, xs, ys, zs = ulises.ReadCdgTxt(pathCdgTxt, options={'readCodes':False, 'readOnlyGood':True})[0:5]
        #
        # obtain good GCPs via RANSAC for simplified model (parabolic and squared)
        possGood = ulises.RANSACForGCPs(cs, rs, xs, ys, zs, oca, ora, eRANSAC, pRANSAC, ecRANSAC, NForRANSACMax, options={'nOfK1asa2':1000})[0]
        #
        # inform
        if possGood is None:
            print('... too few GCPs to be checked')
        elif len(possGood) < len(cs):
            print('... re-run or consider to ignore the following GCPs')
            for pos in [item for item in range(len(cs)) if item not in possGood]:
                c, r, x, y, z = [item[pos] for item in [cs, rs, xs, ys, zs]]
                print('... c = {:8.2f}, r = {:8.2f}, x = {:8.2f}, y = {:8.2f}, z = {:8.2f}'.format(c, r, x, y, z))
        else:
            print('... all the GCPs for {:} are OK'.format(fnImage))
    #
    return None
#
