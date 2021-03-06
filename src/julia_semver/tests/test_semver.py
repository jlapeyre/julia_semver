from julia_semver import semver_spec as spec
from julia_semver import version as ver
import julia_semver
import pytest


def test_caret():
    s = spec('^1.2.3')
    assert s == spec('1.2.3')
    assert s != spec('~1.2.3')
    assert ver('1.2.2') not in s
    assert ver('1.2.3') in s
    assert ver('1.8') in s
    assert ver('2.1') not in s


# And tilde zeros
def test_zeros1():
    s = spec('^0.2.3')
    assert s == spec('0.2.3')
    assert s == spec('~0.2.3')
    assert ver('0.2.3') in s
    assert ver('0.2.10') in s
    assert ver('0.3.0') not in s
    assert ver('1.2.3') not in s


def test_zeros2():
    s = spec('^0.0.3')
    assert s == spec('0.0.3')
    assert s == spec('~0.0.3')
    assert ver('0.0.3') in s
    assert ver('0.0.2') not in s
    assert ver('0.0.4') not in s
    assert ver('0.2.10') not in s
    assert ver('1.0.0') not in s


def test_zeros3():
    s = spec('^0')
    assert s == spec('0')
    assert s == spec('~0')
    assert ver('0.0.0') in s
    assert ver('1.0.0') not in s
    assert ver('0.99.99') in s


def test_zeros4():
    s = spec('^0.0')
    assert s == spec('0.0')
    assert s == spec('~0.0')
    assert ver('0.0.0') in s
    assert ver('0') in s
    assert ver('0.1.0') not in s
    assert ver('0.1') not in s
    assert ver('0.2.3') not in s
    assert ver('0.0.1') in s
    assert ver('0.0.99') in s


def test_tilde():
    s = spec('~1.2.3')
    assert s != spec('1.2.3')
    assert s != spec('^1.2.3')
    assert ver('1.2.2') not in s
    assert ver('1.2.3') in s
    assert ver('1.2.99') in s
    assert ver('1.3.0') not in s
    assert ver('1.8') not in s


def test_dropped():
    assert spec('^1.2') == spec('^1.2.0')
    assert spec('~1.2') == spec('~1.2.0')
    assert spec('1.2') == spec('1.2.0')
    assert spec('^1.2') == spec('^1.2.0')
    assert spec('1') == spec('1.0.0')


def test_equality():
    s = spec('= 1.2.3')
    assert ver('1.2.3') in s
    assert ver('1.2.2') not in s
    assert ver('1.2.4') not in s


def test_greateq():
    s = spec('>= 1.2.3')
    assert ver('1.2.3') in s
    assert ver('1.2.2') not in s
    assert ver('0.0.0') not in s
    assert ver('99.99.99') in s


def test_less():
    s = spec('< 1.2.3')
    assert ver('1.2.3') not in s
    assert ver('1.2.2') in s
    assert ver('0.0.0') in s
    assert ver('99.99.99') not in s


def test_bad_ineq():
    with pytest.raises(ValueError):
        spec('> 1.2.3')
    with pytest.raises(ValueError):
        spec('<= 1.2.3')
    with pytest.raises(ValueError):
        spec('== 1.2.3')


def test_hyphen1():
    assert spec('1.2 - 4.5.6') ==  spec('1.2.0 - 4.5.6')
    s = spec('1.2.3 - 4.5.6')
    assert ver('1.2.3') in s
    assert ver('4.5.6') in s
    assert ver('3.0.0') in s
    assert ver('3') in s
    assert ver('3.0') in s
    assert ver('1.2.2') not in s
    assert ver('4.5.7') not in s


def test_bad_hyphen():
    with pytest.raises(ValueError):
        spec('1.2.3-4.5.6')


def test_comma1():
    s = spec('1.2.3, ~9.1, 11')
    assert ver('1.2.3') in s
    assert ver('1.9.9') in s
    assert ver('2.0.0') not in s
    assert ver('9.1.5') in s
    assert ver('9.2.0') not in s
    assert ver('10') not in s
    assert ver('11.1.2') in s


def test_prerl_match():
    s = spec("^1.2.3")
    assert not s.match(ver("1.2.3-DEV"))
    assert julia_semver.match("^1.2.3", "1.2.3-DEV")
    assert not julia_semver.match("^1.2.3", "1.2.3-DEV", strict=True)


# From Pkg/test/pkg.jl
def test_julia_pkg():
    assert spec("^1.2.3") == spec("1.2.3 - 1")
    assert spec("^1.2") == spec("1.2.0 - 1")
    assert spec("^1") == spec("1.0.0 - 1")
    assert spec("^0.2.3") == spec("0.2.3 - 0.2")
    assert spec("~1.2.3") == spec("1.2.3 - 1.2")
    assert spec("0.0.3, 1.2") == spec("0.0.3, 1.2.0 - 1")
    assert spec("~1") == spec("1.0.0 - 1")
    assert spec("~1.2.3, ~v1") == spec("1.2.3 - 1.2 , 1.0.0 - 1")

    assert   ver("1.5.2")  in spec("1.2.3")
    assert   ver("1.2.3")  in spec("1.2.3")
    assert not (ver("2.0.0")  in spec("1.2.3"))
    assert not (ver("1.2.2")  in spec("1.2.3"))
    assert   ver("1.2.99") in spec("~1.2.3")
    assert   ver("1.2.3")  in spec("~1.2.3")
    assert not (ver("1.3")    in spec("~1.2.3"))
    assert  ver("1.2.0")   in spec("1.2")
    assert  ver("1.9.9")  in spec("1.2")
    assert not (ver("2.0.0")  in spec("1.2"))
    assert not (ver("1.1.9")  in spec("1.2"))
    assert   ver("0.2.3")  in spec("0.2.3")
    assert not (ver("0.3.0")  in spec("0.2.3"))
    assert not (ver("0.2.2")  in spec("0.2.3"))
    assert   ver("0.0.0")  in spec("0")
    assert  ver("0.99.0")  in spec("0")
    assert not (ver("1.0.0")  in spec("0"))
    assert  ver("0.0.0")   in spec("0.0")
    assert  ver("0.0.99")  in spec("0.0")
    assert not (ver("0.1.0")  in spec("0.0"))

    assert   ver("0.2.3") in spec("<0.2.4")
    assert not (ver("0.2.4") in spec("<0.2.4"))
    assert   ver("1.2.3") in spec("=1.2.3")
    assert not (ver("1.2.4") in spec("=1.2.3"))
    assert not (ver("1.2.2") in spec("=1.2.3"))
    assert not (ver("0.3") in spec("0.1 - 0.2"))
    assert ver("0.2.99") in spec("0.1 - 0.2")
    assert ver("0.3") in spec("0.1 - 0")

    with pytest.raises(ValueError):
        spec("0.0.0")
    with pytest.raises(ValueError):
        spec("^^0.2.3")
    with pytest.raises(ValueError):
        spec("0.7 1.0")
