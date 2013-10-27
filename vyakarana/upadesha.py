# -*- coding: utf-8 -*-
"""
    vyakarana.upadesha
    ~~~~~~~~~~~~~~~~~~

    Classes for working with an upadeśa.

    :license: MIT and BSD
"""

import re
from collections import namedtuple
from sounds import Sound, Sounds


_DataSpace = namedtuple('_DataSpace',
                        ['raw', 'clean', 'value', 'asiddhavat', 'asiddha'])

class DataSpace(_DataSpace):

    def replace(self, **kw):
        prev = None
        new = dict()
        for field in self._fields:
            if field in kw:
                new[field] = prev = kw[field]
            elif prev:
                new[field] = prev
        return self._replace(**new)


class Upadesha(object):

    """A Term with indicatory letters."""

    __slots__ = ['data', 'samjna', 'lakshana', 'ops']
    nasal_re = re.compile('([aAiIuUfFxeEoO])~')

    def __init__(self, raw=None, data=None, samjna=None, lakshana=None, ops=None, **kw):
        if raw is not None:
            clean, it_samjna = self._parse_it(raw, **kw)
            data = DataSpace(raw, clean, clean, clean, clean)
            samjna = samjna | it_samjna if samjna else it_samjna
        self.data = data
        self.samjna = samjna
        self.lakshana = lakshana or frozenset()
        self.ops = ops or frozenset()

    def __eq__(self, other):
        if other is None:
            return False
        if self is other:
            return True
        return (self.data == other.data and
                self.samjna == other.samjna and
                self.ops == other.ops)

    def __ne__(self, other):
        return not self == other

    def __nonzero__(self):
        return True

    def __repr__(self):
        return "<%s('%s')>" % (self.__class__.__name__, self.value)

    def copy(self, data=None, samjna=None, lakshana=None, ops=None):
        return self.__class__(
            data=data or self.data,
            samjna=samjna or self.samjna,
            lakshana=lakshana or self.lakshana,
            ops=ops or self.ops
            )

    @property
    def adi(self, key='value'):
        try:
            return getattr(self.data, key)[0]
        except IndexError:
            return None

    @property
    def antya(self, key='value'):
        try:
            return getattr(self.data, key)[-1]
        except IndexError:
            return None

    @property
    def asiddha(self):
        """Return the value created by asiddha rules."""
        return self.data.asiddha

    @property
    def asiddhavat(self):
        """Return the value created by asiddhavat rules."""
        return self.data.asiddhavat

    @property
    def clean(self):
        """Return the raw value without svaras and anubandhas."""
        return self.data.clean

    @property
    def raw(self):
        """Return the raw value."""
        return self.data.raw

    @property
    def upadha(self, key='value'):
        try:
            return getattr(self.data, key)[-2]
        except IndexError:
            return None

    @property
    def value(self):
        """Return the value created by normal rules."""
        return self.data.value

    def _parse_it(self, raw, **kw):
        pratyaya = kw.pop('pratyaya', False)
        vibhakti = kw.pop('vibhakti', False)
        taddhita = kw.pop('taddhita', False)

        it = set()
        samjna = set()

        # svara
        for i, L in enumerate(raw):
            if L in ('\\', '^'):
                # anudattet and svaritet
                if raw[i - 1] == '~':
                    if L == '\\':
                        samjna.add('anudattet')
                    else:
                        samjna.add('svaritet')
                # anudatta and svarita
                else:
                    if L == '\\':
                        samjna.add('anudatta')
                    else:
                        samjna.add('svarita')

        clean = re.sub('[\\\\^]', '', raw)

        # ir
        if clean.endswith('i~r'):
            it.add('ir')
            clean = clean[-3:]

        keep = [True] * len(clean)

        # 1.3.2 "upadeśe 'janunāsika iṭ"
        for i, L in enumerate(clean):
            if L == '~':
                it.add(clean[i - 1] + 'd')
                keep[i - 1] = False
                keep[i] = False

        # 1.3.3. hal antyam
        antya = clean[-1]
        if antya in Sounds('hal'):
            # 1.3.4 "na vibhaktau tusmāḥ"
            if vibhakti and antya in Sounds('tu s m'):
                pass
            else:
                it.add(antya)
                keep[-1] = False

        # 1.3.5 ādir ñituḍavaḥ
        try:
            two_letter = clean[:2]
            if two_letter in ('Yi', 'wu', 'qu'):
                keep[0] = keep[1] = False
                if two_letter.endswith('u'):
                    samjna.add(clean[0] + 'vit')
                else:
                    samjna.add(clean[0] + 'It')
        except IndexError:
            pass

        # 1.3.6 "ṣaḥ pratyayasya"
        # 1.3.7 "cuṭū"
        #
        #     It is interesting to note that no examples involving the
        #     initial ch, jh, Th, and Dh of an affix were provided. This
        #     omission is significant since affix initials ch, jh, Th,
        #     and Dh always are replaced by Iy (7.1.2 AyaneyI...) ant
        #     (7.1.3 jho 'ntaH), ik (7.3.50 ThasyekaH), and ey (7.1.2)
        #     respectively. Thus the question of treating each of these
        #     as an it does not arise.
        #
        #                         Rama Nath Sharma
        #                         The Ashtadhyayi of Panini Vol. II
        #                         Notes on 1.3.7 (p. 145)
        adi = clean[0]
        if pratyaya:
            # no C, J, W, Q by note above.
            if raw[0] in 'zcjYwqR':
                it.add(adi)
                keep[0] = False

            # 1.3.8 "laśakv ataddhite"
            if not taddhita:
                if adi in Sounds('l S ku'):
                    it.add(adi)
                    keep[0] = False


        # 1.3.9 tasya lopaḥ
        clean = ''.join(L for i, L in enumerate(clean) if keep[i])
        samjna = samjna.union([x + 'it' for x in it])
        return clean, samjna

    def add_samjna(self, *names):
        return self.copy(
            samjna=self.samjna.union(names)
        )

    def any_samjna(self, *args):
        return any(a in self.samjna for a in args)

    def set_raw(self, raw):
        clean, it_samjna = self._parse_it(raw)
        samjna = self.samjna | it_samjna
        return self.copy(
            data=self.data.replace(raw=raw, clean=clean),
            samjna=samjna,
            lakshana=self.lakshana | set([self.raw])
        )

    def set_value(self, value):
        return self.copy(data=self.data.replace(value=value))

    def set_asiddhavat(self, asiddhavat):
        return self.copy(data=self.data.replace(asiddhavat=asiddhavat))

    def tasya(self, other, adi=False):
        """
        Perform a substitution according to the normal rules.

        :param other: the term to insert
        """
        value = self.value
        if isinstance(other, basestring):
            # 1.1.52 alo 'ntyasya
            # 1.1.55 anekAlSit sarvasya
            if len(other) <= 1:
                value = value[:-1] + other
            else:
                value = other
            return self.set_value(value)

        if not hasattr(other, 'value'):
            # 1.1.50 sthAne 'ntaratamaH
            last = Sound(self.antya).closest(other)
            value = value[:-1] + last
            return self.set_value(value)

        # 1.1.54 AdeH parasya
        if adi:
            value = other.value + value[1:]
            return self.set_value(value)

        # 1.1.47 mid aco 'ntyAt paraH
        if 'm' in other.it:
            ti = self.ti().value
            c = self.ti(ti[0] + other.value + ti[1:])

        # 1.1.46 Adyantau Takitau
        elif 'k' in other.it:
            c.value += other.value
            c.parts.append(other)
        elif 'w' in other.it:
            c.value = other.value + self.value
            c.parts.insert(0, other)

        # 1.1.52 alo 'ntyasya
        # 1.1.53 Gic ca
        elif len(other.value) == 1 or 'N' in other.it:
            c.value = self.value[:-1] + other.value
            c.parts.append(other)

        # 1.1.55 anekAlSit sarvasya
        elif 'S' in other.it or len(other.value) > 1:
            c.value = other.value
            c.parts = [other]

        else:
            raise NotImplementedError

        return c


