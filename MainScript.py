from selenium import webdriver
from random import randint
import os
import traceback
import heroku3
import time
import requests
from urllib.request import urlparse, urljoin
import colorama
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
import globals as gls


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


open_everything()

global parsed_links
parsed_links = []
colorama.init()
GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET

# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()

total_urls_visited = 0

wp_bot_name = "wp-mg3-comment-bot"


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

        random_rant_syn = rants[randint(0, len(rants) - 1)]
        first_segment = f"{random_det} {random_article_syn} is {random_adv} {random_adj}!"
        last_segment = f"My latest PROFITABLE project at: {random_lander}"

        final_comment = f"{random_comm} "
        final_complement = f" {random_comp} \n {last_segment}"
        final_prov = f" {random_prov}. \n {last_segment}"
        final_phrase = f" {random_phrase}. \n {last_segment}"

        final_joke = f" {random_joke}. \n {last_segment}"

        response_list = [final_comment, final_complement, final_prov, final_phrase, final_joke]

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

    def comment(self, random_post_url, random_comment, random_author, random_email, random_website):
        comment_xpath = '//*[@id="comment"]'
        author_xpath = '//*[@id="author"]'
        email_xpath = '//*[@id="email"]'
        url_xpath = '//*[@id="url"]'
        submit_xpath = '//*[contains(@id,"submit")]'
        try:

            self.driver.get(random_post_url)
            time.sleep(5)

            # Scroll down to bottom
            # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # scroll to element
            self.driver.execute_script("arguments[0].scrollIntoView();", self.driver.find_element_by_xpath(url_xpath))
            gls.sleep_time()

            self.driver.find_element_by_xpath(comment_xpath).send_keys(random_comment)
            gls.sleep_time()
            self.driver.find_element_by_xpath(author_xpath).send_keys(random_author)
            gls.sleep_time()
            self.driver.find_element_by_xpath(email_xpath).send_keys(random_email)
            gls.sleep_time()
            self.driver.find_element_by_xpath(url_xpath).send_keys(random_website)
            gls.sleep_time()
            self.driver.execute_script("window.scrollBy(0,100)", "")
            gls.sleep_time()
            submit_element = self.driver.find_element_by_xpath(submit_xpath)
            gls.sleep_time()
            submit_element.click()
            gls.sleep_time()

        except Exception as em:
            print(f'comment Error occurred with url: {random_post_url}' + str(em))
            print(traceback.format_exc())

        finally:
            print("comment() done")

    def clean_up(self):

        time.sleep(randint(500, 2000))

        self.restart_application()


if __name__ == "__main__":
    count = 0
    while 1:

        with open(f"generated/static_url_list.txt", "r") as internal_link_file:
            parsed_links = [line.strip() for line in internal_link_file]

            # to remove duplicates
            parsed_links_set = set()
            parsed_links_set.update(parsed_links)

        req_proxy = RequestProxy()  # you may get different number of proxy when  you run this at each time
        proxies = req_proxy.get_proxy_list()  # this will create proxy list
        random_proxy = proxies[randint(0, len(proxies) - 1)]

        bot = CommentsBot(wp_bot_name, random_proxy)

        # makes a single comment for each link per each iteration
        # breaks the cycle after a given number of comments to force script tp get another ip address
        if len(parsed_links_set) > 0:
            for link in list(parsed_links_set):
                bot.comment(link, bot.response_generator(), bot.random_name_getter(), bot.random_email_getter(),bot.random_lander_getter())
                gls.sleep_time()

                count += 1
                if count == randint(10, 25):
                    break

        bot.clean_up()
        break
    print("done and dusted for this iteration!")

