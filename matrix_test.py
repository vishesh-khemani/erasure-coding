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
            self.assertEqual(
                self.mat_.num_rows() - len(excluded_rows), submatrix.num_rows())
            self.assertEqual(self.mat_.num_cols(), submatrix.num_cols())
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
            submatrix_bin = submatrix.binary_rep()
            self.assertEqual(
                submatrix.num_rows() * submatrix.field_.n_,
                submatrix_bin.num_rows())
            self.assertEqual(submatrix.num_cols() * submatrix.field_.n_,
                             submatrix_bin.num_cols())
            inverse_bin = inverse.binary_rep()
            product1_bin = inverse_bin.multiply(submatrix_bin)
            product2_bin = submatrix_bin.multiply(inverse_bin)
            for r in range(product1.num_rows() * product1.field_.n_):
                for c in range(product1.num_cols() * product1.field_.n_):
                    self.assertEqual(
                        product1_bin.get_element(r, c),
                        product2_bin.get_element(r, c))
                    if r == c:
                        self.assertEqual(1, product1_bin.get_element(r, c))
                    else:
                        self.assertEqual(0, product1_bin.get_element(r, c))

    def test_binary_rep(self):
        for a in range(self.mat_.field_.order()):
            mat_a = self.mat_.field_.matrix(a)
            for b in range(self.mat_.field_.order()):
                mat_b = self.mat_.field_.matrix(b)
                sum = self.mat_.field_.add(a, b)
                mat_sum = self.mat_.field_.matrix(sum)
                for r in range(len(mat_a)):
                    for c in range(len(mat_a[0])):
                        self.assertEqual(
                            mat_sum[r][c],
                            self.mat_.field_.add(mat_a[r][c], mat_b[r][c]))


if __name__ == '__main__':
    unittest.main()
