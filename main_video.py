# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 11:02:06 2020

@author: OHyic

"""
#Import libraries
import os
import concurrent.futures
from GoogleVideoScraper import GoogleVideoScraper
from patch import webdriver_executable


def worker_thread(search_key):
    video_scraper = GoogleVideoScraper(
        webdriver_path, video_path, search_key, number_of_videos, headless, min_resolution, max_resolution)
    video_urls = video_scraper.find_video_urls()
    # video_scraper.save_videos(video_urls, keep_filenames, keep_urls)

    #Release resources
    del video_scraper

if __name__ == "__main__":
    #Define file path
    webdriver_path = os.path.normpath(os.path.join(os.getcwd(), 'webdriver', webdriver_executable()))
    video_path = os.path.normpath(os.path.join(os.getcwd(), 'photos'))

    #Add new search key into array ["cat","t-shirt","apple","orange","pear","fish"]
    # search_keys = list(set(["Alosa alosa", "Dicologlossa cuneata", "Merluccius merluccius",
    #                         "Mullus surmeletus", "Pedusa lascaris", "Prionace glauca",
    #                         "Raja clavata", "Sardina pilchardus", "Solea senegalensis",
    #                         "Solea solea", "Spondyliosoma cantharus", "Zeus faber"]))

    search_keys = list(set(["Alosa alosa"]))

    #Parameters
    number_of_videos = 1                # Desired number of videos
    headless = True                     # True = No Chrome GUI
    min_resolution = (0, 0)             # Minimum desired video resolution
    max_resolution = (9999, 9999)       # Maximum desired video resolution
    max_missed = 1000                   # Max number of failed videos before exit
    number_of_workers = 1               # Number of "workers" used
    keep_filenames = False              # Keep original URL video filenames
    keep_urls = True

    #Run each search_key in a separate thread
    #Automatically waits for all threads to finish
    #Removes duplicate strings from search_keys
    with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_workers) as executor:
        executor.map(worker_thread, search_keys)
#%%
