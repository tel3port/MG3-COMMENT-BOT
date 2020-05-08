from selenium import webdriver
from random import randint
import os
import numpy as np
import random
import traceback
import heroku3
import time
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
import globals as gls
import re
from collections import defaultdict
import requests
from urllib.request import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import asyncio
import aiohttp
import os
import uuid
colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET

total_urls_visited = 0


def open_everything():
    with open("dictionary/adjectives.txt") as adj_file:
        global adjectives
        adjectives = [line.strip() for line in adj_file]

    with open("dictionary/adverbs.txt") as adv_file:
        global adverbs
        adverbs = [line.strip() for line in adv_file]

    with open("dictionary/comment_list.txt") as comment_file:
        global comments
        comments = [line.strip() for line in comment_file]

    with open("dictionary/complements.txt") as complement_file:
        global complements
        complements = [line.strip() for line in complement_file]

    with open("dictionary/landers.txt") as lander_file:
        global landers
        landers = [line.strip() for line in lander_file]

    with open("dictionary/proverbs.txt") as prov_file:
        global proverbs
        proverbs = [line.strip() for line in prov_file]

    with open("dictionary/static_phrase_list.txt") as phrase_file:
        global STATIC_PHRASES
        STATIC_PHRASES = [line.strip() for line in phrase_file]

    with open("dictionary/article_synonyms.txt") as syn_file:
        global articles
        articles = [line.strip() for line in syn_file]

    with open("dictionary/rant_synonyms.txt") as rant_file:
        global rants
        rants = [line.strip() for line in rant_file]

    with open("dictionary/determiners_list.txt") as dets_file:
        global dets
        dets = [line.strip() for line in dets_file]

    with open("generated/emails.txt") as emails_file:
        global emails
        emails = [line.strip() for line in emails_file]

    with open("generated/names.txt") as names_file:
        global names
        names = [line.strip() for line in names_file]

    with open("dictionary/parsed_jokes.txt") as jokes_file:
        global jokes
        jokes = [line.strip() for line in jokes_file]

    with open("dictionary/profit_syn.txt") as prof_file:
        global prof
        prof = [line.strip() for line in prof_file]

    with open("dictionary/new_syn.txt") as new_file:
        global news
        news = [line.strip() for line in new_file]

    with open("dictionary/expound_syn.txt") as exp_file:
        global exp
        exp = [line.strip() for line in exp_file]

    with open("dictionary/film_syn.txt") as film_file:
        global film
        film = [line.strip() for line in film_file]


open_everything()

global parsed_links
parsed_links = []

# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()

wp_bot_name = "wp-mg3-comment-bot"


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


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
            with open("EXTRACTOR/extracted/FINAL_URL_LIST.txt", "a") as new_urls_file:
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
    for url in (open("EXTRACTOR/extracted/internal_links.txt").readlines()):
        t = loop.create_task(parse_tasks(url))
        tasks.append(t)

    await asyncio.wait(tasks)


def create_append_text_file(extd_links, my_uuid):
    if not os.path.exists(f'./EXTRACTOR/urls/static_url_list_{my_uuid}.txt'):
        with open(f'./EXTRACTOR/urls/static_url_list_{my_uuid}.txt', 'a') as final_urls_list_file:
            for single_lk in extd_links:
                print(single_lk.strip(), file=final_urls_list_file)


def soft_file_cleanup():
    open('EXTRACTOR/extracted/internal_links.txt', 'w').close()
    open('EXTRACTOR/extracted/external_links.txt', 'w').close()


def hard_file_cleanup():
    open('EXTRACTOR/extracted/internal_links.txt', 'w').close()
    open('EXTRACTOR/extracted/external_links.txt', 'w').close()
    open('EXTRACTOR/extracted/blog_link_file.txt', 'w').close()
    open('EXTRACTOR/extracted/FINAL_URL_LIST.txt', 'w').close()


def random_static_url_path():
    static_url_list_paths = os.listdir('./EXTRACTOR/urls')

    return f'EXTRACTOR/urls/{static_url_list_paths[randint(0, len(static_url_list_paths) - 1)]}'
    # return f'EXTRACTOR/urls/static_url_list_26f8faa8c60b4542aed6d89847441296.txt'


