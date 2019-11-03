from lxml import html
from bs4 import BeautifulSoup

def lblr():
    path_to_file = "C:/Users/rob/Google Drive/LBLR_Project/littlebass.com/note0apr.html"
    with open(path_to_file) as open_html_file:
        html_text = open_html_file.read()
    entire_page = BeautifulSoup(html_text, "html.parser")
    table = entire_page.find("table")

    soup = BeautifulSoup(features="html.parser")

    new_page_body = soup.new_tag("body")
    for table_row in table.find_all("tr"):
        date_column, entry_column = table_row.find_all("td")
        date = date_column.text.strip()

        links = entry_column.find_all("a")
        entry = entry_column.text.strip()

        date_div = soup.new_tag("div")

        date_paragraph = soup.new_tag("p")
        date_div.append(date_paragraph)
        date_paragraph.string = date

        text_paragraph = soup.new_tag("p")
        date_div.append(text_paragraph)
        text_paragraph.string = entry

        img_div = soup.new_tag("div")
        date_div.append(img_div)
        for link in links:
            img_tag = soup.new_tag("img", href=link.get("href"))
            img_div.append(img_tag)
        new_page_body.append(date_div)
    print(new_page_body.prettify())

lblr()