import os
import time
import random
import logging

from tabulate import tabulate
from playwright.sync_api import sync_playwright

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

HOME_URL = "https://linux.do/"

class LinuxDoBrowser:
    def __init__(self) -> None:
        self.pw = sync_playwright().start()
        self.browser = self.pw.firefox.launch(headless=True)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto(HOME_URL)

    def login(self):
        logging.info("Attempting to log in")
        self.page.click(".login-button .d-button-label")
        time.sleep(2)
        self.page.fill("#login-account-name", USERNAME)
        time.sleep(2)
        self.page.fill("#login-account-password", PASSWORD)
        time.sleep(2)
        self.page.click("#login-button")
        time.sleep(10)
        user_ele = self.page.query_selector("#current-user")
        if not user_ele:
            logging.error("Login failed")
            return False
        else:
            logging.info("Check in success")
            return True

    def click_topic(self):
        topics = self.page.query_selector_all("#list-area .title")
        logging.info(f"Found {len(topics)} topics on the page")
        for topic in topics:
            title = topic.inner_text()
            href = topic.get_attribute("href")
            logging.info(f"Clicking into topic: {title} (URL: {HOME_URL + href})")
            page = self.context.new_page()
            page.goto(HOME_URL + href)
            time.sleep(3)
            if random.random() < 0.02:  # 100 * 0.02 * 30 = 60
                self.click_like(page)
            time.sleep(3)
            page.close()

    def run(self):
        if not self.login():
            return
        self.click_topic()
        self.print_connect_info()

    def click_like(self, page):
        page.locator(".discourse-reactions-reaction-button").first.click()
        logging.info(f"Clicked like on topic: {page.title()}")

    def print_connect_info(self):
        logging.info("Fetching connect info")
        page = self.context.new_page()
        page.goto("https://connect.linux.do/")
        rows = page.query_selector_all("table tr")

        info = []

        for row in rows:
            cells = row.query_selector_all("td")
            if len(cells) >= 3:
                project = cells[0].text_content().strip()
                current = cells[1].text_content().strip()
                requirement = cells[2].text_content().strip()
                info.append([project, current, requirement])

        logging.info("--------------Connect Info-----------------")
        logging.info("\n" + tabulate(info, headers=["项目", "当前", "要求"], tablefmt="pretty"))

        page.close()

if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        logging.error("Please set USERNAME and PASSWORD")
        exit(1)
    l = LinuxDoBrowser()
    l.run()
