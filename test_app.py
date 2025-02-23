import unittest
from app import calc_bmi, calc_ffmi

class TestBMICalculations(unittest.TestCase):
    def test_bmi_normal_values(self):
        self.assertAlmostEqual(calc_bmi(170, 70), 24.22, places=2)
        self.assertAlmostEqual(calc_bmi(160, 55), 21.48, places=2)
    
    def test_bmi_boundary_values(self):
        self.assertAlmostEqual(calc_bmi(250, 30), 4.8, places=2)
        self.assertAlmostEqual(calc_bmi(100, 200), 200.0, places=2)
    
class TestFFMICalculations(unittest.TestCase):
    def test_ffmi_normal_values(self):
        self.assertAlmostEqual(calc_ffmi(170, 70, 15), 20.59, places=2)
        self.assertAlmostEqual(calc_ffmi(160, 55, 25), 16.11, places=2)
    
    def test_ffmi_boundary_values(self):
        self.assertAlmostEqual(calc_ffmi(250, 30, 100), 0.0, places=2)
        self.assertAlmostEqual(calc_ffmi(100, 200, 0), 200.0, places=2)
    
if __name__ == "__main__":
    unittest.main()
