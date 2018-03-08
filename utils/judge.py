from difflib import SequenceMatcher

def diff_content(new, old):
    s = SequenceMatcher(None, new, old)
    return round(s.quick_ratio(), 2)
