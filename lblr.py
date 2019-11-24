from lxml import html
from bs4 import BeautifulSoup
from os import mkdir
from shutil import copyfile, rmtree
import logging
import sys
from urllib.parse import unquote

SRC_DIR = "C:/Users/rob/Google Drive/LBLR_Project/littlebass.com"
DEST_DIR = "D:/Development/lblr/build"

def lblr():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    logging.info("Building book-friendly version of LBLR Chronicles.")

    rmtree(DEST_DIR, ignore_errors=True)
    mkdir(DEST_DIR)

    pages = find_all_pages()
    for page in pages:
        bookify_page(page)

def find_all_pages():
    logging.info("Reading LBLR Chronicles Archive to find every page...")
    path_to_file = "{}/notesold.html".format(SRC_DIR)
    with open(path_to_file) as open_html_file:
        html_text = open_html_file.read()
    archive = BeautifulSoup(html_text, "html.parser")
    links = []
    for link in archive.find_all("a"):
        link_dest = link.get("href")
        if link_dest:
            logging.info("Found a link in LBLR Chronicles Archive: {}".format(link_dest))
            links.append(link_dest)
    # TODO: Links are ordered in reverse chronological order by year, but then within the year
    # they are in chronological order.. need to figure out how to put them in the right order
    links.reverse()
    return links

def bookify_page(page_filename):
    logging.info("Attempting to make {} book-friendly...".format(page_filename))

    path_to_file = "{}/{}".format(SRC_DIR, page_filename)
    with open(path_to_file, errors="ignore") as open_html_file:
        html_text = open_html_file.read()
    entire_page = BeautifulSoup(html_text, "html.parser")

    page_script_element = entire_page.find("script")
    image_links = {}
    if page_script_element:
        script_lines = page_script_element.contents[0].split("\n")
        for line in script_lines:
            if "=" in line and "var" in line:
                try:
                    var_half, value_half = line.split("=")
                    var_name = var_half.split()[-1]
                    var_value = unquote(value_half.split('"')[1])
                    logging.info("Found variable {}={}".format(var_name, var_value))
                    image_links[var_name] = var_value
                except ValueError as e:
                    print(e)
                    raise Exception("Failed")

    table = entire_page.find("table")

    if not table:
        logging.error("No table found! Nothing to do for {}".format(page_filename))
        return

    soup = BeautifulSoup(features="html.parser")

    new_page_body = soup.new_tag("body")
    for table_row in table.find_all("tr", recursive=False):
        columns = table_row.find_all("td", recursive=False)
        if len(columns) > 2:
            print(columns)
            sys.exit(1)
        date_column, entry_column = table_row.find_all("td", recursive=False)
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
            if link_href:
                if "javascript:open_win" in link_href:
                    link_var = unquote(link_href.split("(")[1][:-1])
                    link_href = image_links[link_var]
                    src_img = "{}/{}".format(SRC_DIR, link_href)
                    dest_img = "{}/{}".format(DEST_DIR, link_href)
                    logging.info("Copying dependent file {}...".format(link_href))
                    copyfile(src_img, dest_img)
                img_tag = soup.new_tag("img", src=link_href)
                img_div.append(img_tag)
        new_page_body.append(date_div)
    dest_html_filename = "{}/{}".format(DEST_DIR, page_filename)
    logging.info("Writing file {}...".format(dest_html_filename))
    with open(dest_html_filename, "w") as dest_html_file:
        dest_html_file.write(new_page_body.prettify())

lblr()