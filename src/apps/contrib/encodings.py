# -*- coding: utf-8 -*-


def clean_accents(string):
    from unicodedata import normalize
    if type(string) is unicode:
        return normalize('NFKD', string).encode('ASCII', 'ignore')
    return normalize('NFKD', string.decode('utf-8')).encode('ASCII', 'ignore')
