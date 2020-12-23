import field
import matrix
import unittest


def choose(l, k):
    results = []
    if k > len(l):
        return results
    if k == 0:
        return results
    sub_results = choose(l[1:], k - 1)
    if len(sub_results) == 0:
        results.append([l[0]])
    else:
        for sub_result in sub_results:
            result = [l[0]] + sub_result
            results.append(result)
    for choice in choose(l[1:], k):
        results.append(choice)
    return results


class TestCauchyMatrix(unittest.TestCase):
    def setUp(self):
        self.mat_ = matrix.Matrix(5, 3, field.BinaryFiniteField(3))
        self.mat_.set_cauchy()

    def test_invertible_submatrices(self):
        num_rows_to_exclude = self.mat_.num_rows() - self.mat_.num_cols()
        for excluded_rows in choose(
                range(self.mat_.num_rows()), num_rows_to_exclude):
            print("Testing with excluded rows: {0}".format(excluded_rows))
            submatrix = self.mat_.submatrix(excluded_rows, [])
            inverse = submatrix.invert()
            product1 = inverse.multiply(submatrix)
            product2 = submatrix.multiply(inverse)
            for r in range(product1.num_rows()):
                for c in range(product1.num_cols()):
                    self.assertEqual(
                        product1.get_element(r, c), product2.get_element(r, c))
                    if r == c:
                        self.assertEqual(1, product1.get_element(r, c))
                    else:
                        self.assertEqual(0, product1.get_element(r, c))


if __name__ == '__main__':
    unittest.main()
