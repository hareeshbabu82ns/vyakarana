import operators as O
from sounds import Sound, Sounds
from terms import Upadesha
from util import SoundEditor, State


def convert(op):
    """A temporary fix to a deeper problem."""
    def func(s):
        return op.apply(State([Upadesha(s + 'a~')]), 0)[0].value
    return func

dirgha = O.dirgha.body
iko_yan_aci = O.al_tasya('ik', 'yaR').body
guna = convert(O.guna)
vrddhi = convert(O.vrddhi)


def apply(state):
    editor = SoundEditor(state)
    for cur in editor:
        next = cur.next
        if next.value is None:
            continue

        x, y = cur.value, next.value
        if x in Sounds('ac'):
            cur.value, next.value = ac_sandhi(x, y)
        elif x in Sounds('hal'):
            cur.value, next.value = hal_sandhi(x, y)

    yield editor.join()


def ac_sandhi(x, y):
    """Apply the rules of ac sandhi to `x` as followed by `y`.

    These rules are from 6.1. A rule is part of ac sandhi iff the first
    letter is a vowel.

    :param x: the first letter.
    :param y: the second letter.
    """

    # 6.1.97 ato guNe
    if x == 'a' and y in Sounds('at eN'):
        x = ''

    # 6.1.101 akaH savarNe dIrghaH
    elif Sound(x).savarna(y):
        x = ''
        y = dirgha(y)

    # 6.1.77 iko yaN aci
    elif x in Sounds('ik') and y in Sounds('ac'):
        x = iko_yan_aci(x)

    # 6.1.78 eco 'yavAyAvaH
    elif x in Sounds('ec') and y in Sounds('ac'):
        converter = dict(zip('eEoO', 'ay Ay av Av'.split()))
        x = converter[x]

    elif x in 'aA' and y in Sounds('ic'):
        x = ''

        # 6.1.87 Ad guNaH
        # 6.1.88 vRddhir eci
        y = vrddhi(y) if y in Sounds('ec') else guna(y)

    return x, y


def hal_sandhi(x, y):
    """Apply the rules of hal sandhi to `x` as followed by `y`.

    These rules are from 6.1. A rule is part of hal sandhi iff the first
    letter is a consonant.

    :param x: the first letter.
    :param y: the second letter.
    """

    # 6.1.66 lopo vyor vali
    if x in Sounds('v y') and y in Sounds('val'):
        x = ''

    return x, y
