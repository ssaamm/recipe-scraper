import collections
import re
import sys

DEBUG = True

Ingredient = collections.namedtuple('Ingredient', ['amount', 'name', 'cost',
'extra'])

amount_re = re.compile(
r'(.{0,10} ?(lb\.?|cups?|tbsp|tsp|oz\.?|pinch|cloves?) )|((\d+|½|¼)(large|medium|small|jar|package)?)',
re.IGNORECASE)
extra_re = re.compile('(, )((finely)? ?diced|sliced|stemmed and cut|minced)|(\([^0-9½¼].*\))', re.IGNORECASE)
#extra_re = re.compile('(to taste|(, )?(finely)? ?diced)|(\(.*\))', re.IGNORECASE)

cost_re = re.compile(r'\$.*$')
def ingredient_from_string(string):
    a = amount_re.match(string)
    c = cost_re.search(string)
    e = extra_re.search(string)

    nst = a.end() if a else None
    nen = e.start() if e else c.start() if c else None
    cost = None
    if c:
        try:
            cost = float(string[c.start() + 1:c.end()].replace('*', ''))
        except ValueError as x:
            if DEBUG:
                print(x)

    return Ingredient(amount=string[a.start():a.end()] if a else None,
            name=string[nst:nen].replace('*', '').replace('to taste', '').strip(),
            extra=string[e.start():e.end()] if e else None,
            cost=cost)

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
