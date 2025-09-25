from acme_cli.ndjson import dump_line

def test_dump_line_is_json():
    s = dump_line({"a": 1, "b": 2})
    assert s == '{"a":1,"b":2}'
