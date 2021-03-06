from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from pre_commit.languages import pygrep


@pytest.fixture
def some_files(tmpdir):
    tmpdir.join('f1').write_binary(b'foo\nbar\n')
    tmpdir.join('f2').write_binary(b'[INFO] hi\n')
    tmpdir.join('f3').write_binary(b"with'quotes\n")
    with tmpdir.as_cwd():
        yield


@pytest.mark.usefixtures('some_files')
@pytest.mark.parametrize(
    ('pattern', 'expected_retcode', 'expected_out'),
    (
        ('baz', 0, ''),
        ('foo', 1, 'f1:1:foo\n'),
        ('bar', 1, 'f1:2:bar\n'),
        (r'(?i)\[info\]', 1, 'f2:1:[INFO] hi\n'),
        ("h'q", 1, "f3:1:with'quotes\n"),
    ),
)
def test_main(some_files, cap_out, pattern, expected_retcode, expected_out):
    ret = pygrep.main((pattern, 'f1', 'f2', 'f3'))
    out = cap_out.get()
    assert ret == expected_retcode
    assert out == expected_out


def test_ignore_case(some_files, cap_out):
    ret = pygrep.main(('--ignore-case', 'info', 'f1', 'f2', 'f3'))
    out = cap_out.get()
    assert ret == 1
    assert out == 'f2:1:[INFO] hi\n'
