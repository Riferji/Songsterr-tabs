# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 14:24:26 2019

@author: rfernandezjimenez
"""

#%%
# Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as chrome_Options  
from selenium.webdriver.firefox.options import Options as firefox_Options

import pandas as pd
import time
from tqdm import tqdm

import os  
import io
import glob
import subprocess

#%%
class Songsterr():
    # We have problems ussing the Firefox driver and the chrome driver, but the failures are disjoint,
    #     therefore, we combine both clients for this project, firefox and chrome
    def __init__(self):
        # Chrome stuff
        chrome_options = chrome_Options()  
        chrome_options.add_argument("--headless")  
        chrome_options.binary_location = '/Program Files (x86)/Google/Chrome/Application/chrome.exe'
        self.driver_chrome = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"), options=chrome_options)
        self.driver_chrome.set_window_size(1600, 800)
        
        # Firefox stuff
        firefox_options = firefox_Options()  
        firefox_options.headless = True
        firefox_options.binary_location = "/Program Files (x86)/Mozilla Firefox/firefox.exe"
        self.driver_firefox = webdriver.Firefox(executable_path=os.path.abspath("geckodriver"), options=firefox_options) 
        self.driver_firefox.set_window_size(1600, 800)
        
        # Check if the "Songs" folder exists
        if not os.path.exists('./Songs'):
            os.makedirs('./Songs')
        
    def close_drivers(self):
        self.driver_chrome.close()
        self.driver_firefox.close()
    
    def get_url(self, url):
        self.driver_chrome.get(url)
        self.driver_firefox.get(url)
        
    def accept_cookies(self, driver):
        try:
            cookie_button = driver.find_element_by_id('accept')
            cookie_button.click()
        except:
            print('Cookie button has been cliked')
    
    def create_folder(self, url):
        self.folder_name = os.path.basename(url)
        self.folder_path = './Songs/{}'.format(self.folder_name)
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)
        
    def add_song_to_list(self, url):
        list_path = './Songs/song_list.txt'
        if os.path.isfile(list_path):
            info_file = pd.DataFrame({'Song_url' : url,
                                      'Folder_name' : os.path.basename(url),
                                      'Author' : self.artist,
                                      'Title' : self.song_name}, index = [0])
            info_file.to_csv(list_path, sep = '\t', 
                             index = False, mode = 'a', header = False)   
        else:
            info_file = pd.DataFrame({'Song_url' : url,
                                      'Folder_name' : os.path.basename(url),
                                      'Author' : self.artist,
                                      'Title' : self.song_name}, index = [0])
            info_file.to_csv(list_path, sep = '\t', 
                             index = False, mode = 'a', header = True)
            
    def get_tabs(self, tabs_limit = 6):
        # Song info
        self.artist = self.driver_chrome.find_element_by_class_name('Cl2pm').text
        self.song_name = self.driver_chrome.find_element_by_tag_name('span').text
        
        tablature_list_chrome = self.driver_chrome.find_elements_by_class_name('C5p2ld')
        tablature_list_firefox = self.driver_firefox.find_elements_by_class_name('C5p2ld')
        
        # The problem is in the 3rd element
        tablature_list = tablature_list_chrome[:5] + tablature_list_firefox[5:]
        
        if tabs_limit<0:
            tabs_limit = len(tablature_list)
        
        print('Starting scrap process...')
        for i, tab in enumerate(tqdm(tablature_list[:tabs_limit])):
            if i <= 4: # Chrome images
                location = tab.location_once_scrolled_into_view
                self.driver_chrome.set_window_position(x = location['x'], y = location['y'])
            else: # Firefox images
                location = tab.location
                self.driver_firefox.set_window_position(x = location['x'], y = location['y'])
            
            time.sleep(1)
            screenshot_result = tab.screenshot('{}/tab_{}.png'.format(self.folder_path, i+1))
            
            if screenshot_result == False:
                print('Fatal error with the tablature {}'.format(i))
            
        print('Process finished')
            
    def process_url(self, url, tabs_limit = 6):
        self.get_url(url)
        self.accept_cookies(self.driver_chrome)
        self.accept_cookies(self.driver_firefox)
        self.create_folder(url)
        self.get_tabs(tabs_limit)
        self.add_song_to_list(url)
    
#%%
class Pdf_Compiler():
    def __init__(self):
        pass
    
    def init_parameters(self, title, author, folder_name):
        # Capitalize the first letter from each word
        self.title = title.title()
        self.author = author.title()
        self.image_path = os.path.join('./Songs/', folder_name)
        self.list_of_images = glob.glob(os.path.join(self.image_path, '*.png'))
    
    def create_latex_folder(self):
        self.latex_path = os.path.join(self.image_path, 'Latex')
        
        # If we haven't a latex folder, we build it
        if not os.path.isdir(self.latex_path):
            os.mkdir(self.latex_path)
        
    def generate_header(self):
        header_text = '''
        \\documentclass{article}
        
        \\usepackage{graphicx}
        \\usepackage{float}
        \\usepackage{geometry}
        \\geometry{
        	a4paper,
        	total={170mm,257mm},
        	left=5mm,
        	right=5mm,
        	top=10mm,
        }
        
        \\title{''' + self.title + '''}
        \\author{''' + self.author + '''}
        
        \\begin{document}
            \\maketitle
        '''
        
        return header_text
        
    def generate_image_code(self, ind):
        # This function generates the image code chunk for the latex
        
        figure_text = '''
        	\\vspace{-2cm}
        	\\begin{figure}[H]
        		\\begin{center}
        			\\includegraphics[width=1\\textwidth]{./../tab_'''+str(ind)+'''}
        			\\label{fig:tab_'''+str(ind)+'''}
        		\\end{center}
        	\\end{figure}
        '''
        
        return figure_text
    
    def generate_latex_code(self):
        self.body_text = self.generate_header()
        # We only use the image path list for know how many images we have, and after that, we define the names as tab_i
        for i in range(len(self.list_of_images)):
            # If our image is greater than 1 Kb, we add it to the partiture
            if os.path.getsize(os.path.join(self.image_path, 'tab_{}.png'.format(i+1))) >= 1024:
                self.body_text += self.generate_image_code(ind = i+1)
        
        self.body_text += '\n        	\\end{document}'
    
    def save_latex_code(self):
        # We create the "Latex" folder
        self.create_latex_folder()
        # We generate the latex code
        self.generate_latex_code()
        
        self.file_path = os.path.join(self.latex_path, '{}.tex'.format(self.title))
        with io.open(self.file_path, 'w', encoding='utf-8') as file:
            file.write(self.body_text)
            
        # We save the author and title info
        info_file = pd.DataFrame({'Author' : self.author,
                                  'Title' : self.title}, index = [0])
        info_file.to_csv(os.path.join(self.latex_path, 'song_info.txt'), sep = '\t', index = False)    
        
    def compile_code(self, title, author, folder_name):
        # We define our parameters
        self.init_parameters(title, author, folder_name)
        
        # Generate our code
        self.save_latex_code()
        
        # Compile the latex code
        # self.latex_path --> were is stored our latex code
        # Parameter explanation
        #     -quiet --> Only the errors are printed
        #     -output-directory= --> Were the output file is saved
        #     -aux-directory= --> Were the aux files are saved
        sentence = 'pdflatex "{tex_path}" -quiet -output-directory="{output_path}" -aux-directory="{aux_path}"'.format(tex_path = self.file_path, output_path = self.latex_path, aux_path = self.latex_path)
        subprocess.call(sentence, shell=True)
        
#%%

url_list = ['https://www.songsterr.com/a/wsa/led-zeppelin-stairway-to-heaven-tab-s27t1',
            'https://www.songsterr.com/a/wsa/metallica-master-of-puppets-tab-s455118t1',
            'https://www.songsterr.com/a/wsa/metallica-nothing-else-matters-tab-s439171t1',
            'https://www.songsterr.com/a/wsa/the-eagles-hotel-california-tab-s447t1',
            'https://www.songsterr.com/a/wsa/metallica-one-tab-s444t1',
            'https://www.songsterr.com/a/wsa/harry-murrel-skyrim-sons-of-skyrim-classical-guitar-tab-s91588t0']

Songsterr_scraper = Songsterr()
Song_Compiler = Pdf_Compiler()

for k, url in enumerate(url_list):
    print('Procesing url {}/{}'.format(k+1, len(url_list)))
    Songsterr_scraper.process_url(url = url, 
                                  tabs_limit = -1)
    time.sleep(1)
    Song_Compiler.compile_code(title = Songsterr_scraper.song_name, 
                               author = Songsterr_scraper.artist, 
                               folder_name = Songsterr_scraper.folder_name)

Songsterr_scraper.close_drivers()

#%%






