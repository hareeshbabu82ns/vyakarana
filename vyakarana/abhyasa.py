# -*- coding: utf-8 -*-
"""
    vyakarana.abhyasa
    ~~~~~~~~~~~~~~~~~

    Rules that apply specifically to an abhyāsa. These rules fall into
    two groups. The first is at the beginning of 6.1:

        6.1.1 ekAco dve prathamasya

    The second is from 7.4.58 to the end of book 7:

        7.4.58 atra lopo 'bhyAsasya

    :license: MIT and BSD
"""


import filters as F
import operators as O
from dhatupatha import DHATUPATHA as DP
from templates import *
from upadesha import Upadesha

f = F.auto

@inherit(None, 'dhatu', None)
def dvirvacana():

    @O.Operator.unparameterized
    def do_dvirvacana(state, i, locus=None):
        # 6.1.1 ekAco dve prathamasya
        # 6.1.2 ajAder dvitIyasya
        # 6.1.3 na ndrAH saMyogAdayaH
        # 6.1.4 pUrvo 'bhyAsaH
        # 6.1.5 ubhe abhyastam
        cur = state[i]
        abhyasa = Upadesha(data=cur.data, samjna=frozenset(['abhyasa']))
        abhyasta = cur.add_samjna('abhyasta')
        return state.swap(i, abhyasta).insert(i, abhyasa)

    return [
        # TODO: why stated as abhyasa?
        ('6.1.8', None, ~f('abhyasta'), 'li~w', do_dvirvacana),
        ('6.1.9', None, True, ('san', 'yaN'), True),
        ('6.1.10', None, True, F.lakshana('Slu~'), True),
        ('6.1.11', None, True, 'caN', True),
    ]


@inherit(None, None, None)
def do_samprasarana():
    # 6.1.15 vaci-svapi-yajādīnāṃ kiti
    vaci_svapi = ['va\ca~', 'Yizva\pa~'] + DP.dhatu_list('ya\\ja~^')

    # 6.1.16 grahi-jyā-vayi-vyadhi-vaṣṭi-vicati-vṛścati-pṛcchati-bhṛjjatīnāṃ
    #        ṅiti ca
    grahi_jya = ['graha~^', 'jyA\\', 'vaya~\\', 'vya\Da~', 'vaSa~',
                 'vyaca~', 'o~vraScU~', 'pra\cCa~', 'Bra\sja~^']

    return [
        ('6.1.15',
            None, vaci_svapi, 'kit',
            O.samprasarana),
        # TODO: ca
        ('6.1.16',
            None, grahi_jya, F.knit,
            True),
        # ('6.1.17',
        #     None, 'abhyasa', [vaci_svapi + grahi_jya, F.knit],
        #     True),
    ]
