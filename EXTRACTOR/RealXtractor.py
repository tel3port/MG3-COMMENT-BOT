import requests
from urllib.request import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import asyncio
import aiohttp
import time
import os
from random import randint
from googlesearch import search
import uuid

colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET

total_urls_visited = 0


def random_tld():
    domains = ["co.uk", "com", "de", 'dz', 'al', 'cv', "hr", "ee", "fr", "mg"]

    return domains[randint(0, len(domains) - 1)]


def search_and_write(search_term, top_level, number, stat_point, stop_point, pause_time):
    final_results = set()
    try:
        query = f'site:wordpress.com {search_term}'
        for j in search(query, tld=top_level, num=number, start=stat_point, stop=stop_point, pause=pause_time):
            char_list = j.split('.com')
            result = f'{char_list[0]}.com'

            final_results.add(result)

            print(result)
    except Exception as e:
        print(e)
        print(str(e))
        if "too many requests" in str(e):
            return

    finally:
        # save the external links to a file
        with open(f"extracted/blog_link_file.txt", "a") as f:
            for link in final_results:
                print(f"writing: {link}")
                print(f"{link.strip()}", file=f)

        # saving all extracted urls to a master lis
        with open(f"/home/m/Documents/blog_master_list.txt", "a") as f:
            for link in final_results:
                print(f"{link.strip()}", file=f)


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def random_proxy_location():
    locations = \
        ['US-C',
         'Ranch',
         'Cub',
         'Snow',
         'Vice',
         'Empire',
         'Precedent',
         'Dogg',
         'Cobain',
         'Granville',
         'Vansterdam',
         'Seine',
         'Castle',
         'Canal',
         'Fjord',
         'Crumpets',
         'Custard',
         'Alphorn',
         'Victoria'

         ]
    return locations[randint(0, len(locations) - 1)]


def get_all_website_links(url):
    try:
        """
        Returns all URLs that is found on `url` in which it belongs to the same website
        """
        # all URLs of `url`
        urls = set()
        # domain name of the URL without the protocol
        domain_name = urlparse(url).netloc
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                # href empty tag
                continue
            # join the URL if it's relative (not absolute link)
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            # remove URL GET parameters, URL fragments, etc.
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if not is_valid(href):
                # not a valid URL
                continue
            if href in internal_urls:
                # already in the set
                continue
            if domain_name not in href:
                # external link
                if href not in external_urls:
                    print(f"{GRAY}[!] External link: {href}{RESET}")
                    external_urls.add(href)

                continue
            print(f"{GREEN}[*] Internal link: {href}{RESET}")
            urls.add(href)
            internal_urls.add(href)
    except Exception as e:
        print(e)
        return False

    return urls


def crawl(url, max_urls=130):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    links = get_all_website_links(url)
    for link in links:
        print(f"total_urls_visited:{total_urls_visited} -- max_urls:{max_urls}")
        if total_urls_visited > max_urls:
            break
        crawl(link, max_urls=max_urls)


# looks for urls with comment boxes accept name, email and website and no recapta
# def sieve(url):
#     soup = BeautifulSoup(requests.get(url).content, "html.parser")
#     comment_box = soup.find('div', class_='comments-area')
#     if comment_box is not None:
#         return True
#     return False


