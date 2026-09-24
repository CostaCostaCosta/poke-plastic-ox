.PHONY: build check serve

build:
	python3 build_wiki.py

check:
	python3 build_wiki.py --check

serve: build
	python3 -m http.server 8000 --directory site
