.DEFAULT_GOAL := simple

simple:
	pdflatex main

bib:
	pdflatex -halt-on-error -interaction batchmode main \
		&& bibtex main \
		&& pdflatex -halt-on-error -interaction batchmode main\
		&& pdflatex -halt-on-error -interaction batchmode main
