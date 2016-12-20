.DEFAULT_GOAL := simple

simple:
	pdflatex -shell-escape Main

bib:
	pdflatex -shell-escape -halt-on-error -interaction batchmode Main \
		&& bibtex Main \
		&& pdflatex -halt-on-error -interaction batchmode Main\
		&& pdflatex -halt-on-error -interaction batchmode Main

# Clean cache
cclean:
	rm cache/*.log cache/*.pdf cache/*.md5 cache/*.dpth
