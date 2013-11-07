# -*- coding: utf-8 -*-
"""
    vyakarana.templates
    ~~~~~~~~~~~~~~~~~~~

    This module contains classes and functions that let us define
    the Ashtadhyayi's rules as tersely as possible. For example, most
    rules are defined as lists of tuples, which this module then
    synthesizes into a more usable form.

    :license: MIT and BSD
"""

import filters as F
import lists
import operators as O
from util import Rank

# New-style rules. Temporary.
ALL_RULES = []


# Rule conditions
# ~~~~~~~~~~~~~~~

class TupleWrapper(object):

    """Wrapper for tuple rules.

    The Ashtadhyayi uses a variety of terms to control when and how a
    rule applies. For example, 'anyatarasyām' denotes that a rule
    specifies an optional operation that can be accepted or rejected.

    In this system, these terms are marked by wrapping a rule in this
    class or one of its subclasses.
    """

    def __init__(self, *args):
        self.data = args

    def __repr__(self):
        return '<%s(%s)>' % self.__class__.__name__, repr(self.data)


class Ca(TupleWrapper):
    """Wrapper for a rule that contains the word "ca".

    "ca" has a variety of functions, but generally it preserves parts
    of the previous rule in the current rule.
    """


class Na(TupleWrapper):
    """Wrapper for a rule that just blocks other rules."""


class Nityam(TupleWrapper):
    """Wrapper for a rule that cannot be rejected.

    This is used to cancel earlier conditions.
    """


class Option(TupleWrapper):
    """Wrapper for a rule that can be accepted optionally.

    This is a superclass for a variety of optional conditions.
    """


class Anyatarasyam(Option):
    """Wrapper for a rule that is indifferently accepted.

    Modern scholarship rejects the traditional definition of anyatarasyām,
    but this system treats it as just a regular option.
    """


class Va(Option):
    """Wrapper for a rule that is preferably accepted.

    Modern scholarship rejects the traditional definiton of vā, but
    this system treats it as just a regular option.
    """


class Vibhasha(Option):
    """Wrapper for a rule that is preferably not accepted.

    Modern scholarship rejects the traditional definiton of vibhāṣā,
    but this system treats it as just a regular option.
    """


class Artha(Option):
    """Wrapper for a rule that applies only in some semantic condition.

    Since the semantic condition can be declined, this is essentially
    an optional provision.
    """


class Opinion(Option):
    """Wrapper for a rule that is accepted by prior opinion.

    Since the opinion can be declined, this is essentially the same as
    an optional provision.
    """


# Rule classes
# ~~~~~~~~~~~~

class Rule(object):

    """A single rule from the Ashtadhyayi.

    Rules are of various kinds. Currently, the system deals only with
    transformational rules ("vidhi") explicitly.
    """

    #: Rank of an ordinary rule
    VIDHI = 0
    #: Rank of a meta-rule.
    SAMJNA = 1
    ATIDESHA = 1
    PARIBHASHA = 1
    #: The current rule type, which is used to create the rule rank.
    RULE_TYPE = VIDHI

    # Rank of an ordinary locus
    NORMAL_LOCUS = 1
    ASIDDHAVAT = 0

    def __init__(self, name, filters, operator, **kw):
        #: A unique ID for this rule, e.g. "6.4.1"
        self.name = name

        #: A list of filter functions to apply to some subsequence in
        #: a state. If the subsequence matches, then we can apply the
        #: rule to the subsequence.
        self.filters = filters

        #:
        self.operator = self._make_operator(operator)

        #:
        self.locus = kw.pop('locus', 'value')

        #: The relative strength of this rule. The higher the rank, the
        #: more powerful the rule.
        self.rank = self._make_rank(self.locus, filters)

        #:
        self.option = kw.pop('option', None)

        #: A list of rules. These rules are all blocked if the current
        #: rule can apply.
        self.utsarga = []

    def __repr__(self):
        class_name = self.__class__.__name__
        return '<%s(%s)>' % (class_name, self.name)

    def __str__(self):
        return self.name

    @classmethod
    def new(self, name, left, center, right, result, **kw):
        if center[0] is F.allow_all and result not in lists.SAMJNA:
            returned = TasmatRule(name, left + right, result, **kw)
        else:
            if kw.get('category') == 'paribhasha':
                cls = ParibhashaRule
            elif result in lists.SAMJNA:
                cls = SamjnaRule
            elif result in lists.IT:
                cls = SamjnaRule
            else:
                cls = TasyaRule

            if left and left[0] == F.allow_all:
                left = []
            if right and right[0] == F.allow_all:
                right = []

            returned = cls(name, left + center + right, result, **kw)

        returned.offset = len(left)
        returned.modifier = kw.get('modifier')
        return returned

    def _make_operator(self, op):
        """Create and return an :class:`~operators.Operator`.

        :param op: an arbitrary object
        """
        return op

    def _make_rank(self, locus, filters):

        if locus == 'asiddhavat':
            rank_locus = Rule.ASIDDHAVAT
        else:
            rank_locus = Rule.NORMAL_LOCUS

        rank = Rank.and_(f.rank for f in filters)
        rank = rank.replace(category=self.RULE_TYPE, locus=rank_locus)
        return rank

    def apply(self, state, index):
        """Apply this rule and yield the results.

        :param state: a state
        :param index: the index where the first filter is applied.
        """
        if self.option:
            # Option declined. Mark the state but leave the rest alone.
            yield state.mark_rule(self, index)

        # 'na' rule. Apply no operation, but block any general rules
        # from applying.
        if self.modifier is Na:
            new = state.mark_rule(self, index)
            new = new.swap(index, new[index].add_op(*self.utsarga))
            yield new
            return

        # Mandatory, or option accepted. Apply the operator and yield.
        # Also, block all utsarga rules.
        #
        # We yield only if the state is different; otherwise the system
        # will loop.
        new = self.operator(state, index + self.offset, self.locus)
        if new != state:
            new = new.mark_rule(self, index)
            new = new.swap(index, new[index].add_op(*self.utsarga))
            yield new

    def features(self):
        feature_set = set()
        for i, filt in enumerate(self.filters):
            feature_set.update((f, i) for f in filt.supersets)
        return feature_set

    def has_apavada(self, other):
        """Return whether the other rule is an apavada to this one.

        Rule B is an apavada to rule A if and only if:
        1. A != B
        2. If A matches some position, then B matches too.
        3. A and B have the same locus
        4. The operations performed by A and B are in conflict

        For details on what (4) means specifically, see the comments on
        :meth:`operators.Operator.conflicts_with`.

        :param other: a rule
        """

        # Condition 1
        if self.name == other.name:
            return False

        # Condition 2
        filter_pairs = zip(self.filters, other.filters)
        if not all(f2.subset_of(f1) for f1, f2 in filter_pairs):
            return False

        # Condition 3
        if self.locus != other.locus:
            return False

        # Condition 4
        return self.operator.conflicts_with(other.operator)

    def has_utsarga(self, other):
        """Return whether the other rule is an utsarga to this one.

        :param other: a rule
        """
        # A is an utsarga to B iff B is an apavada to A.
        return other.has_apavada(self)

    def matches(self, state, index):
        """

        This applies filters sequentially from ``state[index]``.

        :param state: the current :class:`State`
        :param index: an index into the state
        """
        for i, filt in enumerate(self.filters):
            if not filt(state, index + i):
                return False
        return True

    def yields(self, state, index):
        if self.matches(state, index) and self.name not in state[index].ops:
            for result in self.apply(state, index):
                return True
        return False

    def pprint(self):
        data = []
        append = data.append
        append('Rule %s' % self.name)
        append('    Filters  :')
        for f in self.filters:
            append('           %r' % f)
        append('    Operator : %r' % self.operator)
        append('    Rank     : %r' % (self.rank,))
        append('')
        print '\n'.join(data)


