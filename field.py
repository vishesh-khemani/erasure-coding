class BinaryFiniteField:
    """2^n extension finite field for n in [1, 7]."""

    def __init__(self, n):
        """2^n field. """

        assert n in range(1, 8), "n must be in [1, 7]"
        self.n_ = n
        self.order_ = 1 << n

        # Irreducible polynomial for mod multiplication.
        if n == 1:
            pass
        elif n == 2:
            self.divisor_ = 7  # 1 + x + x^2
        elif n == 3:
            self.divisor_ = 11  # 1 + x + x^3
        elif n == 4:
            self.divisor_ = 19  # 1 + x + x^4
        elif n == 5:
            self.divisor_ = 37  # 1 + x^2 + x^5
        elif n == 6:
            self.divisor_ = 67  # 1 + x + x^6
        elif n == 7:
            self.divisor_ = 131  # 1 + x + x^7
        else:
            raise ValueError("n must be in [2, 7]")

    def order(self):
        return self.order_

    def validated(self, a):
        assert a in range(self.order_)
        return a

    def add(self, a, b):
        return self.validated(self.validated(a) ^ self.validated(b))

    def negate(self, a):
        return self.validated(a)

    def subtract(self, a, b):
        return self.add(a, self.negate(b))

    def multiply(self, a, b):
        if self.n_ == 1:
            return self.validated(self.validated(a) * self.validated(b))

        # n > 1
        self.validated(a)
        result = 0
        bin_b = bin(self.validated(b))[2:]  # remove the '0b' prefix
        shift = len(bin_b) - 1
        for d in bin_b:
            if d == '1':
                result = result ^ (a << shift)
            shift = shift - 1
        while result >= self.order_:
            shift = len(bin(result)) - len(bin(self.divisor_))
            result = result ^ (self.divisor_ << shift)
        return self.validated(result)

    def invert(self, a):
        if self.validated(a) == 0:
            raise Exception("0 has no inverse")
        for b in range(self.order_):
            if self.multiply(a, b) == 1:
                return b
        raise Exception("No inverse found for {0}".format(a))

    def divide(self, a, b):
        return self.multiply(a, self.invert(b))

    def matrix(self, a):
        """Returns the n by n binary matrix representation of 'a'."""

        self.validated(a)
        result = [[0] * self.n_ for i in range(self.n_)]
        basis_vec = 1
        for c in range(self.n_):
            p = self.multiply(a, basis_vec)
            bin_p = bin(p)[2:]
            while len(bin_p) < self.n_:
                bin_p = '0' + bin_p
            basis_vec = basis_vec << 1
            for r in range(self.n_):
                result[r][c] = int(bin_p[-r-1])
        return result
