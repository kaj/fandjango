# -*- coding: utf-8 -*-

def makeslug(string):
    from re import sub
    t = string.lower()
    for p, r in ((u'[åäáàâã]', 'a'),
                 (u'[éèëêẽ]', 'e'),
                 (u'[íìïîĩ]', 'i'),
                 (u'[úùüûũ]', 'u'),
                 (u'[ńǹñ]', 'n'),
                 (u'[óòöôõ]', 'o'),
                 (r'[^a-z0-9 ]', ''), 
                 (r'[\s-]+', '_')):
        t = sub(p, r, t)
    return t
