# -*- coding: utf-8 -*-
"""
Created on Thu Mar 9 2023

@author: Leonardo Filipe
(Modified original code from: OHyic)

"""
# import selenium drivers
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# import helper libraries
import time
import urllib.request
from urllib.parse import urlparse
import os
import requests
import io
from PIL import Image
import pandas as pd

# custom patch libraries
import patch


class GoogleVideoScraper():

    def __init__(self, webdriver_path, video_path, search_key="cat", number_of_videos=1, headless=True,
                 min_resolution=(0, 0), max_resolution=(1920, 1080), max_missed=10):
        # check parameter types
        video_path = os.path.join(video_path, search_key)
        if (type(number_of_videos) != int):
            print("[Error] Number of videos must be integer value.")
            return
        if not os.path.exists(video_path):
            print("[INFO] Video path not found. Creating a new folder.")
            os.makedirs(video_path)
        # check if chromedriver is updated
        while (True):
            try:
                # try going to www.google.com
                options = Options()
                if (headless):
                    options.add_argument('--headless')
                driver = webdriver.Chrome(webdriver_path, chrome_options=options)
                driver.set_window_size(1400, 1050)
                driver.get("https://www.google.com")
                if driver.find_elements_by_id("L2AGLb"):
                    driver.find_element_by_id("L2AGLb").click()
                break
            except:
                # patch chromedriver if not available or outdated
                try:
                    driver
                except NameError:
                    is_patched = patch.download_lastest_chromedriver()
                else:
                    is_patched = patch.download_lastest_chromedriver(driver.capabilities['version'])
                if (not is_patched):
                    exit(
                        "[ERR] Please update the chromedriver.exe in the webdriver folder according to your chrome version:https://chromedriver.chromium.org/downloads")

        self.driver = driver
        self.search_key = search_key
        self.number_of_videos = number_of_videos
        self.webdriver_path = webdriver_path
        self.video_path = video_path
        self.url = f"https://www.google.com/search?q={search_key}&rlz=1C1CHBF_pt-PTPT1040PT1040&biw=1536&bih=745&tbm=vid&sxsrf=AJOqlzXIpDCxZ0ibB6krx9TiQ5bANgpteA%3A1676308478868&ei=_m_qY7LLNKybkdUPiZWiiA0&oq=sardina+&gs_lcp=Cg1nd3Mtd2l6LXZpZGVvEAMYADIECCMQJzIHCAAQgAQQCjIHCAAQgAQQCjIHCAAQgAQQCjIHCAAQgAQQCjIHCAAQgAQQCjIHCAAQgAQQCjIHCAAQgAQQCjIHCAAQgAQQCjIHCAAQgAQQCjoICAAQgAQQywE6BggAEBYQHjoJCAAQFhAeEPEEOgcIIxDqAhAnOgQIABBDOggIABCxAxCDAToFCAAQgAQ6CwgAEIAEELEDEIMBOggIABCABBCxA1AtWPAVYOkcaAFwAHgDgAGAAYgBuxOSAQQ0LjE5mAEAoAEBsAEKwAEB&sclient=gws-wiz-video"
        self.headless = headless
        self.min_resolution = min_resolution
        self.max_resolution = max_resolution
        self.max_missed = max_missed

    def find_video_urls(self):
        """
            This function search and return a list of video urls based on the search key.
            Example:
                google_video_scraper = GoogleVideoScraper("webdriver_path","video_path","search_key",number_of_photos)
                video_urls = google_video_scraper.find_video_urls()

        """
        print("[INFO] Gathering video links")
        video_urls = []
        count = 0
        missed_count = 0
        self.driver.get(self.url)
        time.sleep(3)
        indx = 1
        while self.number_of_videos > count:
            try:
                if indx == 1:
                    # find and store src url
                    vidurl = self.driver.find_element_by_xpath(
                        '//*[@id="search"]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/video-voyager/div[1]/div[2]/a[1]/div[1]/div[2]/div[1]/div[1]/video')
                    src_link = vidurl.get_attribute("src")
                    print(
                        f"[INFO] {self.search_key} \t #{count} \t {src_link}")
                    video_urls.append(src_link)
                    count += 1
                    missed_count = 0

                else:
                    # find and store src url
                    vidurl = self.driver.find_element_by_xpath(
                        f'//*[@id="search"]/div[1]/div[1]/div[{str(indx)}]/div[1]/div[1]/div[1]/video-voyager/div[1]/div[1]/div[2]/a[1]/div[1]/div[2]/div[1]/div[1]/video')
                    src_link = vidurl.get_attribute("src")
                    print(
                        f"[INFO] {self.search_key} \t #{count} \t {src_link}")
                    video_urls.append(src_link)
                    count += 1
                    missed_count = 0


            except Exception:
                missed_count = missed_count + 1
                if (missed_count > self.max_missed):
                    print("[INFO] Maximum missed photos reached, exiting...")
                    break

            try:
                # scroll page to load next video
                if (count % 3 == 0):
                    self.driver.execute_script("window.scrollTo(0, " + str(indx * 60) + ");")
                element = self.driver.find_element_by_class_name("mye4qd")
                element.click()
                print("[INFO] Loading next page")
                time.sleep(3)
            except Exception:
                time.sleep(1)
            indx += 1

        self.driver.quit()
        print("[INFO] Google search ended")
        return video_urls

    def save_videos(self, video_urls, keep_filenames, keep_urls):
        print(keep_filenames)
        # save videos into file directory
        """
            This function takes in an array of video urls and save it into the given video path/directory.
            Example:
                google_video_scraper = GoogleVideoScraper("webdriver_path","video_path","search_key",number_of_photos)
                video_urls=["https://example_1.jpg","https://example_2.jpg"]
                google_video_scraper.save_videos(video_urls)

        """
        print("[INFO] Saving video, please wait...")
        for indx, video_url in enumerate(video_urls):
            try:
                print("[INFO] Video url:%s" % (video_url))
                search_string = ''.join(e for e in self.search_key if e.isalnum())
                video = requests.get(video_url, timeout=5)
                if video.status_code == 200:
                    with Image.open(io.BytesIO(video.content)) as video_from_web:
                        try:
                            if keep_filenames:
                                # extact filename without extension from URL
                                o = urlparse(video_url)
                                video_url = o.scheme + "://" + o.netloc + o.path
                                name = os.path.splitext(os.path.basename(video_url))[0]
                                # join filename and extension
                                filename = "%s.%s" % (name, video_from_web.format.lower())
                            else:
                                filename = "%s%s.%s" % (search_string, str(indx), video_from_web.format.lower())

                            video_path = os.path.join(self.video_path, filename)
                            print(
                                f"[INFO] {self.search_key} \t {indx} \t Image saved at: {video_path}")
                            video_from_web.save(video_path)
                        except OSError:
                            rgb_im = video_from_web.convert('RGB')
                            rgb_im.save(video_path)
                        video_resolution = video_from_web.size
                        if video_resolution != None:
                            if video_resolution[0] < self.min_resolution[0] or video_resolution[1] < \
                                    self.min_resolution[1] or video_resolution[0] > self.max_resolution[0] or \
                                    video_resolution[1] > self.max_resolution[1]:
                                video_from_web.close()
                                os.remove(video_path)

                        video_from_web.close()
            except Exception as e:
                print("[ERROR] Download failed: ", e)
                pass
        print("--------------------------------------------------")
        print(
            "[INFO] Downloads completed. Please note that some photos were not downloaded as they were not in the correct format (e.g. jpg, jpeg, png)")

        print("--------------------------------------------------")
        print(f'Keep urls?: {keep_urls}')

        if keep_urls:
            print("[INFO] Storing video URLS in csv file. Using same directory used to store the videos.")

            urls_df = pd.DataFrame(video_urls)

            search_string = ''.join(e for e in self.search_key if e.isalnum())
            filename = "%s.csv" % search_string
            csv_path = os.path.join(self.video_path, filename)

            urls_df.to_csv(csv_path)

        print('[INFO] URLS stored.')