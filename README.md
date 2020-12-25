# erasure-coding

This is a prototype implementation of Erasure Coding, as described here: https://towardsdatascience.com/erasure-coding-for-the-masses-2c23c74bf87e

It is meant for demos only, not for any real encoding. It lacks several features needed for reliabilty, including:

1. Integrity checksums
2. Self-describing data/code formats

## Example Usage

This demo implementation uses linux fifo pipes for the data and code streams. This provides flexibility around the sources and sinks of data/code. The data to encode can be piped through compression etc. before passing to the encoder. The code shards can be directed to destinations chosen by the user (local file, remote storage, etc.). 

### Encode

To encode some data using a [3, 2] code, start the encoder:

```
$python3 erasure.py -N3 -K2 -w8 --data_fifo "data_stream" --code_fifo_prefix "code_stream" encode
[3, 2] erasure code with word length 8 bytes and 2^3 finite field
Listening for data on fifo stream 'data_stream'
Writing code shard 0 on fifo stream 'code_stream_0'
Writing code shard 1 on fifo stream 'code_stream_1'
Writing code shard 2 on fifo stream 'code_stream_2'
```

In a separate process pipe in data to encode into the 'data_stream' fifo:

```
$cat my_photo.png | pv -b > data_stream
```

In separate processes handle the encoded 'code_stream' fifos:

```
$cat code_stream_0 | pv -b > my_photo.png.shard0
```

```
$cat code_stream_1 | pv -b > my_photo.png.shard1
```

```
$cat code_stream_2 | pv -b > my_photo.png.shard2
```

### Decode

To decode the above encoded data using shards 0 and 2, start the decoder:

```
$python3 erasure.py -N3 -K2 -w8 --data_fifo "data_stream" --code_fifo_prefix "code_stream" decode_0
[3, 2] erasure code with word length 8 bytes and 2^3 finite field
Writing decoded data on fifo stream 'data_stream'
Reading code shard 1 on fifo stream 'code_stream_1'
Reading code shard 2 on fifo stream 'code_stream_2'
```

In a separate process pipe out the decoded data:

```
$cat data_stream | pv -b > my_photo_decoded.png
```

In separate processes pipe in the encoded shards:

```
$cat my_photo.png.shard1 | pv -b > code_stream_1
```

```
$cat my_photo.png.shard2 | pv -b > code_stream_2
```
