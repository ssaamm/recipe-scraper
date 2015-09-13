import collections
import re
import sys
from nltk.stem.porter import PorterStemmer

DEBUG = True

Ingredient = collections.namedtuple('Ingredient', ['amount', 'name', 'cost',
'extra'])

st = PorterStemmer()
amount_re = re.compile(
r'[1-9½¼¾⅛]?( *(?:\(.*oz.*\))?.{0,6}\b(?:cups?|cranks?|whole|cans?|box|tsp|tbsp|pinch|inch(es)?|bunch|stalks?|large|medium|med\.?|small|lbs?\.?|oz\.?|cloves?))?',
re.IGNORECASE)
cost_re = re.compile(r'(\$([0-9\.]*)).*$')
prep_re = re.compile(r'(, )?(?:to taste|minced|sliced|diced|dried|grated|freshly cracked|\(optional\))', re.IGNORECASE)
def ingredient_from_string(string):
    am = amount_re.match(string)
    amount = string[am.start():am.end()] if am else ''

    cm = cost_re.search(string)
    cost = float(cm.group(2)) if cm else None

    name_beg = None
    name_end = None
    if cm:
        name_end = cm.start()
    if am:
        name_beg = am.end()
    #name = stemmer.stem(prep_re.sub('', string[name_beg:name_end]).strip())
    name = st.stem(prep_re.sub('', string[name_beg:name_end]).replace('*', '').strip())

    return Ingredient(amount=amount, name=name, cost=cost, extra='')

if __name__ == '__main__':
    ingredients = []
    with open(sys.argv[1], 'r') as f:
        for ingredient_string in f:
            i = ingredient_from_string(ingredient_string)
            if i.name.strip():
                ingredients.append(i)
            elif DEBUG:
                print('EMPTY NAME:', i, ingredient_string.strip())

    freq = collections.Counter(map(lambda i: i.name.lower(), ingredients))
    sorted_ingredients = collections.OrderedDict(sorted(freq.items(), key=lambda
        t: t[1], reverse=True))

    for name, count in sorted_ingredients.items():
        if count < 2: break
        print(count, name)
