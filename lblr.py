from lxml import html
from bs4 import BeautifulSoup
from shutil import copyfile

SRC_DIR = "C:/Users/rob/Google Drive/LBLR_Project/littlebass.com/"

def lblr():
    path_to_file = "{}/note0apr.html".format(SRC_DIR)
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
            link_href = link.get("href")
            if "javascript:open_win" in link_href:
                link_href = "{}.jpg".format(link_href.split("(")[1][:-1])
                src_img = "{}/{}".format(SRC_DIR, link_href)
                copyfile(src_img, link_href)
            img_tag = soup.new_tag("img", src=link_href)
            img_div.append(img_tag)
        new_page_body.append(date_div)
    print(new_page_body.prettify())

lblr()