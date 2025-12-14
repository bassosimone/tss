"""Trusted Secret-Santa generator.

We support generating secret-santa pairings locally
and sharing them as person-specific URLs.

We require the following input:

1. a file containing the name of each person;

2. a file containing bindings for couples, such that
we don't pair two persons in a couple.

The Secret-Santa is trusted in that the operator
potentially knows all the pairsing.
"""
