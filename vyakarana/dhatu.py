# -*- coding: utf-8 -*-
"""
    vyakarana.dhatu
    ~~~~~~~~~~~~~~~

    Rules that apply specifically to a dhātu. Almost all such rules are
    within the domain of 3.1.91:

        3.1.91 dhātoḥ

    which holds until the end of 3.4.

    :license: MIT and BSD
"""

import context as c
from classes import Dhatu, Krt
from decorators import *
from dhatupatha import DHATUPATHA as DP
import util


def adesha(state):
    """
    Perform substitutions on the dhatu. These substitutions can occur
    before ___.

    :param state:
    """

    i, dhatu = state.find('dhatu')
    tin = state[-1]

    if 'vibhakti' not in tin.samjna:
        return

    # 6.1.45 Ad eca upadeze 'ziti
    # One would expect that 'azit' means "that which does not have 'z'."
    # But instead we should interpret it as "that which does not start
    # with 'z' in upadesha. This difference allows us to apply the rules
    # when the suffix 'eS' follows. 'eS' has indicatory 'S', so normally
    # the rule would not apply; but with this change in interpretation,
    # the rule can apply.
    _45 = Dhatu(dhatu.raw).ec and tin.raw[0] != 'S'
    if _45:
        dhatu = dhatu.tasya('A')
        yield state.swap(i, dhatu)


@tasmat(c.samjna('dhatu'), c.and_(c.samjna('tin'), c.samjna('sarvadhatuka')))
def vikarana(dhatu, p):
    """Vikarana for classes 1 through 10."""

    gana_set = DP.gana_set(dhatu)

    def _yield(s):
        return Krt(s).add_samjna('anga')

    # 3.1.68 kartari śap
    if '1' in gana_set or '10' in gana_set:
        yield _yield('Sap')

    # 2.4.75 juhotyādibhyaḥ śluḥ
    # TODO: move to proper section
    if '3' in gana_set:
        yield _yield('Slu~')

    # 3.1.69 divādibhyaḥ śyan
    if '4' in gana_set:
        yield _yield('Syan')

    # 3.1.70 vā bhrāśabhlāśabhramukramuklamutrasitrutilaṣaḥ
    if dhatu.raw in ('wuBrASf~\\', 'wuBlASf~\\', 'Bramu~', 'kramu~',
                     'klamu~', 'trasI~', 'truwa~', 'laza~^'):
        yield _yield('Syan')

    # 3.1.71 yaso 'nupasargAt

    # 3.1.72 saMyasaz ca (TODO)

    # 3.1.73 svādibhyaḥ śnuḥ
    if '5' in gana_set:
        yield _yield('Snu')

    # 3.1.74 zruvaH zR ca

    # 3.1.75 akSo 'nyatarasyAM

    # 3.1.76 tanUkaraNe takSaH

    # 3.1.77 tudādibhyaḥ śaḥ
    if '6' in gana_set:
        yield _yield('Sa')

    # 3.1.78 rudhādhibhyaḥ śnam
    if '7' in gana_set:
        yield _yield('Snam')

    # 3.1.79 tanādikṛñbhya uḥ
    if '8' in gana_set:
        yield _yield('u')

    # 3.1.80 dhinvikRNvyor a ca

    # 3.1.81 kryādibhyaḥ śnā
    if '9' in gana_set:
        yield _yield('SnA')

    # 3.1.82 stambhustumbhuskambhuskumbhuskuñbhyaḥ śnuś ca
    if dhatu.raw in ('sta\mBu~', 'stu\mBu~', 'ska\mBu~', 'sku\mBu~', 'sku\Y'):
        yield _yield('Snu')


def pada_options(dhatu):
    """Decide whether a state can use parasmaipada and atmanepada.
    Some states can use both.

    :param state:
    """
    # TODO: accent
    has_para = has_atma = False

    # 1.3.12 anudAttaGita Atmanepadam
    if 'N' in dhatu.it or 'anudatta' in dhatu.it:
        has_para, has_atma = (False, True)

    # 1.3.72 svaritaJitaH kartrabhiprAye kriyAphale
    elif 'Y' in dhatu.it or 'svarita' in dhatu.it:
        has_para, has_atma = (True, True)

    # 1.3.76 anupasargAj jJaH
    # TODO: no upasarga
    elif dhatu.raw == 'jYA\\':
        has_para, has_atma = (True, True)

    # 1.3.78 zeSAt kartari parasmaipadam
    else:
        has_para, has_atma = (True, False)

    return (has_para, has_atma)
