# -*- coding: utf-8 -*-
"""
    vyakarana.util
    ~~~~~~~~~~~~~~

    Utility functions.

    :license: MIT and BSD
"""

import itertools


def iter_group(items, n):
    """Iterate over `items` by taking `n` items at a time."""
    for i in range(0, len(items), n):
        yield items[i:i+n]


def iter_pairwise(items):
    x, y = itertools.tee(items)
    next(y, None)
    return itertools.izip(x, y)


class Rank(object):

    """
    Among the conflict-solving mechanisms in the Ashtadhyayi is the
    notion of utsarga-apavāda. The idea is that when two rules have
    space to apply, the more general rule (utsarga) is dominated by
    the specific rule (apavāda).

    The "specificity" of a rule can be determined by the conditions
    that allow the rule to act -- for example, some rules apply only
    to certain roots, which makes them very specific -- but to do this
    automatically requires a level of code introspection that would
    greatly complicate the model.

    For that reason, this class provides a simple way to regulate
    utsarga-apavāda relationships in the Ashtadhyayi.
    """

    #: Rank of an unknown rule
    UNKNOWN = 0
    #: Rank of a general rule
    UTSARGA = 1
    #: Rank of a specific rule, as counter to an utsarga
    APAVADA = 2
    #: Rank of a rule that acts on a specific upadesha
    UPADESHA = 4
    #: Rank of a rule that acts on a specific form
    NIPATANA = 5


class State(object):
    """A sequence of terms.

    This represents a single step in some derivation."""

    __slots__ = ['items', 'history']

    def __init__(self, items, history=None):
        #: A list of :class:`Upadesha`s.
        self.items = items
        self.history = history or []

    def __eq__(self, other):
        if other is None:
            return False
        if self is other:
            return True

        return self.items == other.items

    def __ne__(self, other):
        return not self == other

    def __getitem__(self, index):
        return self.items[index]

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return '<State(%r)>' % self.items

    def __str__(self):
        return repr([x.asiddha for x in self.items])

    def debug_printout(self):
        data = []
        append = data.append
        append(str(self))
        for item in self.items:
            append('  %s' % item)
            append('    %s' % (tuple(item.data),))
            append('    %s' % sorted(item.samjna))
            append('    %s' % sorted(item.lakshana))
        append('')
        return '\n'.join(data)

    def _push_rule(self, rule, index):
        self.history.append(self.make_rule_key(rule, index))

    def copy(self):
        return State(self.items[:], self.history[:])

    def insert(self, index, item, rule=None):
        c = self.copy()
        c.items.insert(index, item)
        if rule is not None:
            c._push_rule(rule, index)
        return c

    def make_rule_key(self, rule, index):
        return (rule.name, index)

    def mark_rule(self, rule, index):
        c = self.copy()
        c._push_rule(rule, index)
        return c

    def remove(self, index):
        c = self.copy()
        c.items.pop(index)
        return c

    def replace_all(self, items):
        c = self.copy()
        c.items = items
        return c

    def swap(self, index, item, rule=None):
        c = self.copy()
        c.items[index] = item
        if rule is not None:
            c._push_rule(rule, index)
        return c


class SoundEditor(object):

    def __init__(self, state, locus='asiddha'):
        self.state = state
        self.locus = locus
        self.data = [list(term.asiddha) for term in state]

        self.indices = []
        abs_index = 0
        for i, term in enumerate(state):
            for j, sound in enumerate(term.asiddha):
                sound_index = SoundIndex(value=sound, term=term, state_index=i,
                    term_index=j, absolute_index=abs_index, editor=self)
                self.indices.append(sound_index)
                abs_index += 1

    def __iter__(self):
        for index in self.indices:
            yield index

    def join(self):
        state = self.state
        new_terms = []
        for i, term in enumerate(state):
            new_value = ''.join(L for L in self.data[i])
            new_term = self.state[i].set_at(self.locus, new_value)
            new_terms.append(new_term)

        return state.replace_all(new_terms)

    def next(self, index):
        try:
            return self.indices[index.absolute_index + 1]
        except (TypeError, IndexError):
            return SoundIndex(editor=self)

    def prev(self, index):
        try:
            new_index = index.absolute_index - 1
            if new_index >= 0:
                return self.indices[new_index]
        except TypeError:
            pass
        return SoundIndex(editor=self)


class SoundIndex(object):

    __slots__ = ['_value', 'term', 'state_index', 'term_index',
                 'absolute_index', 'editor', 'first', 'last']

    def __init__(self, value=None, term=None, state_index=None,
                 term_index=None, absolute_index=None, editor=None):
        #: The value associated with this index.
        self._value = value
        #: The term associated with this index.
        self.term = term
        #: The state index that corresponds to `self.term`.
        self.state_index = state_index
        #: The term index that corresponds to `self.value`.
        self.term_index = term_index
        #: The absolute index of this `SoundIndex` within the editor
        self.absolute_index = absolute_index
        #: The sound iterator that produced this index
        self.editor = editor

        #: True iff this is the first letter in the term.
        self.first = term_index == 0
        #: True iff this is the last letter in the term.
        self.last = term_index == len(term.value) - 1 if term else False

    @property
    def next(self):
        return self.editor.next(self)

    @property
    def prev(self):
        return self.editor.prev(self)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.editor.data[self.state_index][self.term_index] = new_value
