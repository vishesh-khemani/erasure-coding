import field
import unittest


class TestBinaryFiniteField(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.field_ = []
        for n in range(1, 8):
            cls.field_.append(field.BinaryFiniteField(n))

    def test_add(self):
        for field in TestBinaryFiniteField.field_:
            negatives = {}
            for a in range(field.order()):
                for b in range(a, field.order()):
                    result = field.add(a, b)
                    self.assertTrue(result in range(0, field.order()))
                    self.assertEqual(result, field.add(b, a))
                    if result == 0:
                        negatives[a] = b
                        negatives[b] = a
            self.assertEqual(field.order(), len(negatives))

    def test_subtract(self):
        for field in self.field_:
            for a in range(field.order()):
                for b in range(field.order()):
                    result = field.subtract(a, b)
                    self.assertTrue(result in range(0, field.order()))
                    if a == b:
                        self.assertEqual(0, result)
                    else:
                        self.assertTrue(result > 0)

    def test_multiply(self):
        for field in self.field_:
            reciprocals = {}
            for a in range(field.order()):
                for b in range(field.order()):
                    result = field.multiply(a, b)
                    self.assertTrue(result in range(0, field.order()))
                    self.assertEqual(result, field.multiply(b, a))
                    if result == 0:
                        self.assertTrue(a == 0 or b == 0)
                    if result == 1:
                        self.assertFalse(a == 0 or b == 0)
                        reciprocals[a] = b
                        reciprocals[b] = a
            self.assertEqual(field.order() - 1, len(reciprocals))

    def test_divide(self):
        for field in self.field_:
            for a in range(field.order()):
                for b in range(field.order()):
                    if b == 0:
                        continue
                    result = field.divide(a, b)
                    self.assertTrue(result in range(0, field.order()))
                    if a == b:
                        self.assertEqual(1, result)
                    else:
                        self.assertNotEqual(1, result)


if __name__ == '__main__':
    unittest.main()
