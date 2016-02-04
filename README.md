# fandjango
The Django implementation of http://fantomenindex.krats.se/

[![Build Status](https://travis-ci.org/kaj/fandjango.svg)]
(https://travis-ci.org/kaj/fandjango)

The admin isn't really used, instead a `readfiles` maintenance command
is used to read the full dataset from the xml files i keep my actual
index in.

The stylesheet and templates contains some references to the Phantom,
and there is specialized views for the generations of our hero, but it
should be simple enough to adapt the code to any other comic magazine,
if someone is interested in keeping a similar index.
