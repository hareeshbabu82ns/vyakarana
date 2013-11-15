# Vyākaraṇa

`vyakarana` derives Sanskrit words by applying the rules of the Ashtadhyayi.
For a given step in the derivation, the system repeatedly selects and applies
an appropriate rule until no further changes can be made.

## Current progress

Strong support for *liṭ* and *laṭ*. Experimental support for *lṛṭ*.

## Setup

`vyakarana` has no external dependencies. [pytest](http://pytest.org/latest/)
is used for testing. To install pytest, run

    pip install pytest

Or just install from requirements.txt:

    pip install -r requirements.txt

## Tests

All test code is in the `test` directory. To run all tests:

    py.test test/*.py --tb=line

## Documentation

Go to http://vyakarana.readthedocs.org for details.
