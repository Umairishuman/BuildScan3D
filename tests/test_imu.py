"""imu.py reads gyro/accelerometer samples out of the ARCore recording (protobuf). Tests of its small parsers."""
import struct

import imu


def varint(n):
    """Encode an integer the way protobuf does (7 bits per byte, high bit = more bytes follow)."""
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def sample(kind, x, y, z, ts):
    """One IMU sample message: field 2 = type, 3/4/5 = x/y/z floats, 6 = timestamp."""
    return (b"\x10" + varint(kind)
            + b"\x1d" + struct.pack("<f", x)
            + b"\x25" + struct.pack("<f", y)
            + b"\x2d" + struct.pack("<f", z)
            + b"\x30" + varint(ts))


def test_varint_single_byte():
    assert imu._varint(b"\x05", 0) == (5, 1)


def test_varint_multi_byte_and_offset():
    # 300 = 0b1_0010_1100 -> 0xAC 0x02; start reading after one filler byte
    assert imu._varint(b"\xff\xac\x02", 1) == (300, 3)


def test_varint_roundtrip():
    for n in (0, 1, 127, 128, 300, 16384, 2 ** 40 + 5):
        value, end = imu._varint(varint(n), 0)
        assert value == n and end == len(varint(n))


def test_walk_finds_a_sample():
    out = []
    assert imu._walk(sample(1, 0.5, -1.25, 9.81, 123456789), out) is True
    assert len(out) == 1
    kind, ts, x, y, z = out[0]
    assert kind == 1 and ts == 123456789
    assert (x, y, z) == (0.5, -1.25, struct.unpack("<f", struct.pack("<f", 9.81))[0])


def test_walk_finds_samples_nested_in_other_messages():
    inner = sample(4, 1.0, 2.0, 3.0, 99)
    wrapped = b"\x0a" + varint(len(inner)) + inner            # field 1, length-delimited
    twice = wrapped + b"\x0a" + varint(len(inner)) + inner
    out = []
    assert imu._walk(twice, out) is True
    assert len(out) == 2 and all(o[0] == 4 for o in out)


def test_walk_ignores_messages_without_all_fields():
    out = []
    imu._walk(b"\x10\x01", out)                                # only a type field
    assert out == []


def test_walk_survives_truncated_or_garbage_input():
    out = []
    assert imu._walk(b"\x1d\x00", out) is False                # float cut short
    imu._walk(b"\x0a\x7f\x01", out)                            # length points past the end: must not raise
    assert imu._walk(b"", out) is True                         # empty input is not an error
    assert out == []                                           # and none of these produced a sample
