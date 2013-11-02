# -*- coding: utf-8 -*-
"""
    vyakarana.filters
    ~~~~~~~~~~~~~~~~~

    Excluding paribhāṣā, all rules in the Ashtadhyayi describe a context
    then specify an operation to apply based on that context. Within
    this simulator, a rule's context is defined using *filters*, which
    return a true or false value for a given term within some state.

    This module defines a variety of parameterized and unparameterized
    filters, as well as as some basic operators for combining filters.

    :license: MIT and BSD
"""

from collections import defaultdict

from dhatupatha import DHATUPATHA as DP
from sounds import Sounds
from util import Rank


class Filter(object):

    """A callable class that returns true or false.

    The program uses :class:`Filter` objects in order to make use of
    ``&``, ``|``, and ``~``. These operators give us a terse way to
    create more complex conditions, e.g. ``al('hal') & upadha('a')``.
    """

    CACHE = {}

    def __init__(self, name, body, rank):
        #: A unique name for this filter
        self.name = name
        #: The function that corresponds to this filter
        self.body = body
        #: The relative rank of this filter. More specific filters
        #: have higher rank.
        self.rank = rank

    def __call__(self, state, index):
        return self.body(state, index)

    def __repr__(self):
        return '<f(%s)>' % self.name

    def __and__(self, other):
        """Bitwise "and" (``&``).

        The result is a function that matches the logical "and" of the
        two filters.

        :param other: the other :class:`Filter`.
        """
        return and_(self, other)

    def __invert__(self):
        """Bitwise "not" (``~``).

        The result is a function that matches the "not" of the current
        filter.
        """
        return not_(self)

    def __or__(self, other):
        """Bitwise "or" (``|``).

        The result is a function that matches the logical "or" of the
        two filters.

        :param other: the other :class:`Filter`.
        """
        return or_(self, other)

    @classmethod
    def parameterized(cls, fn):
        """Decorator constructor for parameterized filters.

        :param fn: a function factory. It accepts parameters and returns
                   a parameterized filter function.
        """

        cache = cls.CACHE
        def wrapped(*params):
            try:
                if hasattr(params[0], '__call__'):
                    param_str = ', '.join(f.name for f in params)
                    name = "%s(%s)" % (fn.__name__, param_str)
                else:
                    name = "%s(%s)" % (fn.__name__, ', '.join(params))
            except IndexError:
                name = "%s()" % fn.__name__
            name = name.replace('_', '')

            if name not in cache:
                body, rank = fn(*params)
                cache[name] = cls(name=name, body=body, rank=rank)
            return cache[name]
        return wrapped

    @classmethod
    def unparameterized(cls, fn):
        """Decorator constructor for unparameterized filters.

        :param fn: some filter function.
        """
        return cls(name=fn.__name__, body=fn, rank=Rank())

    def subset_of(self, filt):
        if self.name == filt.name:
            return True
        try:
            return any(x.subset_of(filt) for x in self.body.members)
        except AttributeError:
            return False

    def required(self):
        returned = set()
        try:
            for m in self.body.members:
                returned |= m.required()
        except AttributeError:
            name = self.name
            if name != 'allow_all':
                returned.add(self)

        return returned


class TermFilter(Filter):

    def __call__(self, state, index):
        try:
            term = state[index]
            return term and self.body(term)
        except IndexError:
            return False


# Parameterized filters
# ~~~~~~~~~~~~~~~~~~~~~
# Each function accepts arbitrary arguments and returns a body and rank.

@TermFilter.parameterized
def adi(*names):
    """Filter on the sounds at the beginning of the term.

    :param names: a list of sounds
    """
    sounds = Sounds(*names)
    def func(term):
        return term.adi in sounds

    return func, Rank.with_al(sounds)


@TermFilter.parameterized
def al(*names):
    """Filter on the sounds at the end of the term.

    :param names: a list of sounds
    """
    sounds = Sounds(*names)
    def func(term):
        return term.antya in sounds

    return func, Rank.with_al(sounds)


@TermFilter.parameterized
def gana(start, end=None):
    gana_set = DP.dhatu_set(start, end)
    def func(term):
        return term.raw in gana_set

    return func, Rank.with_upadesha(gana_set)


@TermFilter.parameterized
def lakshana(*names):
    """Filter on the ``raw`` property of the term, as well as `lakshana`.

    :param names: a list of raw values
    """
    names = frozenset(names)
    def func(term):
        return any(n in term.lakshana for n in names)

    return func, Rank.with_upadesha(names)


@TermFilter.parameterized
def raw(*names):
    """Filter on the ``raw`` property of the term.

    :param names: a list of raw values
    """
    names = frozenset(names)
    def func(term):
        return term.raw in names

    return func, Rank.with_upadesha(names)


@TermFilter.parameterized
def samjna(*names):
    """Filter on the ``samjna`` property of the term.

    :param names: a list of samjnas
    """
    def func(term):
        return any(n in term.samjna for n in names)

    return func, Rank.with_samjna(names)


