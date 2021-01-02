#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 20:39:49 2020

@author: anitjain
"""

import scrapy
import requests
import re
from urllib.parse import urlparse

"""
Class: PyClawler - Crawl websites (extract all reference links)
"""
class PyCrawler(object):
    def __init__(self, starting_url):
        self.starting_url = starting_url
        self.visited = set()
        self.orig_netloc = self.netloc_base(starting_url) 
        
    def get_html(self, url):
        try:
            html = requests.get(url)
        except Exception as e:
            print(e)
            return ""
        return html.content.decode('latin-1')
        
    def get_links_yld(self, url):
        html = self.get_html(url)
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        links = re.findall('''<a\s+(?:[^>]*?\s+)?href="([^"]*)"''', html)    
        
        for i, link in enumerate(links):
            print(f"LINK: {link}   NETLOC: {urlparse(link).netloc}")
            if not urlparse(link).netloc :
                link = base + link
                print(f"BASE+LINK: I={i} B/L={link}")
            
            if 'mailto' in link:
                continue
            
            yield link
            
    def netloc_base(self, url):
        s = re.findall("(?:.*\.)?([\w]+\.[\w]+)", urlparse(url).netloc)[0]
        print(f"PRINT-{s}")
        return s
            
        
        
    def get_links(self, url):
        html = self.get_html(url)
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        links = re.findall('''<a\s+(?:[^>]*?\s+)?href="([^"]*)"''', html)    
        
        for i, link in enumerate(links):
            #print(f"LINK2: {link}   NETLOC: {urlparse(link).netloc}")
            if not urlparse(link).netloc :
                link_with_base = base + link
                links[i] = link_with_base
                #print(f"BASE+LINK2: I={i} B/L={link_with_base}")
        
        return set(filter(lambda x: 'mailto' not in x,links))

    def extract_info(self, url):
        html = self.get_html(url)
        meta = re.findall("<meta .*?name=[\"'](.*?)['\"].*?content=[\"'](.*?)['\"].*?>", html)    
        return dict(meta)
    
    def crawl(self, url):
        for link in self.get_links(url):
            if link in self.visited:
                continue
            #print(link)
            self.visited.add(link)
            info = self.extract_info(link)
            print(f"""Link: {link}
Description: {info.get('description')}    
Keywords: {info.get('keywords')}    
            """) 
            if self.orig_netloc == self.netloc_base(link):
                print(f"Same Netloc {self.orig_netloc}")
                self.crawl(link)
            else:
                print(f"New Netloc {urlparse(link).netloc}")
        
    def start(self):
        self.crawl(self.starting_url)
    
    
class BrickSetSpider(scrapy.Spider):
    name = "bricket_spider"
    start_urls = ['http:/brickset.com/sets/year-2016']
    

if __name__ == "__main__":
    
    crawler = PyCrawler("https://people.com")
    crawler.start()
    