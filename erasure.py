import argparse
import os
import sys
import field
import matrix


class ErasureCoder:

    def __init__(self, N, K, w):
        self.N_ = N
        self.K_ = K
        assert w in [1, 4, 8]
        self.w_ = w
        field_n = 2
        while (1 << field_n) < (N + K):
            field_n = field_n + 1
        self.field_ = field.BinaryFiniteField(field_n)
        self.encoder_ = matrix.Matrix(N, K, self.field_)
        self.encoder_.set_cauchy()
        print("[{0}, {1}] erasure code with word length {2} bytes and 2^{3} "
              "finite field".format(N, K, w, field_n))
        self.chunk_size_ = self.w_ * field_n
        self.data_block_size_ = self.chunk_size_ * self.K_
        self.code_block_size_ = self.chunk_size_ * self.N_

    def read_data_block(self, in_fifo):
        block_size = 0
        buffer = bytearray(self.w_)
        block_ints = [0] * (self.field_.n_ * self.K_)
        for i in range(len(block_ints)):
            read_size = in_fifo.readinto(buffer)
            block_size = block_size + read_size
            if read_size < len(buffer):
                buffer[-1] = block_size
            block_ints[i] = int.from_bytes(buffer, byteorder='big')
        return block_ints, block_size < self.data_block_size_

    def read_code_block(self, in_fifos):
        buffer = bytearray(self.w_)
        block_ints = [0] * (self.field_.n_ * self.K_)
        for i in range(len(block_ints)):
            read_size = in_fifos[i // self.field_.n_].readinto(buffer)
            assert read_size == len(buffer)
            block_ints[i] = int.from_bytes(buffer, byteorder='big')
        return block_ints, len(in_fifos[i // self.field_.n_].peek(1)) == 0

    def write_code_block(self, encoder, data_block_ints, out_fifos):
        code_block_ints = [0] * (self.field_.n_ * self.N_)
        for i in range(len(code_block_ints)):
            for j in range(encoder.num_cols()):
                if encoder.get_element(i, j) == 1:
                    code_block_ints[i] = code_block_ints[i] ^ data_block_ints[j]
            out_buffer = (code_block_ints[i]).to_bytes(self.w_, byteorder='big')
            out_fifos[i // self.field_.n_].write(out_buffer)

    def write_data_block(self, decoder, code_block_ints, out_fifo, done):
        out_buffer = []
        data_block_ints = [0] * (self.field_.n_ * self.K_)
        for i in range(len(data_block_ints)):
            for j in range(decoder.num_cols()):
                if decoder.get_element(i, j) == 1:
                    data_block_ints[i] = data_block_ints[i] ^ code_block_ints[j]
            out_buffer.append((data_block_ints[i]).to_bytes(
                self.w_, byteorder='big'))
        if done:
            data_block_size = out_buffer[-1][-1]
            assert data_block_size < self.data_block_size_
        else:
            data_block_size = self.data_block_size_
        written_size = 0
        for i in range(len(out_buffer)):
            if (written_size + self.w_) <= data_block_size:
                out_fifo.write(out_buffer[i])
                written_size = written_size + self.w_
            else:
                out_fifo.write(out_buffer[i][:(data_block_size - written_size)])
                written_size = data_block_size
                break
        return data_block_size

    def encode(self, in_fifo, out_fifos):
        assert len(out_fifos) == self.N_
        encoder_bin = self.encoder_.binary_rep()
        size = 0
        done = False
        while not done:
            data_block_ints, done = self.read_data_block(in_fifo)
            self.write_code_block(encoder_bin, data_block_ints, out_fifos)
            if not done:
                size = size + self.data_block_size_
            else:
                size = size + (data_block_ints[-1]).to_bytes(
                    self.w_, byteorder='big')[-1]
        return size

    def decode(self, excluded_shards, in_fifos, out_fifo):
        assert len(excluded_shards) == (self.N_ - self.K_)
        assert len(in_fifos) == self.K_
        decoder_bin = self.encoder_.submatrix(
            excluded_shards, []).invert().binary_rep()
        size = 0
        done = False
        while not done:
            code_block_ints, done = self.read_code_block(in_fifos)
            size = size + self.write_data_block(
                decoder_bin, code_block_ints, out_fifo, done)
        return size


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command')
    parser.add_argument('-N', type=int, help='# code chunks in a block')
    parser.add_argument('-K', type=int, help='# data chunks in a block')
    parser.add_argument('-w', type=int, help='# bytes in a word in a chunk')
    parser.add_argument('--data_fifo',
                        help='name of data fifo stream')
    parser.add_argument('--code_fifo_prefix',
                        help='prefix of code fifo streams')
    args = parser.parse_args()

    try:
        os.mkfifo(args.data_fifo)
    except FileExistsError:
        pass

    ec = ErasureCoder(args.N, args.K, args.w)
    if args.command == 'encode':
        print("Listening for data on fifo stream '{0}'".format(args.data_fifo))
        for i in range(ec.N_):
            name = '{0}_{1}'.format(args.code_fifo_prefix, i)
            print("Writing code shard {0} on fifo stream '{1}'".format(i, name))

        data_fifo = open(args.data_fifo, "rb")
        print("Data fifo stream is open.")
        code_fifos = []
        for i in range(ec.N_):
            name = '{0}_{1}'.format(args.code_fifo_prefix, i)
            try:
                os.mkfifo(name)
            except FileExistsError:
                pass
            code_fifos.append(open(name, "wb"))
            print("Code fifo stream for shard {0} is open".format(i))

        print("Starting encode.")
        size = ec.encode(data_fifo, code_fifos)
        data_fifo.close()
        for i in range(ec.N_):
            code_fifos[i].close()
        print("Finished encoding {0} bytes.".format(size))
    elif args.command.startswith('decode'):
        excluded_shards = [int(index) for index in args.command.split('_')[1:]]
        print("Writing decoded data on fifo stream '{0}'".format(args.data_fifo))
        for i in range(ec.N_):
            if i in excluded_shards:
                continue
            name = '{0}_{1}'.format(args.code_fifo_prefix, i)
            print("Reading code shard {0} on fifo stream '{1}'".format(i, name))
        data_fifo = open(args.data_fifo, "wb")
        print("Data fifo stream is open.")
        code_fifos = []
        for i in range(ec.N_):
            if i in excluded_shards:
                continue
            name = '{0}_{1}'.format(args.code_fifo_prefix, i)
            try:
                os.mkfifo(name)
            except FileExistsError:
                pass
            code_fifos.append(open(name, "rb"))
            print("Code fifo stream for shard {0} is open".format(i))
        print("Starting decode.")
        size = ec.decode(excluded_shards, code_fifos, data_fifo)
        print("Finished decoding {0} bytes.".format(size))
    else:
        print("Invalid command")
