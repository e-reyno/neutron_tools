import unittest
import mcnp_input_reader

class version_test_case(unittest.TestCase):
    """ test for reading the version of output file"""
    
    def test_is_version(self):
       self.assertTrue(True)
        
if __name__ == '__main__':
    unittest.main()