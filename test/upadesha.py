# -*- coding: utf-8 -*-
"""
    test.upadesha
    ~~~~~~~~~~~~~



    :license: MIT and BSD
"""

from vyakarana.upadesha import *


def test_upadesha_properties():
    t = Upadesha('gati')
    assert t
    assert t.raw == 'gati'
    assert t.value == 'gati'
    assert t.adi == 'g'
    assert t.upadha == 't'
    assert t.antya == 'i'

    t = Upadesha('anta~')
    assert t
    assert t.raw == 'anta~'
    assert t.value == 'ant'
    assert t.adi == 'a'
    assert t.upadha == 'n'
    assert t.antya == 't'


def test_upadesha():
    # 1.3.2
    for v in Sounds('ac'):
        for c in Sounds('hal'):
            if c + v in ('Yi', 'wu', 'qu'):
                continue
            s = c + v + '~'
            u = Upadesha(s)
            assert u.raw == s
            assert u.value == c
            assert v + 'dit' in u.samjna

    # 1.3.3
    for v in Sounds('ac'):
        for c in Sounds('hal'):
            s = v + c
            u = Upadesha(s)
            assert u.raw == s
            assert u.value == v
            assert c + 'it' in u.samjna

    # 1.3.4
    for v in Sounds('ac'):
        for c in Sounds('tu s m'):
            s = v + c
            u = Upadesha(s, vibhakti=True)
            assert u.raw == s
            assert u.value == s
            assert c + 'it' not in u.samjna

    pairs = [
        ('iya~N', 'iy'),
        ('uva~N', 'uv'),
        ('vu~k', 'v'),
    ]
    for raw, value in pairs:
        u = Upadesha(raw)
        assert u.raw == raw
        assert u.value == value


def test_anga():
    a = Anga('nara')
    assert 'anga' in a.samjna


def test_dhatu():
    pairs = [
        ('BU', 'BU'),
        ('qukf\Y', 'kf'),
        ('sta\mBu~', 'stamB'),
        ('qukrI\Y', 'krI'),
    ]
    for raw, value in pairs:
        d = Dhatu(raw)
        assert 'anga' in d.samjna
        assert 'dhatu' in d.samjna
        assert d.raw == raw
        assert d.value == value


def test_krt():
    pairs = [
        ('san', 'sa', ['nit']),
        ('yaN', 'ya', ['Nit']),
        ('yak', 'ya', ['kit']),
        ('kyac', 'ya', ['kit', 'cit']),

        ('Sap', 'a', ['Sit', 'pit']),
        ('Syan', 'ya', ['Sit', 'nit', 'Nit']),
        ('Sa', 'a', ['Sit', 'Nit']),
        ('Snam', 'na', ['Sit', 'mit', 'Nit']),
        ('Ric', 'i', ['Rit', 'cit']),
        ('kvasu~', 'vas', ['kit', 'udit'])
    ]
    for raw, value, its in pairs:
        p = Krt(raw)
        assert 'pratyaya' in p.samjna
        assert 'krt' in p.samjna
        assert p.raw == raw
        assert p.value == value

        for it in its:
            assert it in p.samjna


def test_vibhakti():
    pairs = [
        ('tip', 'ti', ['pit']),
        ('iw', 'i', ['wit']),
        ('Ral', 'a', ['Rit', 'lit']),
        # ('eS', 'e', ['S']),
        ('irec', 'ire', ['cit']),
        ('wA', 'A', ['wit']),
        ('Nas', 'as', ['Nit']),
        ('Nasi~', 'as', ['Nit', 'idit']),
        ('sup', 'su', ['pit']),
    ]
    for raw, value, its in pairs:
        v = Vibhakti(raw)
        assert 'pratyaya' in v.samjna
        assert 'vibhakti' in v.samjna
        assert v.raw == raw
        assert v.value == value

        for it in its:
            assert it in v.samjna

