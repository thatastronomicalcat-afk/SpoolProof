import unittest, tempfile, struct
from pathlib import Path
from spoolproof import quote, stl_bounds
class Checks(unittest.TestCase):
    def job(self, **kw):
        return dict(grams=100, hours=1, filament_per_kg=20, **kw)
    def test_known_cost(self):
        r=quote(self.job(quantity=2, margin=.5, setup_cost=1))
        self.assertEqual(r['expected_job_cost'],5)
        self.assertEqual(r['suggested_price'],10)
    def test_retries_and_spool(self):
        r=quote(self.job(failure_probability=.5,spool_remaining_g=199))
        self.assertEqual(r['expected_filament_g'],200)
        self.assertFalse(r['spool_expected_sufficient'])
    def test_orientation(self):
        self.assertTrue(quote(self.job(dimensions_mm=[100,200,50],build_mm=[200,50,100]))['fits_axis_aligned'])
        self.assertFalse(quote(self.job(dimensions_mm=[246,20,20]))['fits_axis_aligned'])
    def test_invalid(self):
        for field,v in [('grams',-1),('hours',float('nan')),('margin',1),('failure_probability',1),('quantity',1.5),('grams',True)]:
            j=self.job();j[field]=v
            with self.assertRaises(ValueError):quote(j)
    def test_labor_not_retried(self):
        r=quote(self.job(failure_probability=.5,labor_minutes=60,labor_per_hour=10))
        self.assertEqual(r['expected_job_cost'],14)
    def test_ascii_and_binary(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.stl'
            p.write_text('solid t\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\nvertex 5 0 0\nvertex 0 4 3\nendloop\nendfacet\nendsolid t')
            self.assertEqual(stl_bounds(p),[5,4,3])
            p.write_bytes(b'solid'+b' ' *75+struct.pack('<I',1)+struct.pack('<12fH',0,0,1,0,0,0,5,0,0,0,4,3,0))
            self.assertEqual(stl_bounds(p),[5,4,3])
    def test_unknown_units(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.stl';p.write_text('vertex 0 0 0\nvertex 1 0 0\nvertex 0 1 1')
            with self.assertRaisesRegex(ValueError,'no units'):quote(self.job(stl='a.stl'),Path(d))
    def test_malformed_mesh(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.stl';p.write_text('vertex nan 0 0\nvertex 1 0 0\nvertex 0 1 1')
            with self.assertRaises(ValueError):stl_bounds(p)
if __name__=='__main__':unittest.main(verbosity=2)
