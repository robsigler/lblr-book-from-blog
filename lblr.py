from lxml import html
from bs4 import BeautifulSoup
from os import mkdir, makedirs
from shutil import copyfile, rmtree
import logging
import sys
from urllib.parse import unquote

SRC_DIR = "C:/Users/rob/Google Drive/LBLR_Project/littlebass.com"
DEST_DIR = "D:/Development/lblr/build"
BLACKLIST = []

PROBLEMATIC_LINKS = []
NO_TABLE_PAGES = []

def lblr():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    logging.info("Building book-friendly version of LBLR Chronicles.")

    rmtree(DEST_DIR, ignore_errors=True)
    mkdir(DEST_DIR)

    pages = find_all_pages()
    logging.info("list of all pages:")
    logging.info(pages)
    BLACKLIST.extend(pages)
    html_pages = []
    for page in pages:
        html_page = bookify_page(page)
        if html_page:
            html_pages.append(html_page)

    dest_html_filename = "{}/index.html".format(DEST_DIR)
    logging.info("Writing {}...".format(dest_html_filename))
    with open(dest_html_filename, "w") as dest_html_file:
        for html_page in html_pages:
            dest_html_file.write(html_page.prettify())
    logging.info("We found {} problematic links".format(len(PROBLEMATIC_LINKS)))
    logging.info(PROBLEMATIC_LINKS)

    logging.info("We found {} no-table-pages".format(len(NO_TABLE_PAGES)))
    logging.info(NO_TABLE_PAGES)

def find_all_pages():
    logging.info("Reading LBLR Chronicles Archive to find every page...")
    path_to_file = "{}/notesold.html".format(SRC_DIR)
    with open(path_to_file) as open_html_file:
        html_text = open_html_file.read()
    archive = BeautifulSoup(html_text, "html.parser")
    links = []
    months = []
    month = None
    year_long_pages = [
        "notes04.html",
        "notes01.html",
        "notes00.html",
        "notes99.html",
        "notes97.html",
    ]
    for link in archive.find_all("a"):
        link_dest = link.get("href")
        if link_dest:
            logging.debug("Found a link in LBLR Chronicles Archive: {}".format(link_dest))
            if link_dest in year_long_pages:
                pass
            if "jan" in link_dest:
                if month:
                    month.reverse()
                    links.extend(month)
                month = [link_dest]
            else:
                month.append(link_dest)
    month.reverse()
    links.extend(month)
    links.extend(year_long_pages)
    links.reverse()
    return links

def get_html_soup(filename):
    path_to_file = "{}/{}".format(SRC_DIR, filename)
    with open(path_to_file, errors="ignore") as open_html_file:
        html_text = open_html_file.read()
    return BeautifulSoup(html_text, "html.parser")

def copy_from_src_to_dir(link_href):
    src = "{}/{}".format(SRC_DIR, link_href)
    dest = "{}/{}".format(DEST_DIR, link_href)
    # Need to make sure that the directory we are copying to exists
    img_dest_dir = "/".join(dest.split("/")[:-1])
    makedirs(img_dest_dir, exist_ok=True)
    logging.debug("Copying dependent file {}...".format(link_href))
    copyfile(src, dest)

def copy_all_images_found(soup):
    img_tags = soup.find_all("img")
    for img_tag in img_tags:
        img_src = img_tag.get("src")
        copy_from_src_to_dir(img_src)

def bookify_page(page_filename):
    logging.debug("Attempting to make {} book-friendly...".format(page_filename))

    entire_page = get_html_soup(page_filename)

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
                    logging.debug("Found variable {}={}".format(var_name, var_value))
                    image_links[var_name] = var_value
                except ValueError as e:
                    print(e)
                    raise Exception("Failed")

    table = entire_page.find("table")

    if not table:
        logging.error("No table found! Nothing to do for {}".format(page_filename))
        NO_TABLE_PAGES.append(page_filename)
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
                    copy_from_src_to_dir(link_href)
                    img_tag = soup.new_tag("img", src=link_href)
                    img_div.append(img_tag)
                elif ".jpg" in link_href:
                    copy_from_src_to_dir(link_href)
                    img_tag = soup.new_tag("img", src=link_href)
                    img_div.append(img_tag)
                elif link_href == "memorial.html":
                    copy_from_src_to_dir("grampa.jpg")
                    copy_from_src_to_dir("flag.jpg")
                    memorial_html = get_html_soup("memorial.html")
                    memorial_table = memorial_html.find("table")
                    img_div.append(memorial_table)
                elif ".html" in link_href and link_href in BLACKLIST:
                    logging.warning("Found .html in blacklist: {}".format(link_href))
                    pass
                elif "http" in link_href or ".com" in link_href or "#" in link_href:
                    pass
                elif ".html" in link_href:
                    # Handle pages which are links to other misc pages on littlebass.com
                    link_soup = get_html_soup(link_href)
                    copy_all_images_found(link_soup)
                    img_div.append(link_soup)
                else:
                    PROBLEMATIC_LINKS.append(link_href)
        new_page_body.append(date_div)
    return new_page_body

if __name__ == "__main__":
    lblr()
