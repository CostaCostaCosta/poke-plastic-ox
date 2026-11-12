.PHONY: build check serve story validate next test

build:
	python3 build_wiki.py

check:
	python3 build_wiki.py --check

serve: build
	python3 -m http.server 8000 --directory site

story:
	python3 ../story/check_story_notes.py

validate: story check

next:
	python3 ../story/next_pass.py

test:
	python3 ../story/test_story_notes.py