class CommentsBot:
    def __init__(self, bot_name, my_proxy):
        self.my_proxy = my_proxy
        self.bot_name = bot_name
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-dev-sgm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        my_proxy_address = self.my_proxy.get_address()
        webdriver.DesiredCapabilities.CHROME['proxy'] = {
            "httpProxy": my_proxy_address,
            "ftpProxy": my_proxy_address,
            "sslProxy": my_proxy_address,

            "proxyType": "MANUAL",

        }
        # self.driver = webdriver.Chrome(executable_path='./chromedriver', options=chrome_options)
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        print("my ip address", my_proxy_address)

    def restart_application(self):
        heroku_conn = heroku3.from_key('b477d2e0-d1ba-48b1-a2df-88d87db973e7')
        app = heroku_conn.apps()[self.bot_name]
        app.restart()

    def wp_post_getter(self):
        data = self.driver.page_source

        soup = BeautifulSoup(data, "html.parser")

        article = soup.find('div', class_="entry-content")

        return article.text

    def blog_extractor(self):
        with open("EXTRACTOR/extracted/search_terms.txt") as search_terms_file:
            search_terms = [line.strip() for line in search_terms_file]
            random_search_term = search_terms[randint(0, len(search_terms) - 2)]
            print(f"searching for blogs on: {random_search_term}")

        self.driver.get(f'https://en.wordpress.com/tag/{random_search_term}/')

        data = self.driver.page_source

        soup = BeautifulSoup(data, "html.parser")

        links_list = soup.find_all('a', class_="blog-url")

        for single_link in links_list:
            link = single_link['href']
            with open("EXTRACTOR/extracted/blog_link_file.txt", "a") as new_blogs_file:
                print(link.strip(), file=new_blogs_file)

    @staticmethod
    def response_generator():
        random_adj = adjectives[randint(0, len(adjectives) - 1)]
        random_adv = adverbs[randint(0, len(adverbs) - 1)]
        random_comm = comments[randint(0, len(comments) - 1)]
        random_comp = complements[randint(0, len(complements) - 1)]
        random_det = dets[randint(0, len(dets) - 1)]
        random_lander = landers[randint(0, len(landers) - 1)]
        random_prov = proverbs[randint(0, len(proverbs) - 1)]
        random_phrase = STATIC_PHRASES[randint(0, len(STATIC_PHRASES) - 1)]
        random_article_syn = articles[randint(0, len(articles) - 1)]
        random_joke = jokes[randint(0, len(jokes) - 1)]
        random_prof = prof[randint(0, len(prof) - 1)]
        random_new = news[randint(0, len(news) - 1)]
        random_exp = exp[randint(0, len(exp) - 1)]
        random_film = film[randint(0, len(film) - 1)]

        random_rant_syn = rants[randint(0, len(rants) - 1)]
        first_segment = f"{random_det} {random_article_syn} is {random_adv} {random_adj}!"
        # last_segment = f"My {random_new} {random_prof} {random_rant_syn.upper()} at my site {random_exp}"
        last_segment = f"we are making a {random_film} about this. Book for free here: https://youtu.be/s2jpbmvsmvs"
        tokenized_text = [
            word
            for word in re.split('\W+', extracted_post)
            if word != ''
        ]

        # Create graph.
        markov_graph = defaultdict(lambda: defaultdict(int))

        last_word = tokenized_text[0].lower()
        for word in tokenized_text[1:]:
            word = word.lower()
            markov_graph[last_word][word] += 1
            last_word = word

        # Preview graph.
        limit = 3
        for first_word in ('the', 'by', 'who'):
            next_words = list(markov_graph[first_word].keys())[:limit]
            # for next_word in next_words:
            #     print(first_word, next_word)

        def walk_graph(graph, distance=5, start_node=None):
            """Returns a list of words from a randomly weighted walk."""
            if distance <= 0:
                return []

            # If not given, pick a start node at random.
            if not start_node:
                start_node = random.choice(list(graph.keys()))

            weights = np.array(
                list(markov_graph[start_node].values()),
                dtype=np.float64)
            # Normalize word counts to sum to 1.
            weights /= weights.sum()

            # Pick a destination using weighted distribution.
            choices = list(markov_graph[start_node].keys())
            chosen_word = np.random.choice(choices, None, p=weights)

            return [chosen_word] + walk_graph(
                graph, distance=distance - 1,
                start_node=chosen_word)

        # generated_sentence = f"{' '.join(walk_graph(markov_graph, distance=35))}...  "
        generated_sentence = ""
        markov_comment = f'{first_segment.capitalize()} {generated_sentence.capitalize()}. {last_segment.capitalize()}'
        final_comment = f"{random_comm.capitalize()} {generated_sentence.capitalize()}. \n {last_segment.capitalize()} "
        final_complement = f" {random_comp.capitalize()}. {generated_sentence.capitalize()}. \n {last_segment.capitalize()}"
        final_prov = f"You know what they say: {random_prov.capitalize()}. {generated_sentence.capitalize()} {last_segment.capitalize()}"
        final_phrase = f"The author should know: {random_phrase.capitalize()}. {generated_sentence.capitalize()}\n {last_segment.capitalize()}"
        final_joke = f"This post makes me remember a bad joke: {random_joke.capitalize()}. {generated_sentence.capitalize()} {last_segment.capitalize()}"

        response_list = [markov_comment, final_comment, final_complement, final_prov, final_phrase, final_joke]

        return response_list[randint(0, len(response_list) - 1)]

    @staticmethod
    def random_email_getter():
        return emails[randint(0, len(emails) - 1)]

    @staticmethod
    def random_name_getter():
        return names[randint(0, len(names) - 1)]

    @staticmethod
    def random_lander_getter():
        return landers[randint(0, len(landers) - 1)]

    def jetpack_frame_finder(self):
        comment_frame_xpath = '//*[@id="jetpack_remote_comment"]'

        jetpack_frame = None
        try:
            jetpack_frame = self.driver.find_element_by_xpath(comment_frame_xpath)

        except Exception as e:
            print(e)

        return jetpack_frame

    def comment_submit_finder(self):
        submit_xpath = '//*[@id="comment-submit"]'

        xpath_element = None
        try:
            xpath_element = self.driver.find_element_by_xpath(submit_xpath)

        except Exception as e:
            print(e)

        return xpath_element

    def submit_finder(self):
        submit_xpath = '//*[@id="submit"]'

        xpath_element = None
        try:
            xpath_element = self.driver.find_element_by_xpath(submit_xpath)

        except Exception as e:
            print(e)

        return xpath_element

    def fl_comment_finder(self):
        submit_xpath = '//*[@id="fl-comment-form-submit"]'

        xpath_element = None
        try:
            xpath_element = self.driver.find_element_by_xpath(submit_xpath)

        except Exception as e:
            print(e)

        return xpath_element

    def comment(self, random_post_url, random_author, random_email, random_website):
        policy_xpath = '//*[@type="submit"]'
        comment_xpath = '//*[@id="comment"]'
        author_xpath = '//*[@id="author"]'
        email_xpath = '//*[@id="email"]'
        url_xpath = '//*[@id="url"]'
        print(f'POST BEING WORKED ON: {random_post_url}')

        random_num = randint(1, 100)
        author_name = ''

        if random_num % 2 == 0:
            author_name = random_author.capitalize()

        elif random_num % 3 == 0:
            author_name = random_author.upper()
        else:
            author_name = random_author

        try:

            self.driver.get(random_post_url)
            time.sleep(5)

            global extracted_post
            extracted_post = self.wp_post_getter()
            random_comment = self.response_generator()
            time.sleep(10)

            try:
                gls.sleep_time()
                policy_element = self.driver.find_element_by_class_name('accept')
                gls.sleep_time()
                policy_element.click()
            except Exception as e:
                print("policy click error ", str(e))

            try:
                gls.sleep_time()
                policy_element = self.driver.find_element_by_xpath(policy_xpath)
                gls.sleep_time()
                policy_element.click()
            except Exception as e:
                print("policy click error ", str(e))

            if self.jetpack_frame_finder() is not None:
                gls.sleep_time()
                self.driver.switch_to.frame('jetpack_remote_comment')
                gls.sleep_time()

            else:
                # scroll to element
                gls.sleep_time()
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView();", self.driver.find_element_by_xpath(url_xpath))
                    gls.sleep_time()
                except Exception as x:
                    print(x)

            self.driver.find_element_by_xpath(comment_xpath).send_keys(random_comment)
            gls.sleep_time()
            self.driver.find_element_by_xpath(author_xpath).send_keys(f'{author_name}')
            gls.sleep_time()
            self.driver.find_element_by_xpath(email_xpath).send_keys(random_email)

            # try:
            #     gls.sleep_time()
            #     self.driver.find_element_by_xpath(url_xpath).send_keys(random_website)
            #     gls.sleep_time()
            # except Exception as ex:
            #     print("url loader error: ", str(ex))

            self.driver.execute_script("window.scrollBy(0,150)", "")
            gls.sleep_time()

            submit_element_1 = self.comment_submit_finder()  # '//*[@id="comment-submit"]'
            submit_element_2 = self.submit_finder()  # '//*[@id="submit"]'
            submit_element_3 = self.fl_comment_finder()  # '//*[@id="fl-comment-form-submit"]'

            if submit_element_1 is not None:
                gls.sleep_time()
                submit_element_1.click()
                gls.sleep_time()
            elif submit_element_2 is not None:
                gls.sleep_time()
                submit_element_2.click()
                gls.sleep_time()
            elif submit_element_3 is not None:
                gls.sleep_time()
                submit_element_3.click()
                gls.sleep_time()

        except Exception as em:
            print(f'comment Error occurred with url: {random_post_url} ' + str(em))
            print(traceback.format_exc())

            if 'invalid session id' in str(em):
                self.clean_up()

        finally:
            print("comment() done")

    def clean_up(self):

        t = randint(500, 2000)
        print(f"clean up sleep for {t} seconds")
        time.sleep(t)

        self.driver.delete_all_cookies()
        self.restart_application()


