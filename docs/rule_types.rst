Rule Types
==========

The Ashtadhyayi has **ordinary rules**, which take some input and yield some
output(s), and metarules, which describe how to interpret other rules.

.. note::
    The divisions loosely correspond to traditional definitions, but there
    is no 1:1 mapping.

Ordinary Rules
--------------

Ordinary rules, or just "rules" for short, are the bulk of the Ashtadhyayi.
These rules accept a list of terms as input, where a **term** is some group
of sounds. For example, the input to a rule might be something like
*ca + kṛ + a*. Outputs have the same form.

There are various kinds of ordinary rules;

- rules that substitute
- rules that insert
- rules that designate
- rules that block

These are described below.

Substituting
^^^^^^^^^^^^

Most rules **substitute** one term for another. They look something like this:

    C is replaced by X (when L comes before C) (when C comes before R).

Here, *L*, *C*, *R*, and *X* are terms:

- *L* is the **left context** and appears immediately before *C*. Not all
  rules use it.
- *R* is the **right context** and appears immediately after *C*. Not all
  rules use it.
- *C* is the **center context**. It defines where the substitution occurs.
- *X* is the **replacement**. It defines the new value for *C*.

For each input, we look for a place where we have *L*, *C*, and *R* in order.
Then we replace *C* with X.

For example, rule 6.1.77 of the Ashtadhyayi states that short vowels are
replaced by semivowels when followed by other vowels. Given this input:

    *ca + kṛ + a*

we have a match when *C = ṛ* and *R = a*. (*L* is unspecified, so we ignore
it.) We replace with *X = r* to get our output:

    *ca + kṛ + a → ca + kr + a*

Designating
^^^^^^^^^^^

Some rules **designate** a term by assigning some name to it.
Those rules look something like this:

    C is called X (when L comes before C) (when C comes before R).

where *X* is the name given to the center context *C*.

For example, rule 1.3.1 states that items in the Dhatupatha are called
*dhātu* ("root") Given this input:

    *bhū*

we have a match where *C = bhū*, with *L* and *R* unspecified. We then give
*bhū* the name "dhātu." In other words, *bhū* is a *dhātu*.

Inserting
^^^^^^^^^

Of the rules left, most **insert**:

    X is inserted after L (when L comes before R).

For example, rule 3.1.68 states that *a* is inserted after a verb root when
the root is followed by a certain kind of verb ending. Given this input:

    *car + ti*

we have a match where *L = car* and *R = ti*. So, we insert *X = a* to get
our output:

    *car + ti → car + a + ti*

Blocking
^^^^^^^^

Some rules are used to *block* other rules from occurring:

    C does not accept rule Y (when L comes before C) (when C comes before X).

For example, rule 1.1.5 blocks *guṇa* substitution if the right context has
a certain property.

Other rules
^^^^^^^^^^^

A few rules are combinations of the ones above. For example, rule 3.1.80
inserts one term then performs a substitution on another.

Metarules
---------

Metarules define the metalanguage used by the Ashtadhyayi. Since we're using
our own metalanguage (Python), many of these metarules are modeled implicitly.

There are basically two kinds of metarules. These are described below.

Interpreting
^^^^^^^^^^^^

Most metarules are intended to help us understand what rules in the
Ashtadhyayi mean. Such rules are called **paribhāṣā**. Some examples:

    | Terms in case 5 (*tasmāt*) define the left context. (1.1.67)
    | If *X* is just a single letter, then only the last letter of *C* is
      replaced. (1.1.52)

Contextualizing
^^^^^^^^^^^^^^^

All other metarules provide some extra context for other rules. Such rules
are called **adhikāra**. Some examples:

    | In the rules below, all inserted terms are called *pratyaya*. (3.1.1)
    | In the rules below, *L* and *R* together are replaced by *X*. (6.1.84)
