from selenium import webdriver 
from selenium.webdriver.common.by import By
import random
from time import sleep
import json
from datetime import datetime
import pandas as pd
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup


class Scrapper(object):

    def __init__(self):
        #Open firefox webdriver
        #options = Options()
        #options.headless = True
        #self.driver = webdriver.Firefox(options=options)
        self.driver = webdriver.Firefox()
        self.driver.maximize_window()
        sleep(random.randint(1,6))

    def return_driver(self):
        #For debug the driver
        return self.driver

    def back(self):
        #Return one page from driver (back)
        self.driver.back()
        sleep(2)
        return

    def access_profile(self,profile):
        #Access profile
        self.profile = profile
        self.driver.get(profile)
        sleep(3)
        return
        
    def scroll_page(self):
        #Scroll the page on range (500, 2000) pixels
        finalScroll = random.randint(500,2000)
        self.driver.execute_script(f"window.scrollTo(0,{finalScroll})")
        sleep(random.randint(3,6))
        return
    
    def get_page(self):
        #return the page source (HTML)
        return self.driver.page_source




class Extractor(object):
    
    def __init__(self, page_source):
        self.soup = BeautifulSoup(page_source, "html.parser")

    def extract_main_info(self):
        try:
            name = self.soup.find('h1', 'top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0')
            name = " ".join(name.text.split())
        except:
            name = ""
        try:
            activity = self.soup.find('h2','top-card-layout__headline break-words font-sans text-md leading-open text-color-text')
            activity = " ".join(activity.text.split())
        except:
            activity = ""
        try:
            region = self.soup.find('h3', 'top-card-layout__first-subline font-sans text-md leading-open text-color-text-low-emphasis')
            if len(region.text.split(',')) == 3:
                cidade = " ".join(region.text.split()).split(',')[0]
                estado = " ".join(region.text.split()).split(',')[1]
                pais = " ".join(region.text.split()).split(',')[2]
            elif len(region.text.split(',')) == 2:
                cidade = ""
                estado =  " ".join(region.text.split()).split(',')[0]
                pais =  " ".join(region.text.split()).split(',')[1]
            else:
                cidade = ""
                estado = ""
                pais = ""
        except:
            cidade = ""
            estado = ""
            pais = ""
        d = {
            'name':name,
            'activity_linkedin':activity,
            'city':cidade,
            'state':estado,
            'pais':pais
        }
        return d

    def extract_about_me(self):
        try:
            aboutme = self.soup.find('div', "core-section-container__content break-words")
            aboutme = " ".join(aboutme.text.split())
        except:
            aboutme = ""
        d = {
            'about_me':aboutme
        }
        return d
    
    def extract_experience(self):
        exp = self.soup.find('section',"core-section-container my-3 core-section-container--with-border border-b-1 border-solid border-color-border-faint m-0 py-3 pp-section experience")
        exp = exp.findAll(['h3','h4','span'], {"class":["profile-section-card__title","profile-section-card__subtitle","date-range"]})

        bag = []
        n = 0
        d = {}
        for i in exp:
            b = " ".join(i.text.split())

            if i.name == "h3":
                d['title'] = b
            elif i.name == "h4":
                d['local'] = b
            #elif exp[i].name == 'div':
                #dis = b
            elif i.name == 'span':
                d['data'] = b
            n += 1
            if n % 3 == 0:
                bag.append(d)
                d = {}
        experience = {
            'experience':bag
        }

        return experience
                
    def extract_academics(self):
        academics = self.soup.find('section', "core-section-container my-3 core-section-container--with-border border-b-1 border-solid border-color-border-faint m-0 py-3 pp-section education")
        academics = academics.findAll(['h3','h4','p'],{"class":["profile-section-card__title","profile-section-card__subtitle","education__item education__item--duration"]})
        d = {}
        bag = []
        n = 1
        for i in academics:
            academic = " ".join(i.text.split())
            if i.name == "h3":
                d['title'] = academic
            elif i.name == "h4":
                d['course'] = academic 
            elif i.name == "p":
                d['date'] = academic
            n += 1
            if n % 3 == 0:
                bag.append(d)
                d = {}
        acad = {
            'academic':bag
        }
        return acad
    


def load_data(path):
    profile_list = pd.read_csv(path)
    profile_list = profile_list[profile_list['link'].str.strip().astype(bool)]
    profile_list = profile_list.dropna()
    return profile_list

linkedin = Scrapper()
driver = linkedin.return_driver()
#Load dataframe with profile links
profile_list = load_data('data.csv')
for i in profile_list['link']:
    #Switch to new tab
    start_time = datetime.now()
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])

    

    #Complete link as https:www.linkedin.com/in/name (comment this line if you have just the profile name)
    profile = i.split('/')[2]
    print(f"Perfil de: {profile}")
    #Access the page without login
    #linkedin.access_profile(f"https://www.linkedin.com/in/{profile}/?trk=public_profile_browsemap")
    linkedin.access_profile(f"https://br.linkedin.com/in/{profile}/?trk=people-guest_people_search-card&original_referer=")
    sleep(3)
    linkedin.access_profile(f"https://br.linkedin.com/in/{profile}/?trk=people-guest_people_search-card&original_referer=")
    linkedin.scroll_page()


    main = Extractor(linkedin.get_page())

    #Close the tab and return to main tab
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    #Construct JSON response
    main_info = main.extract_main_info()
    aboutme = main.extract_about_me()
    experience = main.extract_experience()
    academics = main.extract_academics()

    main_info.update(aboutme)
    main_info.update(experience)
    main_info.update(academics)
    #Save JSON response
    with open(f"{profile}.json", "w") as outfile:
        json.dump(main_info, outfile, ensure_ascii=False)

    end_time = datetime.now()
    print("Duração: {}".format(end_time - start_time))
    print(60*"*")