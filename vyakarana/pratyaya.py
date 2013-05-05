# -*- coding: utf-8 -*-
"""
    vyakarana.pratyaya
    ~~~~~~~~~~~~~~~~~~

    Rules that apply specifically to a pratyaya.

    :license: MIT and BSD
"""

import gana
from classes import Term, Upadesha as U, Group
from decorators import *
from util import Rank


@once('it')
def it(state):
    """

    :param state:
    """
    i, anga = state.find('anga')
    p = state[i+1]

    status = it_status(anga, p)
    if status in ('set', 'vet'):
        yield state.swap(i+1, p.tasya(U('iw')))
    if status in ('anit', 'vet'):
        yield state


def it_status(anga, p):
    """
    Determine whether `state` takes 'iṭ'.

    With regard to 'iṭ', all verb forms behave in one of three ways:

    - they always accept 'iṭ' (seṭ)
    - they never accept 'iṭ' (aniṭ)
    - they sometimes accept 'iṭ' (veṭ)

    This function determines the 'it' status of the given state by
    applying 7.2.8 - 7.2.78. These rules are in the domain of
    6.4.1 "angasya" and thus apply to non-dhatus as well.

    :param anga:
    :param p:
    """

    status = None
    rank = Rank()

    # krt (anit)
    # ----------
    if 'krt' in p.samjna:
        # 7.2.8 neD vazi kRti
        _8 = p.adi().value in Group('vaS')

        # 7.2.9 titutratathasisusarakaseSu ca
        _9 = p.value in ('ti', 'tu', 'tra', 'ta', 'Ta', 'si', 'su', 'sara',
                         'ka', 'sa')
        if _8 or _9:
            status = 'anit'

    # upadesha (various)
    # ------------------
    # 7.2.10 ekAca upadeze 'nudAttAt
    if Term(anga.raw).one_syllable and 'anudatta' in anga.it:
        status = 'anit'
        rank.set(rank.APAVADA)

    # 7.2.11 zryukaH kiti
    if 'k' in p.it:
        if anga.clean == 'Sri' or anga.antya().value in Group('uk'):
            status = 'anit'

    # 7.2.12 sani grahaguhoz ca
    if p.value == 'san':
        # 'Sri' is excluded here.
        if anga.clean in ('grah', 'guh') or anga.antya().value in Group('uk'):
            status = 'anit'

    # 7.2.13 kRsRbhRvRstudrusruzruvo liTi
    # When followed by liT, only the roots above are aniT. Therefore,
    # any other root is denied 'aniT' status.
    if 'li~w' in p.lakshana:
        if anga.clean in gana.KRADI:
            status = 'anit'
            rank.set(rank.UPADESHA)
        elif status == 'anit':
            status = None
            rank.set(rank.UTSARGA)

    # 7.2.14 zvIdito niSThAyAm
    # 7.2.15 yasya vibhASA
    # 7.2.16 Aditaz ca
    # 7.2.17
    # 7.2.18
    # 7.2.19 dhRSizasI vaiyAtye
    # 7.2.20 dRDhaH sthUlabalayoH
    # 7.2.21 prabhau parivRDhaH
    # 7.2.22
    # 7.2.23
    # 7.2.24
    # 7.2.25 abhez cAvidUrye
    # 7.2.26 Ner adhyayane vRttam

    # vet
    # ---
    # 7.2.27 vA dAntazAntapUrNadastapaSTacchannajJAptAH
    # 7.2.28
    # 7.2.29
    # 7.2.30
    # 7.2.31
    # 7.2.32
    # 7.2.33
    # 7.2.34

    # ardhadhatuka (set, vet)
    # -----------------------
    # 7.2.35 ArdhadhAtukasyeD valAdeH
    if 'ardhadhatuka' in p.samjna and p.adi().value in Group('val'):
        if rank <= rank.UTSARGA:
            status = 'set'

        # 7.2.36 snukramor anAtmanepadanimitte
        # 7.2.37 graho 'liTi dIrghaH
        # 7.2.38 vRRto vA
        # 7.2.39
        # 7.2.40
        # 7.2.41
        # 7.2.42 liGsicor AtmanepadeSu
        # 7.2.43 Rtaz ca saMyogAdeH

        # 7.2.44 svaratisUtisUyatidhUJUdito vA
        _44 = anga.raw in ('svf', 'zUG', 'zUN', 'DUY') or 'U' in anga.it

        # 7.2.45 radhAdhibhyaz ca
        _45 = anga.clean in gana.RUDH

        if _44 or _45:
            status = 'vet'

    # 7.2.46

    # set
    # ---
    # 7.2.47

    # vet
    # ---
    # 7.2.48
    # 7.2.49
    # 7.2.50 klizaH ktvAniSThayoH
    # 7.2.51

    # set
    # ---
    # 7.2.52
    # 7.2.53
    # 7.2.54
    # 7.2.55

    # vet
    # ---
    # 7.2.56
    # 7.2.57

    # set
    # ----
    # 7.2.58

    # anit
    # ----
    # 7.2.59
    # 7.2.60 tAsi ca klRpaH

    # thal (anit, vet)
    # ----------------
    if p.value == 'Ta':
        # 7.2.61 acas tAsvat thaly aniTo nityam
        _61 = anga.ac

        # 7.2.62 upadeze 'tvataH
        _62 = 'a' in anga.clean

        # 7.2.63 Rto bhAradvAjasya
        _63 = anga.antya().value == 'f'

        if rank <= rank.APAVADA:
            if _63:
                status = 'anit'
            elif _61 or _62:
                tasvat = it_status(anga, U('tAs'))
                if tasvat == 'anit':
                    status = 'vet'
                elif tasvat in ('set', 'vet'):
                    status = 'anit'

        # 7.2.64 babhUvAtatanthajagRmbhavavartheti nigame
        #        Implicitly, 'iT' is obligatory in normal language.
        if anga.clean in ('BU', 'tan', 'grah', 'vf'):
            status = 'set'

        # 7.2.65 vibhASA sRjidRzoH
        elif anga.clean in ('sfj', 'dfS'):
            status = 'vet'

        # 7.2.66 iD attyarttivyayatInAm
        elif anga.clean in ('ad', 'f', 'vye'):
            status = 'set'

    # 7.2.67

    # vet
    # ---
    # 7.2.68
    # 7.2.69

    # set
    # ---
    # 7.2.70
    # 7.2.71
    # 7.2.72
    # 7.2.73
    # 7.2.74
    # 7.2.75 kiraz ca paJcabhyaH
    # 7.2.76 rudAdibhyaH sArvadhAtuke
    # 7.2.77 IzaH se
    # 7.2.78 IDajanor dhve ca

    return status or 'anit'
