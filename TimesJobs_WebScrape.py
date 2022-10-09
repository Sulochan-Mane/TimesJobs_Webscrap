from bs4 import BeautifulSoup
import lxml
import requests
import pandas as pd
import numpy as np

#generates a link for required pages takes input as int
link_generate = lambda x : requests.get('https://www.timesjobs.com/candidate/job-search.html?from=submit&actualTxtKeywords=data%20analyst&searchBy=0&rdoOperator=OR&searchType=personalizedSearch&luceneResultSize=25&postWeek=60&txtKeywords=0DQT0data%20analyst0DQT0&pDate=I&sequence='+str(x)+'&startPage=1').text

#converts and sparses the link given as input
soup_maker = lambda link : BeautifulSoup(link, 'lxml') 

#creates list for all the links
links = list(map(link_generate, range(1, 11)))

#creates list of webpage fetched by the list of link 
soups = list(map(soup_maker, links))

# white box is the block in website where all the info regarding a job opening is present 

white_boxes = []

for soup in soups:
    
    white_boxes.append(soup.find_all('li', class_ = "clearfix job-bx wht-shd-bx"))  
    
# the white boxes extracted are in nested lists for each page, Converting it to single list

white_box_1D = []

for white_box in white_boxes:
    
    for i in white_box:
        
        white_box_1D.append(i)
        
# Grouping the white boxes with different inputs given 

# normal : collection of the white boxes where the Salary is not given
# salaried: Collection of the white boxes where Salary is provided
# extra : collection of white boxes where there is additional data is provided other than first two lists

normal = []

salaried = []

extra = []

index = 0

for i in white_box_1D:
    
    if len(i.find_all('li')) ==4:       
        normal.append((index, i))
        
    elif len(i.find_all('li')) ==5:       
        salaried.append((index, i))
        
    elif len(i.find_all('li')) ==6:       
        extra.append((index, i))
    
    index+=1


# extract job titles
# job titles come under the first h2 in each white box

job_titles = []

for white_box in white_box_1D:     
        job_titles.append(white_box.find('h2').text.replace('\n', "").replace('\r', "").replace('\t', "").strip())
              
job_titles = list(enumerate(job_titles))

# extract company names
# company names are under the first h3 in each white box

comp_names = []

for white_box in white_box_1D:     
        comp_names.append(white_box.find('h3'))

comp_names_cleaned = []       
        
for i in comp_names:   
    comp_names_cleaned.append(i.text.replace('\n', "").replace('\r', "").replace('\t', "").strip())
    
comp_names_cleaned = list(enumerate(comp_names_cleaned))

# for NORMAL white boxes, 0th is experience 1st is location, 2nd is JD, 3rd is Keyskills
# for SALARIED white boxes, 0th is experience 1st is salary, 2nd is Location, 3rd is JD, 4 is keyskills

exp = []
salary = []
location = []
JD = []
skills = []

# extract all the work experience

for i in normal:   
    exp.append((i[0], i[1].find_all('li')[0].text.replace('card_travel', "")))
    
for i in salaried:  
    exp.append((i[0], i[1].find_all('li')[0].text.replace('card_travel', "")))
    
# extract all the available salaries

for i in normal:   
    salary.append((i[0], ""))
    
for i in salaried:    
    salary.append((i[0], i[1].find_all('li')[1].text))

# To extract all the skillset and Job Description, need to access individual hyperlinks and scrape data from there

job_links=[]
index = 0

for i in white_box_1D:   
    link = requests.get(i.find('a', href = True)['href']).text    
    job_links.append(BeautifulSoup(link, "lxml"))


# Extract all the skillsets from the links in the form of list
    
skillset = []
index = 0

for link in job_links:
    skillset.append((index, list(map(lambda x:x.text.replace('\n', "").replace('\r', "").replace('\t', "").strip(), link.find_all(class_ = 'jd-skill-tag')))))    
    index +=1

# Extract all the Job description text    
    
Job_Description = []
index = 0

for link in job_links:
    Job_Description.append((index, link.find(class_ = 'jd-desc job-description-main').text))    
    index +=1

# extrct all the locations

for i in normal:   
    location.append((i[0], i[1].find_all('li')[1].text.replace('\n', "").replace('\r', "").replace('\t', "").replace('location_on', "").strip()))

for i in salaried:
    location.append((i[0], i[1].find_all('li')[2].text.replace('\n', "").replace('\r', "").replace('\t', "").replace('location_on', "").strip()))


# Converting each list into a Dataframe     
    
job_titles = pd.DataFrame(list(map(lambda x:x[1], job_titles)), index = list(map(lambda x:x[0], job_titles)), columns = ["Job Title"])

company_name = pd.DataFrame(list(map(lambda x:x[1], comp_names_cleaned)), index = list(map(lambda x:x[0], comp_names_cleaned)), columns = ["Company"])

experience = pd.DataFrame(list(map(lambda x:x[1], exp)), index = list(map(lambda x:x[0], exp)), columns = ["Experience"])

salary = pd.DataFrame(list(map(lambda x:x[1], salary)), index = list(map(lambda x:x[0], salary)), columns = ["Salary"])

location = pd.DataFrame(list(map(lambda x:x[1], location)), index = list(map(lambda x:x[0], location)), columns = ["Location"])

skills = pd.DataFrame(list(map(lambda x:str(x[1]), skillset)), index = list(map(lambda x:x[0], skillset)), columns = ["skills"])

job_description = pd.DataFrame(list(map(lambda x:x[1], Job_Description)), index = list(map(lambda x:x[0], Job_Description)), columns = ["Job Description"])

# Joining all the individual Dataframes on Index

webscrap = job_titles.join(company_name.join(experience.join(salary.join(location.join(skills.join(job_description))))))

print(webscrap)