class Anga(Upadesha):

    __slots__ = ()

    def __init__(self, *a, **kw):
        Upadesha.__init__(self, *a, **kw)
        self.samjna |= set(['anga'])


class Dhatu(Anga):

    __slots__ = ()

    def __init__(self, *a, **kw):
        Upadesha.__init__(self, *a, **kw)
        self.samjna |= set(['anga', 'dhatu'])

        value = self.value
        if not value:
            return

        # 6.1.64 dhAtvAdeH SaH saH
        if value.startswith('z'):
            value = 's' + value[1:]
            # paribhasha: nimittApAye naimittikasya api apAyaH
            converter = {'w': 't', 'W': 'T'}
            v = value[1]
            value = value[0] + converter.get(v, v) + value[2:]

        # 6.1.65 No naH
        elif value.startswith('R'):
            value = 'n' + value[1:]

        self.data = self.data.replace(value=value)


class Pratyaya(Upadesha):

    __slots__ = ()

    def __init__(self, *a, **kw):
        Upadesha.__init__(self, *a, **kw)
        self.samjna |= set(['pratyaya'])

        # 1.1.__ pratyayasya lukzlulupaH
        if self.value in ('lu~k', 'Slu~', 'lu~p'):
            self.value = ''

    def _parse_it(self, value):
        return Upadesha._parse_it(self, value, pratyaya=True)


class Krt(Pratyaya):

    __slots__ = ()

    def __init__(self, *a, **kw):
        Pratyaya.__init__(self, *a, **kw)
        self.samjna |= set(['krt'])

        # 3.4.113 tiGzit sArvadhAtukam
        # 3.4.115 liT ca (ArdhadhAtukam)
        if 'Sit' in self.samjna and self.raw != 'li~w':
            self.samjna |= set(['sarvadhatuka'])
        else:
            self.samjna |= set(['ardhadhatuka'])

        # 1.2.4 sArvadhAtukam apit
        if 'sarvadhatuka' in self.samjna and 'pit' not in self.samjna:
            self.samjna |= set(['Nit'])


class Vibhakti(Pratyaya):

    __slots__ = ()

    def __init__(self, *a, **kw):
        Pratyaya.__init__(self, *a, **kw)
        self.samjna |= set(['vibhakti'])

    def _parse_it(self, value):
        return Upadesha._parse_it(self, value, pratyaya=True, vibhakti=True)
