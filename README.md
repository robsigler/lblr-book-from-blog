This repo contains Python scripts that were used to scrape a blog and turn it into a book-ready format to make into a gift for the blog's author.

This project ultimately failed because the blog was much less well-suited for print than we realized (lots of links, audio and video), and the book was so long the printing company could only put it in a three-ring binder, which we felt defeated the purpose of the gift (to look nice).

To produce the book, run (in a virtual environment with requirements installed):

```bash
python lblr.py
cd build
iconv -f utf-8 -t utf-8 -c build\index.html > sanitized.html
pandoc -s -o "book.docx" -t html5 -t docx sanitized.html
```