class TasyaRule(Rule):

    """A substitution rule.

    For some locus ``(state, index)``, the rule applies filters starting
    from ``state[index - 1]``. `self.operator` is a function that accepts
    an :class:`Upadesha` and a state with its index and returns a new
    :class:`Upadesha`, which is saved at ``state[index]``.
    """

    def _make_operator(self, op):
        if hasattr(op, '__call__'):
            return op
        else:
            return O.tasya(op)


class SamjnaRule(TasyaRule):

    """A saṃjñā rule.

    For some locus ``(state, index)``, the rule applies filters starting
    from ``state[index - 1]``. `self.operator` is a string that defines
    the saṃjñā to add to the term.

    Programmatically, this rule is a :class:`TasyaRule`.
    """

    RULE_TYPE = Rule.SAMJNA

    def _make_operator(self, op):
        self.domain = op
        return O.add_samjna(op)


class AtideshaRule(SamjnaRule):

    RULE_TYPE = Rule.ATIDESHA


class TasmatRule(Rule):

    """An insertion rule.

    For some locus ``(state, index)``, the rule applies filters starting
    from ``state[index]``. `self.operator` is an :class:`Upadesha` that
    is inserted at ``state[index]``.
    """

    __slots__ = ()

    def _make_operator(self, op):
        return O.insert(op)


class ParibhashaRule(Rule):

    RULE_TYPE = Rule.PARIBHASHA


# Rule creators
# ~~~~~~~~~~~~~

def generate_filter(data, base=None, prev=None):
    """Create and return a filter for a tuple rule.

    :param data: one of the following:
                 - ``None``, which signals that `base` should be used.
                 - ``True``, which signals that `prev` should be used.
                 - an arbitrary object, which is sent to `filters.auto`.
                   The result is "and"-ed with `base`, if `base` is
                   defined.
    :param base: the corresponding base filter.
    :param prev: the corresponding filter created on the previous tuple.
    """
    if data is None:
        return base
    if data is True:
        return prev

    extension = F.auto(data)
    if base is None or base is F.allow_all:
        return extension
    else:
        return extension & base


def process_tuples(rules, base):
    """

    :param rules: a list of tuple rules
    :param base: a list of :class:`Filter`s.
    """
    prev = (None, None, None)
    prev_operator = None

    for row in rules:
        kw = {
            'option': False,
            'modifier': None,
        }

        if isinstance(row, TupleWrapper):
            modifier = row.__class__
            kw['option'] = isinstance(row, Option)
            kw['modifier'] = modifier
            row = row.data

        assert len(row) == 5

        name = row[0]
        window = row[1:4]
        operator = row[4]

        filters = []
        for b, w, p in zip(base, window, prev):
            filters.append(generate_filter(w, base=b, prev=p))

        if operator is True:
            operator = prev_operator

        yield name, filters, operator, kw
        prev, prev_operator = (filters, operator)


def inherit(*base, **base_kw):
    """

    """

    base = [F.auto(x) for x in base]

    def decorator(fn):
        rules = fn()

        for name, filters, operator, rule_kw in process_tuples(rules, base):
            left, center, right = filters

            kw = dict(base_kw, **rule_kw)
            rule = Rule.new(name, [left], [center], [right],
                            operator, **kw)
            ALL_RULES.append(rule)

    return decorator
