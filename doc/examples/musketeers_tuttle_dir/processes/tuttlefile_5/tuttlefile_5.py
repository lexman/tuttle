# -*- coding: utf8 -*-
from os import getcwd as __get_current_dir__
from sys import path as __python__path__
__python__path__.append(__get_current_dir__())
names = ["Athos", "Porthos", "Aramis", "d'Artagnan"]
with open('characters_count.dat', 'w') as f_out:
    with open('Les_trois_mousquetaires.txt') as f_in:
        content_low = f_in.read().lower()
    print("{} chars in the novel".format(len(content_low)))
    for name in names:
        name_low = name.lower()
        f_out.write("{}\t{}\n".format(name, content_low.count(name_low)))
        print("{} - done".format(name))
