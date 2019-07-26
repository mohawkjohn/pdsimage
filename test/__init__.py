import unittest

from test import test_cookbook

def pdsimage_test_suite():
    loader = unittest.TestLoader()
    suite  = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromModule(test_cookbook))
    return suite

if __name__ == '__main__':
    unittest.main()
    
