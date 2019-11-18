from lxml import html
from bs4 import BeautifulSoup
from shutil import copyfile
import logging

SRC_DIR = "C:/Users/rob/Google Drive/LBLR_Project/littlebass.com/"
DEST_DIR = "D:/Development/lblr/build"

def lblr():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    logging.info("Building book-friendly version of LBLR Chronicles.")
    day_filename = "note0apr.html"
    bookify_day(day_filename)

def bookify_day(day_filename):
    path_to_file = "{}/{}".format(SRC_DIR, day_filename)
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
                dest_img = "{}/{}".format(DEST_DIR, link_href)
                logging.info("Copying dependent file {}...".format(link_href))
                copyfile(src_img, dest_img)
            img_tag = soup.new_tag("img", src=link_href)
            img_div.append(img_tag)
        new_page_body.append(date_div)
    dest_html_filename = "{}/{}".format(DEST_DIR, day_filename)
    logging.info("Writing file {}...".format(dest_html_filename))
    with open(dest_html_filename, "w") as dest_html_file:
        dest_html_file.write(new_page_body.prettify())

lblr()