import requests
import itertools
import multiprocessing
from bs4 import BeautifulSoup

DEBUG = True

def take(iterable, n):
    return itertools.islice(iterable, n)

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
    ingredient_strings = []

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    ingredients = soup.find_all('li', class_='ingredient')

    for ingredient in ingredients:
        ingredient_string = None
        if ingredient.string:
            ingredient_string = ingredient.string
        else:
            ingredient_string = ' '.join(ingredient.stripped_strings)
        ingredient_strings.append(str(ingredient_string))

    return ingredient_strings

if __name__ == '__main__':
    pool = multiprocessing.Pool()

    urls = take(budget_bytes_links(), 500)
    ingredients = itertools.chain.from_iterable(pool.imap_unordered(get_ingredients, urls))
    pool.close()

    for ingredient in ingredients:
        print(ingredient)
