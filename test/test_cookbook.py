import unittest

from .context import *



class Test_Cookbook(unittest.TestCase):

    def setUp(self):
        self.root = os.path.join(os.path.dirname(__file__), '..')
        self.pds_path = os.path.join(self.root, 'PDS_FILES')

    def load_partial_image(self):
        lon0, lon1, lat0, lat1 = 0, 20, -10, 10
        img = BinaryTable('LDEM_16', path_pdsfile=self.pds_path)
        X, Y, Z = img.extract_grid(lon0,lon1,lat0,lat1)
        
    def test_load_partial_image(self):
        self.load_partial_image()

    def test_overlay_impact_crater(self):
        self.load_partial_image()

        imagep = os.path.join(self.root, 'docs', 'source', '_static')
        
        Copernicus = Crater('name', 'Copernicus', path_pdsfile=self.pds_path)
        Copernicus.ppdlola = 64
        Copernicus.ppdwac = 64
        Copernicus.overlay(True, name=os.path.join(imagep, 'Copernicus2.png'))


        

