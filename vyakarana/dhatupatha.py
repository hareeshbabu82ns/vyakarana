# -*- coding: utf-8 -*-
"""
    vyakarana.dhatupatha
    ~~~~~~~~~~~~~~~~~~~~

    Coordinates access to the Dhātupāṭha.

    :license: MIT and BSD
"""

from collections import defaultdict


DHATUPATHA = None


class Dhatupatha(object):

    """A collection of all verb roots in the Sanskrit language.

    This class makes it easy to select a continuous range of roots from
    the Dhātupāṭha and query for other properties of interest, such as
    the original gaṇa.

    All data is stored in a CSV file, which is read when the program
    begins.

    The Dhātupāṭha is traditionally given as a list of roots, each
    stated in upadeśa with a basic gloss. For example::

        1.1 bhū sattāyām

    The first number indicates the root *gaṇa*, of which there are ten.
    This gaṇa determines the form that the root takes when followed by
    sārvadhātuka affixes. The second number indicates the root's
    relative position within the gaṇa.

    Although few modern editions of the text have accent markings, the
    Sanskrit grammatical tradition has preserved the original accents
    all of the original items. Per the conventions of SLP1, these are
    written as follows:

    ========  =========  ==========  ====
    Accent    SLP1       Devanagari  IAST
    ========  =========  ==========  ====
    udātta    (no mark)
    anudātta  ``\\``
    svarita   ``^``
    ========  =========  ==========  ====

    """

    def __init__(self, filename=None):
        self.gana_map = {}
        #: List of all dhatu, one for each row in the original file.
        self.all_dhatu = []
        #:
        self.index_map = defaultdict(list)

        if filename is not None:
            self.init(filename)

    def init(self, filename):
        """
        :param filename: path to the Dhatupatha file
        """
        with open(filename) as f:
            i = 0
            for line in f:
                gana, number, dhatu = line.strip().split(',')
                self.all_dhatu.append(dhatu)
                self.index_map[dhatu].append(i)
                self.gana_map[i] = gana
                i += 1

    def dhatu_range(self, start, end=None):
        """Get an inclusive list of of dhatus.

        :param start: the first dhatu in the list
        :param end: the last dhatu in the list. If ``None``, add until
                    the end of the gana.
        """
        start_index = self.index_map[start][0]

        # From `start` to the end of the gana
        if end is None:
            gana = self.gana_map[start_index]
            returned = []
            end_index = start_index
            while True:
                try:
                    dhatu = self.all_dhatu[end_index]
                    if self.gana_map[end_index] == gana:
                        returned.append(dhatu)
                    else:
                        return returned
                except IndexError:
                    return returned
                end_index += 1

        # From start to first instance of `end`
        else:
            end_index = self.index_map[end][-1]
            return self.all_dhatu[start_index:end_index]

    def dhatu_set(self, *args):
        return frozenset(self.dhatu_range(*args))


DHATUPATHA = Dhatupatha('data/dhatupatha.csv')