async def if_comment_box_exists(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                html_text = await resp.read()

        if "comment-form-field" in str(html_text) \
                or "comments-area" in str(html_text) \
                or "comment-form" in str(html_text) \
                or "jetpack_remote_comment" in str(html_text) \
                or "reply-title" in str(html_text) \
                or "captcha" not in str(html_text) \
                or "comment-respond" in str(html_text):
            with open("extracted/FINAL_URL_LIST.txt", "a") as new_urls_file:
                print(url.strip(), file=new_urls_file)
            return True
        else:
            pass
            # with open("extracted/x.txt", "a") as new_urls_file:
            #     print(url.strip(), file=new_urls_file)

    except Exception as e:
        print(e)
        return False


async def parse_tasks(url):
    await if_comment_box_exists(url)


def int_checker(url):
    char_list = url.split('/')
    last_element = char_list[len(char_list) - 2]

    if len(last_element) > 4:
        return False

    return True


async def main():
    tasks = []
    for url in (open("extracted/internal_links.txt").readlines()):
        t = loop.create_task(parse_tasks(url))
        tasks.append(t)

    await asyncio.wait(tasks)


def create_append_text_file(extd_links, my_uuid):
    if not os.path.exists(f'/home/m/PycharmProjects/MG3-COMMENT-BOT/EXTRACTOR/urls/static_url_list_{my_uuid}.txt'):
        with open(f'/home/m/PycharmProjects/MG3-COMMENT-BOT/EXTRACTOR/urls/static_url_list_{my_uuid}.txt', 'a') as final_urls_list_file:
            for single_lk in extd_links:
                print(single_lk.strip(), file=final_urls_list_file)


def windscribe_vpn_rotate():
    os.system(f"windscribe connect {random_proxy_location()}")


def soft_file_cleanup():
    open('extracted/internal_links.txt', 'w').close()
    open('extracted/external_links.txt', 'w').close()


def hard_file_cleanup():
    open('extracted/internal_links.txt', 'w').close()
    open('extracted/external_links.txt', 'w').close()
    open('extracted/blog_link_file.txt', 'w').close()
    open('extracted/FINAL_URL_LIST.txt', 'w').close()


def push_to_github():
    try:
        os.system('git add .')
        os.system('git commit -m "added more static urls"')
        os.system('git push https://tel3port:AjTdJsetif3Q5dn@github.com/tel3port/MG3-COMMENT-BOT.git --all')

        print("5 new files hopefully pushed to github")
    except Exception as ex:
        print(str(ex))


if __name__ == "__main__":
    count = 0
    while 1:
        try:

            with open("extracted/search_terms.txt") as search_terms_file:
                global search_terms
                search_terms = [line.strip() for line in search_terms_file]

                for _ in range(4):
                    # windscribe_vpn_rotate()
                    random_search_term = search_terms[randint(0, len(search_terms) - 2)]
                    print(f"searching for blogs on: {random_search_term}")

                    search_and_write(random_search_term, random_tld(), randint(5, 10), randint(5, 10), randint(20, 30), randint(25, 35))

                    time.sleep(randint(12, 30))

                print("DONE WITH THE BLOG EXTRACTION")

            # # ===============OPENS A LIST OF BLOGS ==================================================================

            with open(f"extracted/blog_link_file.txt", "r") as blog_list_file:
                main_blog_list = [line.strip() for line in blog_list_file]

            # ===============LOOPS THRU EACH BLOG AND EXTRACTS ALL INTERNAL AND EXTERNAL URLS========================
            for single_blog in main_blog_list:
                # initialize the set of links (unique links)
                internal_urls = set()
                external_urls = set()
                internal_urls.clear()
                external_urls.clear()

                # os.system(f"windscribe connect {random_proxy_location()}")

                print(f"WORKING ON: {single_blog}")
                try:
                    crawl(single_blog, max_urls=130)
                except Exception as e:
                    print(e)
                print("[+] Total Internal links:", len(internal_urls))
                print("[+] Total External links:", len(external_urls))
                print("[+] Total URLs:", len(external_urls) + len(internal_urls))

                # todo find out why do i need this urlparse
                # domain_name = urlparse(single_blog).netloc

                # save the internal links to a file ====> {domain_name}_internal_links.txt"
                with open(f"extracted/internal_links.txt", "a") as f:
                    for internal_link in internal_urls:
                        if not ('/tag/' in internal_link or "/categor" in internal_link
                                or "faq" in internal_link or "events" in internal_link
                                or "policy" in internal_link or "terms" in internal_link
                                or "photos" in internal_link or "author" in internal_link
                                or "label" in internal_link or "video" in internal_link
                                or "search" in internal_link or "png" in internal_link
                                or "pdf" in internal_link or "jpg" in internal_link
                                or "facebook" in internal_link or "twitter" in internal_link
                                or "nytimes" in internal_link or "wsj" in internal_link
                                or "reddit" in internal_link or "bbc" in internal_link
                                or "wikipedia" in internal_link or "guardian" in internal_link
                                or "flickr" in internal_link or "cnn" in internal_link
                                or "ttps://wordpre" in internal_link or "google" in internal_link
                                or "cookies" in internal_link or "instagram" in internal_link
                                or "youtube" in internal_link or "spotify" in internal_link
                                or "mail" in internal_link or "pinterest" in internal_link
                                or "tumblr" in internal_link or "label" in internal_link
                                or "dribble" in internal_link or "unsplash" in internal_link
                                or "automattic" in internal_link or "facebook" in internal_link
                                or "amazon" in internal_link or "amzn" in internal_link
                                or "doc" in internal_link or "amzn" in internal_link
                                or int_checker(internal_link)) or "jsp" in internal_link:
                            print(internal_link.strip(), file=f)
                        else:
                            pass
                #
                # with open(f"extracted/external_links.txt", "a") as f:
                #     for external_link in external_urls:
                #         if not ('/tag/' in external_link or "/categor" in external_link
                #                 or "faq" in external_link or "events" in external_link
                #                 or "policy" in external_link or "terms" in external_link
                #                 or "photos" in external_link or "author" in external_link
                #                 or "label" in external_link or "video" in external_link
                #                 or "search" in external_link or "png" in external_link
                #                 or "pdf" in external_link or "jpg" in external_link
                #                 or "facebook" in external_link or "twitter" in external_link
                #                 or "nytimes" in external_link or "wsj" in external_link
                #                 or "reddit" in external_link or "bbc" in external_link
                #                 or "wikipedia" in external_link or "guardian" in external_link
                #                 or "flickr" in external_link or "cnn" in external_link
                #                 or "ttps://wordpre" in external_link or "google" in external_link
                #                 or "cookies" in external_link or "instagram" in external_link
                #                 or "youtube" in external_link or "mail" in external_link
                #                 or "automattic" in external_link or "facebook" in external_link
                #                 or int_checker(external_link)) or "jsp" in external_link:
                #             print(external_link.strip(), file=f)
                #         else:
                #             pass

                # # ===============PARSES THRU URLS AND SAVES THOSE THAT MOST LIKELY HAVE A COMMENT BOX ==============

                # saves those that have comment boxes into  FINAL_URL_LIST
                try:
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(main())
                except Exception as e:
                    print(e)

                soft_file_cleanup()

            # ===============COPIES ALL EXTRACTED FINAL URLS TO THE OTHER SCRIPT AND CLEARS UP ASSOCIATED FILES ================

            with open("extracted/FINAL_URL_LIST.txt") as extracted_links_file:
                global extracted_links
                extracted_links = [line.strip() for line in extracted_links_file]

            create_append_text_file(extracted_links, uuid.uuid4().hex)

            hard_file_cleanup()

            count += 1
            if count == 5:
                push_to_github()
        except Exception as exx:
            print(str(exx))


print("END OF THE LINE")
