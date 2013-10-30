# -*- coding: utf-8 -*-
"""
    vyakarana.operators
    ~~~~~~~~~~~~~~~~~~~

    Excluding paribhāṣā, all rules in the Ashtadhyayi describe a context
    then specify an operation to apply based on that context. Within
    this simulator, operations are defined using *operators*, which
    take some :class:`Upadesha` and return a new :class:`Upadesha`.

    This module defines a variety of parameterized and unparameterized
    operators. All operators accept an optional right context `right`.

    :license: MIT and BSD
"""

from sounds import Sound, Sounds


# TODO: rewrite operators to more closely model the Ashtadhyayi.


def parameterized(fn):
    def wrapped(*args):
        result = fn(*args)
        result.__name__ = '%s(%s)' % (fn.__name__, repr(args))
        return result
    return wrapped


def dirgha(cur, right=None):
    converter = dict(zip('aiufx', 'AIUFX'))
    letters = list(cur.value)
    for i, L in enumerate(letters):
        if L in converter:
            letters[i] = converter[L]
            break

    return cur.set_value(''.join(letters))


def guna(cur, right=None):
    # 1.1.5 kGiti ca (na)
    if right is not None and right.any_samjna('kit', 'Nit'):
        return cur

    # 1.1.2 adeG guNaH
    # 1.1.3 iko guNavRddhI
    converter = dict(zip('iIuUfFxX', 'eeooaaaa'))
    letters = list(cur.value)
    for i, L in enumerate(letters):
        if L in converter:
            letters[i] = converter[L]
            if L in 'fF':
                letters[i] += 'r'
            break

    return cur.set_value(''.join(letters)).add_samjna('guna')


def hrasva(cur, right=None):
    converter = dict(zip('AIUFXeEoO', 'aiufxiiuu'))
    letters = list(cur.value)
    for i, L in enumerate(letters):
        if L in converter:
            letters[i] = converter[L]
            break

    return cur.set_value(''.join(letters))


def samprasarana(cur, right=None):
    rev_letters = list(reversed(cur.value))
    for i, L in enumerate(rev_letters):
        # 1.1.45 ig yaNaH saMprasAraNAm
        # TODO: enforce short vowels automatically
        if L in Sounds('yaR'):
            rev_letters[i] = Sound(L).closest('ifxu')
            break

    # 6.4.108 saMprasAraNAc ca
    try:
        L = rev_letters[i - 1]
        if L in Sounds('ac'):
            rev_letters[i - 1] = ''
    except IndexError:
        pass

    return cur.set_value(''.join(reversed(rev_letters)))


@parameterized
def replace(target, result):
    def func(cur, right=None):
        return cur.set_value(cur.value.replace(target, result))
    return func


@parameterized
def ti(result):
    ac = Sounds('ac')
    def func(cur, right=None):
        for i, L in enumerate(reversed(cur.value)):
            if L in ac:
                break

        value = cur.value[:-(i+1)] + result
        return cur.set_value(value)

    return func


def vrddhi(cur, right=None):
    # 1.1.5 kGiti ca (na)
    if right and right.any_samjna('kit', 'Nit'):
        return cur

    # 1.1.1 vRddhir Adaic
    # 1.1.3 iko guNavRddhI
    converter = dict(zip('iIuUfFxX', 'EEOOAAAA'))
    letters = list(cur.value)
    for i, L in enumerate(letters):
        if L in converter:
            letters[i] = converter[L]
            if L in 'fF':
                letters[i] += 'r'
            break

    return cur.set_value(''.join(letters))


@parameterized
def upadha(L):
    def func(cur, right=None):
        return cur.upadha(L)
    return func


@parameterized
def al_tasya(target, result):
    target = Sounds(target)
    result = Sounds(result)
    def func(cur, **kw):
        letters = list(cur.value)
        for i, L in enumerate(letters):
            if L in target:
                letters[i] = Sound(L).closest(result)
                if L in 'fF' and letters[i] in Sounds('aR'):
                    letters[i] += 'r'
                break
        return cur.set_value(''.join(letters))
    return func


@parameterized
def yathasamkhya(targets, results):
    print 'yathasamkha'
    converter = dict(zip(targets, results))
    def func(cur, **kw):
        return cur.set_raw(converter[cur.raw])
    return func
