import os
import sys
root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, os.path.abspath(root))

from pdsimage.Structure import *
from pdsimage.PDS_Extractor import *

import matplotlib.pyplot as plt

if __name__ == '__main__':
    path_pdsfile = os.path.join(root, 'PDS_FILES')
    
    lon0, lon1, lat0, lat1 = 0, 20, -10, 10
    img = BinaryTable('LDEM_16', path_pdsfile=path_pdsfile)    
    X, Y, Z = img.extract_grid(lon0,lon1,lat0,lat1)

    imagep = os.path.join(root, 'docs', 'source', '_static')
    
    Copernicus = Crater('name', 'Copernicus', path_pdsfile=path_pdsfile)
    Copernicus.ppdlola = 64
    Copernicus.ppdwac = 64
    
    Copernicus.overlay(True, name=os.path.join(imagep, 'Copernicus2.png'))

    plt.show()