if __name__ == "__main__":

    while 1:
        time.sleep(5)
        count = 0
        random_cycle_nums = randint(300, 700)

        req_proxy = RequestProxy()  # you may get different number of proxy when  you run this at each time
        proxies = req_proxy.get_proxy_list()  # this will create proxy list
        random_proxy = proxies[randint(0, len(proxies) - 1)]

        bot = CommentsBot(wp_bot_name, random_proxy)

        for _ in range(10):
            bot.blog_extractor()

        # ===============LOOPS THRU EACH BLOG AND EXTRACTS ALL INTERNAL AND EXTERNAL URLS========================

        try:
            with open(f"EXTRACTOR/extracted/blog_link_file.txt", "r") as blog_list_file:
                main_blog_list = [line.strip() for line in blog_list_file]
                blog_list_set = set(main_blog_list)

            for single_blog in blog_list_set:
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
                with open(f"EXTRACTOR/extracted/internal_links.txt", "a") as f:
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
                loop = asyncio.get_event_loop()
                loop.run_until_complete(main())

                soft_file_cleanup()

        except Exception as e:
            print(e)

        with open("EXTRACTOR/extracted/FINAL_URL_LIST.txt") as extracted_links_file:
            global extracted_links
            extracted_links = [line.strip() for line in extracted_links_file]

        create_append_text_file(extracted_links, uuid.uuid4().hex)

        hard_file_cleanup()

        with open(random_static_url_path(), "r") as internal_link_file:
            parsed_links = [line.strip() for line in internal_link_file]

            # to remove duplicates
            parsed_links_set = set()
            parsed_links_set.update(parsed_links)

        # makes a single comment for each link per each iteration
        # breaks the cycle after a given number of comments to force script tp get another ip address
        if len(parsed_links_set) > 0:
            for link in list(parsed_links_set):
                bot.comment(link, bot.random_name_getter(), bot.random_email_getter(), bot.random_lander_getter())
                gls.sleep_time()

                count += 1
                print(f"count number: {count}")
                if count == random_cycle_nums:
                    break

        bot.clean_up()