@TermFilter.parameterized
def upadha(*names):
    """Filter on the penultimate letter of the term.

        1.1.65 alo 'ntyāt pūrva upadhā

    :param names:
    """
    sounds = Sounds(*names)
    def func(term):
        return term.upadha in sounds

    return func, Rank.with_al(sounds)


@TermFilter.parameterized
def value(*names):
    """Filter on the ``value`` property of the term.

    :param names: a list of values
    """
    names = frozenset(names)
    def func(term):
        return term.value in names

    return func, Rank.with_upadesha(names)


@Filter.parameterized
def and_(*filters):
    """Create a filter that returns ``all(f(*args) for f in filters)``

    :param filters: a list of :class:`Filter`s.
    """
    def func(state, index):
        return all(f(state, index) for f in filters)

    func.members = filters
    return func, Rank.and_(f.rank for f in filters)


@Filter.parameterized
def or_(*filters):
    """Create a filter that returns ``any(f(*args) for f in filters)``

    :param filters: a list of :class:`Filter`s.
    """
    def func(state, index):
        return any(f(state, index) for f in filters)

    return func, Rank.or_(f.rank for f in filters)


@Filter.parameterized
def not_(filt):
    """Create a filter that returns ``not any(f(*args) for f in filters)``

    :param filt: a :class:`Filter`.
    """
    def func(state, index):
        return not filt(state, index)

    return func, filt.rank


# Unparameterized filters
# ~~~~~~~~~~~~~~~~~~~~~~~
# Each function defines a filter body.

@TermFilter.unparameterized
def Sit_adi(term):
    return term.raw and term.raw[0] == 'S'


@Filter.unparameterized
def placeholder(*args):
    """Matches nothing."""
    return False


@Filter.unparameterized
def allow_all(*args):
    """Matches everything."""
    return True


@TermFilter.unparameterized
def samyoga(term):
    hal = Sounds('hal')
    return term.antya in hal and term.upadha in hal


@TermFilter.unparameterized
def samyogadi(term):
    value = term.value
    hal = Sounds('hal')
    try:
        return value[0] in hal and value[1] in hal
    except IndexError:
        return False


@TermFilter.unparameterized
def samyogapurva(term):
    value = term.value
    hal = Sounds('hal')
    try:
        return value[-2] in hal and value[-1] in hal
    except IndexError:
        return False


@TermFilter.unparameterized
def term_placeholder(term):
    return False


asavarna = term_placeholder
ekac = term_placeholder
each = term_placeholder


# Automatic filter
# ~~~~~~~~~~~~~~~~

def auto(data):
    """Create a filter to match the context specified by `data`.

    :param data:
    """
    hal_it = set([L + 'it' for L in 'kKGNYwqRpmS'])
    ac_it = set([L + 'dit' for L in 'aiufx'])
    samjna_set = set([
        'atmanepada', 'parasmaipada',
        'dhatu', 'anga', 'pada', 'pratyaya',
        'krt', 'taddhita',
        'sarvadhatuka', 'ardhadhatuka',
        'abhyasa', 'abhyasta',
        'tin', 'sup',
    ])
    samjna_set |= (hal_it | ac_it)
    sound_set = set([
        'a', 'at',
        'i', 'it',
        'u', 'ut',
        'f', 'ft',
        'ak', 'ik',
        'ac', 'ec',
        'yaY',
        'JaS', 'jaS',
        'car',
        'hal', 'Jal',
    ])
    pratyaya_set = set([
        'luk', 'Slu', 'lup',
        'la~w', 'li~w', 'lu~w', 'lf~w', 'le~w', 'lo~w',
        'la~N', 'li~N', 'lu~N', 'lf~N',
        'Sap', 'Syan', 'Snu', 'Sa', 'Snam', 'u', 'SnA',
        'Ric',
    ])

    if data is None:
        return allow_all

    if hasattr(data, '__call__'):
        return data

    # Make `data` iterable
    if isinstance(data, basestring):
        data = [data]

    parsed = defaultdict(list)
    for datum in data:
        matcher = None
        # String selector: value, samjna, or sound
        if isinstance(datum, basestring):
            if datum in samjna_set:
                parsed['samjna'].append(datum)
            elif datum in sound_set:
                parsed['al'].append(datum)
            elif datum in pratyaya_set:
                parsed['lakshana'].append(datum)
            else:
                parsed['raw'].append(datum)

        # Function
        elif hasattr(datum, '__call__'):
            parsed['functions'].append(datum)
        else:
            raise NotImplementedError(datum)


    # Create filter
    base_filter = None
    d = {
        'raw': raw,
        'lakshana': lakshana,
        'samjna': samjna,
        'al': al
    }
    for key in ['raw', 'lakshana', 'samjna', 'al']:
        values = parsed[key]
        if values:
            matcher = d[key](*values)
            if base_filter is None:
                base_filter = matcher
            else:
                base_filter |= matcher

    if parsed['functions']:
        print base_filter, 'OR', parsed['functions']
        base_filter = or_(base_filter, *parsed['functions'])
    return base_filter


# Common filters
# ~~~~~~~~~~~~~~

knit = samjna('kit', 'Nit')
