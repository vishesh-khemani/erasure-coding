import erasure
import filecmp
import random
import tempfile
import unittest


class TestErasureCoder(unittest.TestCase):
    def setUp(self):
        self.ec_ = erasure.ErasureCoder(5, 3, 8)

    def test_encode_decode(self):
        data_file = tempfile.NamedTemporaryFile()
        data_file.close()
        decoded_data_file = tempfile.NamedTemporaryFile()
        decoded_data_file.close()
        code_file = []
        for i in range(self.ec_.N_):
            code_file.append(tempfile.NamedTemporaryFile())
            code_file[-1].close()

        data_out = open(data_file.name, "wb")
        data_out.write(b'The quick brown fox jumps over the lazy dog.')
        data_out.close()

        # Encode.
        data_in = open(data_file.name, "rb")
        code_out = []
        for i in range(self.ec_.N_):
            code_out.append(open(code_file[i].name, "wb"))
        data_size = self.ec_.encode(data_in, code_out)
        self.assertTrue(data_size > 0)
        data_in.close()
        for i in range(self.ec_.N_):
            code_out[i].close()

        # Decode.
        excluded_shards = random.sample([i for i in range(self.ec_.N_)],
                                        self.ec_.N_ - self.ec_.K_)
        data_out = open(decoded_data_file.name, "wb")
        code_in = []
        for i in range(self.ec_.N_):
            if i not in excluded_shards:
                code_in.append(open(code_file[i].name, "rb"))
        decoded_size = self.ec_.decode(excluded_shards, code_in, data_out)
        self.assertEqual(data_size, decoded_size)
        data_out.close()
        for i in range(self.ec_.K_):
            code_in[i].close()

        # Verify decode.
        self.assertTrue(
            filecmp.cmp(data_file.name, decoded_data_file.name, shallow=False))


if __name__ == '__main__':
    unittest.main()
