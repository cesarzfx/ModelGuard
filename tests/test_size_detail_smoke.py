
def test_size_detail_bert():
    d = _size_detail("https://huggingface.co/bert-base-uncased")
    # all devices present and in [0,1]
    assert set(d) == {
        "raspberry_pi", "jetson_nano", "desktop_pc", "aws_server"
    }
    assert all(0.0 <= float(v) <= 1.0 for v in d.values())
