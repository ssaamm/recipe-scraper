RAW=raw.txt

ingredients.txt: interpret.py $(RAW)
	python $< $(RAW) > $@

$(RAW): scrape.py
	python $< > $@
