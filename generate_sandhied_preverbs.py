import os
from sandhi_engine.sandhi_engine import SandhiEngine
from sandhi_engine.find_applicable_sandhis import FindApplicableSandhis
from itertools import permutations
from sanskrit_util import sanscript
from trie import Trie

DEVA = sanscript.DEVANAGARI
SLP = sanscript.SLP1  # sanscript.transliterate('त्र', _from=DEVA, _to=SLP)
s = SandhiEngine('sanskrit')
fa = FindApplicableSandhis('sanskrit')


def generate_perms(elts, trie):
    # limit the length of combinations to 3, following beginning of p.3 of:
    # https://www.asc.ohio-state.edu/papke.5/downloads/ICHLhandout.pdf

    # 1. simple elements, first as-is, then sandhied
    for e in elts:
        key = sanscript.transliterate(e, _from=SLP, _to=DEVA)
        trie.add(key, data=key)

    sandhied_potentials = {a.split(',')[0]: p for p in elts for a in fa.all_possible_sandhis(p)}
    for k, v in sandhied_potentials.items():
        key = sanscript.transliterate(k, _from=SLP, _to=DEVA)
        trie.add(key, data=v)

    # 2. all permutations of any two preverbs, first as-is, then sandhied
    for a, b in list(permutations(elts, r=2)):
        potentials = s.apply_sandhi(a, b)
        potentials = [p.replace(' ', '') for p in potentials]
        for pot in potentials:
            key = sanscript.transliterate(pot, _from=SLP, _to=DEVA)
            trie.add(key, data=pot)

        sandhied_potentials = {a.split(',')[0]: p for p in potentials for a in fa.all_possible_sandhis(p)}
        for k, v in sandhied_potentials.items():
            key = sanscript.transliterate(k, _from=SLP, _to=DEVA)
            trie.add(key, data=v)

    # 3. all permutations of any three preverbs, first as-is, then sandhied
    for a, b, c in list(permutations(elts, r=3)):
        first_potentials = s.apply_sandhi(a, b)
        potentials = [p.replace(' ', '') for p in first_potentials]
        for p in potentials:
            p_potentials = s.apply_sandhi(p, c)
            p_potentials = [p.replace(' ', '') for p in p_potentials]
            for pot in p_potentials:
                key = sanscript.transliterate(pot, _from=SLP, _to=DEVA)
                trie.add(key, data=pot)

            sandhied_p_potentials = {a.split(',')[0]: p for p in p_potentials for a in fa.all_possible_sandhis(p)}
            for k, v in sandhied_p_potentials.items():
                key = sanscript.transliterate(k, _from=SLP, _to=DEVA)
                trie.add(key, data=v)


# the list of the 22 preverbs taken from:
# https://en.wikipedia.org/wiki/Upasarga
preverbs = ['ati', 'aDi', 'anu', 'apa', 'api', 'aBi', 'ava', 'A', 'ut', 'ud', 'upa',
            'duH', 'ni', 'niH', 'parA', 'pari', 'pra', 'prati', 'vi', 'sam', 'su']

SH_preverbs = ["ati", "aDi", "aDyava", "aDyA", "anu", "anuni", "anuparA", "anupra", "anuvi", "anuvyava", "anusam",
               "antar", "anvA", "apa", "apA", "aBi", "aBini", "aBipra", "aBivi", "aBivyA", "aBisam", "aByanu", "aByava",
               "aByA", "aByut", "aByupa", "aByupA", "alam", "ava", "A", "Apa", "Apra", "Avis", "ut", "utpra", "udA",
               "upa", "upani", "upasam", "upA", "upAti", "upADi", "upot", "tiras", "ni", "nirava", "nirA", "nis",
               "parA", "pari", "parini", "parinis", "parisam", "paryava", "paryA", "paryut", "paryupa", "puras", "pra",
               "praRi", "prati", "pratini", "pratipra", "prativi", "pratisam", "pratyapa", "pratyaBi", "pratyava",
               "pratyA", "pratyut", "pratyudA", "pravi", "pravyA", "prasam", "prA", "prot", "bahis", "vi", "vini",
               "vinis", "viparA", "vipari", "vipra", "viprati", "visam", "vyati", "vyapa", "vyapA", "vyaBi", "vyava",
               "vyA", "vyut", "saMvi", "saMvyava", "sanni", "sam", "samanu", "samaBi", "samaBivi", "samaBivyA",
               "samalam", "samava", "samA", "samut", "samudA", "samudvi", "samupa", "samupA", "sampra", "samprati",
               "sampravi"]

# A. prepare the Trie
trie = Trie()

# add permutations of preverbs
generate_perms(preverbs, trie)

# add preverbs only found in the SH list
SH_only_preverbs = ["antar", "alam", "Avis", "tiras", "puras", "praRi", "bahis", "sanni", "samalam", "sampra",
                    "samprati", "sampravi"]
for pre in SH_only_preverbs:
    trie.add(sanscript.transliterate(pre, _from=SLP, _to=DEVA))

corpus_path = 'corpus'
corpus_names = [corpus_path+'/'+a for a in os.listdir(corpus_path)]

matches = {}
for f in corpus_names:
    with open(f, 'r') as g:
        content = g.read()
    trie.max_match(content, matches)

found_combinations = []
for k, v in matches.items():
    if len(v) > 0:
        unsandhied = v[0][1]
        if not unsandhied:
            unsandhied = ''
        found_combinations.append((sanscript.transliterate(k, _from=DEVA, _to=SLP), len(v), unsandhied))

found_preverbs = sorted(found_combinations, key=lambda x: x[1], reverse=True)

with open('SARIT_preverbs.txt', 'w') as f:
    out = []
    for p in found_preverbs:
        if p[2]:
            out.append('{}\t{}\t{}'.format(p[0], p[1], p[2]))
    f.write('\n'.join(out))
