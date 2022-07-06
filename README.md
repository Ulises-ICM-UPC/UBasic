# UBasic

`UBasic` is an open source software written in Python for manual image calibration.

### Description
The program is aimed to obtain the image calibration from a set on control points. The result of the process is the intrinsic camera parameters and the extrinsic parameters for each individual image. In addition, planviews can be generated for each image. A code to verify the quality of the GCPs used in the manual calibration of the images is also provided. The development of this software is suitable for images from any source, in particular from Argus-type video monitoring stations or drones. Details about the algorithm and methodology are described in
> *Simarro, G.; Calvete, D.; Souto, P.; Guillen, J. Camera Calibration for Coastal Monitoring Using
Available Snapshot Images. Remote Sens. 2020, 12, 1840; https://doi.org/doi:10.3390/rs12111840*

`UBasic` provides the following tools:

1. [Image calibration](#image-calibration)
2. [Planview generation](#planviews)
3. [Check GCP for basis calibration](#gcp-check)

### Requirements and project structure
To run the software it is necessary to have Python (3.8) and install the following dependencies:
- cv2 (4.2.0)
- numpy (1.19.5)
- scipy (1.6.0)

In parenthesis we indicate the version with which the software has been tested. It is possible that it works with older versions. 

The structure of the project is the following:
* `example.py`
* `example_notebook.py`
* **`ubasic`**
  * `ubasic.py`
  * `ulises_ubasic.py`
* **`example`**
  * **`basis`**
    * `basisImage01.png`
    * `basisImage01cal.txt`
    * `basisImage01cdg.txt`
    * `basisImage01cdh.txt`
    * `basisImage01par.txt`
    * . . .
  * **`basis_check`**
    * `basisImage01.png`
    * `basisImage01cdg.txt`
    * . . .
  * **`planviews`**
    * `crxyz_planviews.txt`
    * `xy_planview.txt`
    * `basisImage01plw.png`
    * . . .
  * **`TMP`**
    * `basisImage01cal_check.png`
    * `basisImage01_checkplw.png`
    * `basisImage01plw_check.png`
    * . . .

The local modules of `UBasic` are located in the **`ubasic`** folder.

To run the demo in the folder **`example`** with the basis of images in **`basis`** using a Jupyter Notebook we provide the file `example_notebook.ipynb`. For experienced users, the `example.py` file can be run in a terminal. `UCalib` handles `PNG` (recommended) and `JPEG` image formats.

## Image calibration
To manually calibrate the images placed in the folder **`basis`**,  it is necessary that each image `<basisImage>.png` is supplied with a file containing the Ground Control Points (GCP) and, optionally, the Horizon Points (HP). The structure of each of these files is the following:
* `<basisImage>cdg.txt`: For each GCP one line with  (minimum 6)
>`pixel-column`, `pixel-row`, `x-coordinate`, `y-coordinate`, `z-coordinate`
* `<basisImage>cdh.txt`: For each HP one line with (minimum 3)
>`pixel-column`, `pixel-row`

Quantities must be separated by at least one blank space between them and the last record should not be continued with a newline (return).

To generate `<basisImage>cdg.txt` and `<basisImage>cdh.txt` files the [UClick](https://github.com/Ulises-ICM-UPC/UClick) software is available.

### Run basis calibration
Import modules:


```python
import sys
import os
sys.path.insert(0, 'ubasic')
import ubasic as ubasic
```

Set the main path and the path where the basis is located:


```python
pathFolderMain = 'example'
pathFolderBasis = os.path.join(pathFolderMain, 'basis')
```

Set the value of maximum error allowed for the basis calibration:

|  | Parameter | Suggested value | Units |
|:--|:--:|:--:|:--:|
| Critical reprojection pixel error | `eCritical` | _5._ | _pixel_ |



```python
eCritical = 5.
```

Select an intrinsic camera calibration model.

| Camara model | `parabolic` | `quartic`| `full` |
|:--|:--:|:--:|:--:|
| Lens radial distortion | parabolic | parabolic + quartic | parabolic + quartic |
| Lens tangential distortion | no | no | yes |
| Square pixels | yes | yes | no |
| Decentering | no | no | yes |

The `parabolic` model is recommended by default, unless the images are highly distorted.


```python
calibrationModel = 'parabolic'
```

To facilitate the verification that the GCPs have been correctly selected in each image of the basis, images showing the GCPs and HPs (black), the reprojection of GCPs (yellow) and the horizon line (yellow) on the images can be generated. Set parameter `verbosePlot = True`, and to `False` otherwise. Images (`<basisImage>cal_check.png`) will be placed on a **`TMP`** folder.


```python
verbosePlot = True
```

Run the calibration algorithm for each image of the basis:


```python
ubasic.CalibrationOfBasisImages(pathFolderBasis, eCritical, calibrationModel, verbosePlot)
```

In case that the reprojection error of a GCP is higher than the error `eCritical` for a certain image `<basisImage>`, a message will appear suggesting to re-run the calibration of the basis or to modify the values or to delete points in the file `<basisImage>cdg.txt`. If the calibration error of an image exceeds the error `eCritical` the calibration is given as _failed_. Consider re-run the calibration of the basis or verify the GPCs and HPs.

As a result of the calibration, the calibration file `<basisImage>cal.txt` is generated in the **`basis`** directory for each of the images. This file contains the following parameters:

| Magnitudes | Variables | Units |
|:--|:--:|:--:|
| Camera position coordinates | `xc`, `yc`, `zc` | _m_ |
| Camera orientation angles | `ph`, `sg`, `ta` | _rad_ |
| Lens radial distortion (parabolic, quartic) | `k1a`, `k2a` | _-_ |
| Lens tangential distortion (parabolic, quartic) | `p1a`, `p2a` | _-_ |
| Pixel size | `sc`, `sr` | _-_ |
| Decentering | `oc`, `rr` | _pixel_ |
| Image size | `nc`, `nr` | _pixel_ |
| Calibration error | `errorT`| _pixel_ |

In case an image is to be calibrated by setting certain parameters listed above, a `<basisImage>par.txt` in the **`basis`** folder must be provided with the specific parameter values. The structure of this file is the following:
* `<basisImage>par.txt`: For each calibration parameter one line with 
> `value`, _`parameter_name`_

## Planviews

Once the frames have been calibrated, planviews can be generated. The region of the planview is the one delimited by the minimum area rectangle containing the points of the plane specified in the file `xy_planview.txt` in the folder **`planviews`**. The planview image will be oriented so that the nearest corner to the point of the first of the file  `xy_planview.txt` will be placed in the upper left corner of the image. The structure of this file is the following:
* `xy_planview.txt`: For each points one line with 
> `x-coordinate`, `y-coordinate`

A minimum number of three not aligned points is required. These points are to be given in the same coordinate system as the GCPs.

Set the folder path where the file `xy_planview.txt` is located and the value of `z0`.


```python
pathFolderPlanviews = os.path.join(pathFolderMain, 'planviews')
z0 = 3.2
```

The resolution of the planviews is fixed by the pixels-per-meter established in the parameter `ppm`. To help verifying that the points for setting the planview are correctly placed, it is possible to show such points on the frames and on the planviews. Set the parameter `verbosePlot = True`, and to `False` otherwise. The images (`<basisImage>_checkplw.png` and `<basisImage>plw_check.png`) will be placed in a TMP folder.


```python
ppm = 1.0
verbosePlot = True
```

Run the algorithm to generate the planviews:


```python
ubasic.PlanviewsFromImages(pathFolderBasis, pathFolderPlanviews, z0, ppm, verbosePlot)
```

As a result, for each of the calibrated images `<basisImage>.png` in folder **`basis`**, a planview `<basisImage>plw.png` will be placed in the folder **`planviews`**. Note that objects outside the plane at height `z0` will show apparent displacements due to real camera movement. In the same folder, the file `crxyz_planview.txt` will be located, containing the coordinates of the corner of the planviews images:
* `crxyz_planview.txt`: For each corner one line with 
>`pixel-column`, `pixel-row`, `x-coordinate`, `y-coordinate`, `z-coordinate`

## GCP check

To verify the quality of the GCPs used in the manual calibration of the basis images, a RANSAC (RANdom SAmple Consensus) is performed. Points of the files `<basisImage>cdg.txt` located at the **`basis_check`** folder will be tested. The calibration of the points (minimum 6) is done assuming a _parabolic_ camera model and requires the maximum reprojection pixel error `eCritical` for the GCPs. Set the folder and run the RANSAC algorithm:


```python
pathFolderBasisCheck = os.path.join(pathFolderMain, 'basis_check')
ubasic.CheckGCPs(pathFolderBasisCheck, eCritical)
```

For each file `<basisImage>cdg.txt`, the GCPs that should be revised or excluded will be reported.

## Contact us

Are you experiencing problems? Do you want to give us a comment? Do you need to get in touch with us? Please contact us!

To do so, we ask you to use the [Issues section](https://github.com/Ulises-ICM-UPC/UBasic/issues) instead of emailing us.

## Contributions

Contributions to this project are welcome. To do a clean pull request, please follow these [guidelines](https://github.com/MarcDiethelm/contributing/blob/master/README.md).

## License

UCalib is released under a [AGPL-3.0 license](https://github.com/Ulises-ICM-UPC/UBasic/blob/master/LICENSE). If you use UCalib in an academic work, please cite:

    @Article{rs12111840,
      AUTHOR = {Simarro, Gonzalo and Calvete, Daniel and Souto, Paola and Guillén, Jorge},
      TITLE = {Camera Calibration for Coastal Monitoring Using Available Snapshot Images},
      JOURNAL = {Remote Sensing},
      VOLUME = {12},
      YEAR = {2020},
      NUMBER = {11},
      ARTICLE-NUMBER = {1840},
      URL = {https://www.mdpi.com/2072-4292/12/11/1840},
      ISSN = {2072-4292},
      DOI = {10.3390/rs12111840}
      }

    @Online{ulisesbasic, 
      author = {Simarro, Gonzalo and Calvete, Daniel},
      title = {UBasic},
      year = 2022,
      url = {https://github.com/Ulises-ICM-UPC/UBasic}
      }
