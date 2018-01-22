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


def generate_perms(elts):
    # limit the length of combinations to 3, following beginning of p.3 of:
    # https://www.asc.ohio-state.edu/papke.5/downloads/ICHLhandout.pdf
    permuts = []
    for a, b in list(permutations(elts, r=2)):
        potentials = s.apply_sandhi(a, b)
        potentials = [p.replace(' ', '') for p in potentials]
        sandhied_potentials = [a.split(',')[0] for p in potentials for a in fa.all_possible_sandhis(p)]
        for pot in sandhied_potentials:
            key = sanscript.transliterate(pot, _from=SLP, _to=DEVA)
            permuts.append(key)

    for a, b, c in list(permutations(elts, r=3)):
        first_potentials = s.apply_sandhi(a, b)
        potentials = [p.replace(' ', '') for p in first_potentials]
        for p in potentials:
            p_potentials = s.apply_sandhi(p, c)
            p_potentials = [p.replace(' ', '') for p in p_potentials]
            sandhied_p_potentials = [a.split(',')[0] for p in p_potentials for a in fa.all_possible_sandhis(p)]
            for key in sandhied_p_potentials:
                permuts.append(key)
    return permuts


# the list of the 22 preverbs taken from:
# https://en.wikipedia.org/wiki/Upasarga
preverbs = ['ati', 'aDi', 'anu', 'apa', 'api', 'aBi', 'ava', 'A', 'ut', 'ud', 'upa',
            'duH', 'ni', 'niH', 'parA', 'pari', 'pra', 'prati', 'vi', 'sam', 'su']
total_perms = generate_perms(preverbs)
total_perms = [sanscript.transliterate(t, _from=SLP, _to=DEVA) for t in total_perms]

trie = Trie()
for perm in total_perms:
    trie.add(perm)

corpus_path = 'corpus'
corpus_names = [corpus_path+'/'+a for a in os.listdir(corpus_path)]

matches = {}
for f in corpus_names:
    with open(f, 'r') as g:
        content = g.read()
    trie.find_matches(content, matches)

found_combinations = []
for k, v in matches.items():
    if len(v) > 0:
        found_combinations.append((sanscript.transliterate(k, _from=DEVA, _to=SLP), len(v)))

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

hundred = sorted(found_combinations, key=lambda x: x[1], reverse=True)[:110]
hundred = [a[0] for a in hundred]

only_SH, only_preverb, common = [], [], []
for pre in hundred:
    pre = pre
    if pre in SH_preverbs:
        common.append(pre)
    else:
        only_preverb.append(pre)
for pre in SH_preverbs:
    if pre not in hundred:
        only_SH.append(pre)

print(only_SH)
print(only_preverb)
print(common)
