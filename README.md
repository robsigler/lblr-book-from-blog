To produce the book, run (in a virtual environment with requirements installed):

python lblr.py
cd build
iconv -f utf-8 -t utf-8 -c build\index.html > sanitized.html
pandoc -s -o "book.docx" -t html5 -t docx sanitized.html