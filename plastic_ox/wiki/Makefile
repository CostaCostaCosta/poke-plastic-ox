.PHONY: build check serve edit story validate next direction test editor-test region-test

build:
	python3 build_wiki.py

check:
	python3 build_wiki.py --check

serve: build
	python3 -m http.server 8000 --directory site

edit:
	python3 editor/serve.py

story:
	python3 ../story/check_story_notes.py

validate: story check

next:
	python3 ../story/next_pass.py

direction:
	python3 ../story/direction.py --all-dirty

test: editor-test region-test
	python3 ../story/test_story_notes.py

editor-test:
	python3 editor/test_editor.py

region-test:
	python3 ../story/test_region.py
