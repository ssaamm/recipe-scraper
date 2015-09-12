import sys
import re
import requests
import itertools
import collections
import multiprocessing
from bs4 import BeautifulSoup

DEBUG = True
Ingredient = collections.namedtuple('Ingredient', ['amount', 'name', 'cost',
'extra'])

amount_re = re.compile(
r'(.{0,10} ?(lb\.?|cups?|tbsp|tsp|oz\.?|pinch|can|cloves?) )|((\d+|½)(large|jar|package)?)',
re.IGNORECASE)
extra_re = re.compile('(to taste)|(, )((finely)? ?diced|sliced|stemmed and cut|minced)|(\([^0-9].*\))', re.IGNORECASE)
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
            name=string[nst:nen]
            .replace('*', '').strip(),
            extra=string[e.start():e.end()] if e else None,
            cost=cost)

def take(iterable, n):
    return itertools.islice(iterable, 0, n)

BUDGET_BYTES_URL = 'http://www.budgetbytes.com/'
def budget_bytes_links():
    url = BUDGET_BYTES_URL

    while True:
        bb = requests.get(url)
        soup = BeautifulSoup(bb.text, 'html.parser')

        for link in soup.find_all('h2', class_='entry-title'):
            yield link.find('a')['href']
        url = soup.find('li', class_='pagination-next').find('a')['href']

def get_ingredients(url):
    mapped_ingredients = []

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    ingredients = soup.find_all('li', class_='ingredient')

    for ingredient in ingredients:
        ingredient_string = None
        if ingredient.string:
            ingredient_string = ingredient.string
        else:
            ingredient_string = ' '.join(ingredient.stripped_strings)
        mapped_ingredient = ingredient_from_string(ingredient_string)

        if mapped_ingredient.name.strip():
            mapped_ingredients.append(mapped_ingredient)
        elif DEBUG:
            print('EMPTY NAME:\t', mapped_ingredient, ingredient_string)

    return mapped_ingredients

if __name__ == '__main__':
    pool = multiprocessing.Pool()

    urls = take(budget_bytes_links(), 500)
    ingredients = itertools.chain.from_iterable(pool.imap_unordered(get_ingredients, urls))
    pool.close()

    freq = collections.Counter(map(lambda i: i.name.lower(), ingredients))
    sorted_ingredients = collections.OrderedDict(sorted(freq.items(), key=lambda
        t: t[1], reverse=True))

    for name, count in sorted_ingredients.items():
        if count < 2: break
        print(count, name)
