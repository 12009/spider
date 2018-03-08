# -*- coding: utf-8 -*-

def diff_body(body1 = None, body2 = None):
    s = SequenceMatcher(None, body1, body2)
    return round(s.ratio(), 3)
