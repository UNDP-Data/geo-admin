import random
import unittest
from admin_tools.uniqueid import lonlat2id, id2lonlat
import math
class MyTestCase(unittest.TestCase):


    def create_range(self):
        """Create a series of coordinates to check when the id algos stop working"""
        pass
    def setUp(self):
        self.lon = -169.33259181615757
        self.lat = -34.55406470337032
        self.precisions = range(1, 7)

    def test_id_isint(self):
        for precision in self.precisions:
            aid = lonlat2id(lon=self.lon, lat=self.lat, precision=precision)
            self.assertEqual(int, type(aid))  # add assertion here
    def test_return_type(self):
        for p in self.precisions:
            aid = lonlat2id(lon=self.lon, lat=self.lat, precision=p)
            lon, lat = id2lonlat(aid)
            self.assertEqual(float, type(lon))
            self.assertEqual(float, type(lat))

    def test_precision_onepoint(self):
        random.seed(44)
        rnumbers = [random.random() ** 2 * random.random() * random.choice([-1, 1]) for e in range(20)]
        rnumbers = [1*10**-e for e in range(11)]
        print('\n')
        for p in self.precisions:
            for i, r in enumerate(rnumbers, start=1):
                aid = lonlat2id(lon=self.lon, lat=self.lat, precision=p)
                aidr = lonlat2id(lon=self.lon+r, lat=self.lat+r, precision=p)
                if aidr != aid:
                    print(p, i, r, aid,aidr)
            print('-'*30)



    def test_precision_range(self):


        for p in self.precisions:
            aid = lonlat2id(lon=self.lon, lat=self.lat, precision=p)
            lon, lat = id2lonlat(aid)
            lonc = str(lon).find('.')+p
            latc = str(lat).find('.')+p
            flon = str(lon)[:lonc]
            flat = str(lat)[:latc]
            flon_orig = str(self.lon)[:lonc]
            flat_orig = str(self.lat)[:latc]
            self.assertEqual(flon, flon_orig)
            self.assertEqual(flat, flat_orig)



if __name__ == '__main__':
    unittest.main()
