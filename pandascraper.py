# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 12:45:08 2022

@author: joshu
"""


import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from selenium.webdriver.common.by import By
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
import re
import csv


def clearSurvey(driver):
    #sometimes there is a survey that pops up, this dismisses that 
    try:
        noThanks = driver.find_element(By.XPATH, '//button[@class="_hj-wTnOw__SurveyInvitation__noThanksButton _hj-3OscV__styles__clearButton"]')
        noThanks.click()
    except:
        pass
    try:
        downArrow = driver.find_element(By.XPATH, '//button[@class="_hj-OO1S1__styles__openStateToggle"]')
        downArrow.click()
    except:
        pass
    
    
    
def csvConverter():
    Excels = os.path.join(os.path.dirname(__file__), "Excels")  #put excel files to be processed in a folder named Excels in the same directory as where this program is
    csvFolder = os.path.join(os.path.dirname(__file__), "csv")  #saves the csvs in a folder in same directory as program 
    excelList = []
    for entry in os.scandir(Excels):
        excelList.append(entry.path)
        #print(fileList)
    for excel in excelList:
        entry = str(excel)
        entry = entry.split(' ')
        entry = entry[-1].split('.')
        name = entry[0]
        print(name)
        read_file = pd.read_excel(excel)
        read_file.to_csv (f'{csvFolder}\{name}.csv', index = None, header=True)


def tryloc(df, col, idx, default=None):
  try:
    return df.iloc[col, idx]
  except IndexError:
    return default
        
        
def logData(i, currentDoctor, df):
    currentNPI = df.iloc[i, 0]
    nextNPI = df.iloc[i+1, 0]
    df.iat[i, 5] = currentDoctor.clinicAddress
    df.iat[i, 6] = currentDoctor.clinicName
    df.iat[i, 7] = currentDoctor.clinicPhone
    print("logged data here: ")
    print(currentDoctor.clinicAddress)
    print(currentDoctor.clinicName)
    print(currentDoctor.clinicPhone)
    if currentDoctor.NPI == nextNPI:
        i = checkDupes(currentDoctor, df, i)
    if driver.current_window_handle != driver.window_handles[0]:
        driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(1)
    homeButton = driver.find_element(By.XPATH, '//a[@class="hgGlobalHeader__Logo"]')
    homeButton.click()
    print("active window at end of logData: " + driver.title)
    return i
        
    
def checkDupes(currentDoctor, df, i):
    print(f"i in checkdupes: {i}")
    now = datetime.now().time()
    print(now)
    nextNPI = df.iloc[i+1, 0]
    
    print(nextNPI)
    print(currentDoctor.NPI)
    address = currentDoctor.clinicAddress
    name = currentDoctor.clinicName
    phone = currentDoctor.clinicPhone
    while nextNPI == currentDoctor.NPI:
        print("writing dupe data")
        print(nextNPI)
        print(currentDoctor.NPI)
        print("in check dupes while loop, i: " + str(i))
        df.iat[i, 5] = address
        df.iat[i, 6] = name
        df.iat[i, 7] = phone
        df.iat[i+1, 5] = address
        df.iat[i+1, 6] = name
        df.iat[i+1, 7] = phone
        i += 1
        nextNPI = df.iloc[i+1, 0]
        if nextNPI != currentDoctor.NPI:
            return i
        
    else:
        print("not a dupe")
        i += 1
        return i

            


def getData(driver, currentDoctor):
    #this will gather the data from the details page 
    clinicName = ''
    clinicAddress = ''
    clinicPhone = ''
    try:
        cookiesPopup = driver.find_element(By.XPATH, '//button[@class="onetrust-close-btn-handler banner-close-button ot-close-icon"]')
        cookiesPopup.click()
    except:
        pass
    try:
        clearSurvey(driver)
    except: 
        pass
    time.sleep(5)
    print("inside getData, tab title: " + driver.title)
    
    try:  #this tries to get the data from the location section on the result page 
        addressLIST = driver.find_elements(By.XPATH, '//div[@class="office-location profile-subsection-bordered-container"]/section/div/address/div/span')
        addressUnedited = ''
        for item in addressLIST:
            addressUnedited = addressUnedited + item.get_attribute('innerHTML')
        clinicAddress = addressUnedited.replace('<!-- -->', '')  
        
        clinicName = driver.find_element(By.XPATH, '//div[@class="office-location profile-subsection-bordered-container"]/section/div/address/div/a').get_attribute('innerHTML')
        clinicPhone = driver.find_element(By.XPATH, '//div[@class="office-location profile-subsection-bordered-container"]/section/div[2]/div/a').get_attribute('innerHTML')
        
        currentDoctor.add_clinic_address(clinicAddress)
        print("added clinic address: " + currentDoctor.clinicAddress)
        currentDoctor.add_clinic_name(clinicName)
        print("added clinic name: " + currentDoctor.clinicName)
        currentDoctor.add_clinic_phone(clinicPhone)
        print("added clinic phone: " + currentDoctor.clinicPhone)
        return currentDoctor
    except: 
        pass 
    
     
        
    try: #make this a try
        #this gets the clinic name & address by splitting up <address> element and it's children 
        print("in address plan B")
        address = driver.find_element(By.XPATH, '//address[@class="address"]')
        addressChildren = address.find_elements(By.XPATH, './/*')
        holder = ''
        for element in addressChildren:
            if len(element.get_attribute('innerHTML')) > 1:
                holder = holder + element.get_attribute('innerHTML')
                #print(holder)
        regex = r"<(.+?)>"
        result = re.sub(regex, 'zzzzz', holder, 0, re.MULTILINE)
        #print(result)
        resultSplit = result.split('zzzzz')
        clinicName = resultSplit[1]
        print(clinicName)
        clinicAddress = resultSplit[3] + ' ' + resultSplit[6] + ', ' + resultSplit[9] + ' ' + resultSplit[12]
        print(clinicAddress)
        
        try:
            clinicPhone = driver.find_element(By.XPATH, '//div[@class="office-location profile-subsection-bordered-container"]/section/div[2]/div/a').get_attribute('innerHTML')
        except: 
            pass
        
        if len(clinicPhone) < 5:
            try: #tries the phone number by itself, as its possible for clinic/name address to not match the original technique but the phone number still does 
                clinicPhone = driver.find_element(By.XPATH, '//a[@class="toggle-phone-number-button"]').get_attribute('innerHTML')
            except: #skips the phone number if it still isn't able to get it 
                pass
        
        currentDoctor.add_clinic_address(clinicAddress)
        print("added clinic address: " + currentDoctor.clinicAddress)
        currentDoctor.add_clinic_name(clinicName)
        print("added clinic name: " + currentDoctor.clinicName)
        currentDoctor.add_clinic_phone(clinicPhone)
        print("added clinic phone: " + currentDoctor.clinicPhone)
        return currentDoctor
                        
    except NoSuchElementException: 
        #maybe log this 
        print("unable to find an element")
        pass  
        
    if len(clinicPhone) < 5:
        try: #tries the phone number by itself, as its possible for clinic/name address to not match the original technique but the phone number still does 
            clinicPhone = driver.find_element(By.XPATH, '//a[@class="toggle-phone-number-button"]').get_attribute('innerHTML')
        except: #skips the phone number if it still isn't able to get it 
            pass
        
    currentDoctor.add_clinic_address(clinicAddress)
    print("added clinic address: " + currentDoctor.clinicAddress)
    currentDoctor.add_clinic_name(clinicName)
    print("added clinic name: " + currentDoctor.clinicName)
    currentDoctor.add_clinic_phone(clinicPhone)
    print("added clinic phone: " + currentDoctor.clinicPhone)
    return currentDoctor


def findDoctor(driver, currentDoctor):
    #this function finds the currentDoctor on healthgrades 
    driver.get('https://www.healthgrades.com')
    driver.maximize_window()
    skip = False
    try:
        clearSurvey(driver)
    except:
        pass
    time.sleep(2)
    try:  #sometimes there is a satisfaction survey, this clears that if present
        dismissSatisfaction = driver.find_element(By.XPATH, '//button[@class="_hj-OO1S1__styles__openStateToggle"]')
        dismissSatisfaction.click()
    except:
        pass
    drName = currentDoctor.firstName + ' ' + currentDoctor.lastName
    nameBox = driver.find_element(By.XPATH, '//input[@name="term-input-group"]')
    nameBox.send_keys(drName)  #send Prscrbr_Last_Org_Name + ' ' + Prscrbr_First_Name here
    print("entered name: " + drName)
    time.sleep(1)
    drLocation = currentDoctor.city + ', ' + currentDoctor.state
    locationBox = driver.find_element(By.XPATH, '//input[@name="location-input-group"]')
    locationBox.click()
    locationBox.send_keys(Keys.CONTROL + "A")
    time.sleep(1)
    
    locationBox.send_keys(drLocation)  #send Prscrbr_City + ', ' +	Prscrbr_State_Abrvtn here
    print("entered location: " + drLocation)
    time.sleep(1.5)
    searchButton = driver.find_element(By.XPATH, '//button[@class="search-bar-btns__search-btn"]')
    searchButton.click() 
    time.sleep(5)
    
    addressList = driver.find_elements(By.XPATH, '//div[@class="location-info__office-loc"]/div')   
    for item in addressList:
        print(item.get_attribute('innerHTML'))
    try:  #this tries to dismiss a survey, does nothing if there isn't one present 
        dismissSurvey = driver.find_element(By.XPATH, '//button[@class="_hj-OO1S1__styles__openStateToggle"]')
        dismissSurvey.click()
    except:
        pass

    try:
        targetResult = driver.find_element(By.XPATH, '//a[@class="provider-name__lnk"]')  #this should get the first result, possibly revisit this if searches are providing multiple results or first result isn't correct 
        targetResult.click()  #this will open the details for the DR in question 
    except:
        skip = True
        print("unable to find target result, skipping")
        print(driver.title)
        print("not switching to window[1] due to skip == true")
    time.sleep(1)
    if skip == False:  
        driver.switch_to.window(driver.window_handles[1])
    print(driver.title)
    return skip

        
class Doctor:
    #this is used to save the data while working on each doctor
    def __init__(self, NPI, lastName, firstName, city, state):
        self.lastName = lastName
        self.firstName = firstName
        self.city = city
        self.state = state
        self.clinicName = ''
        self.clinicAddress = ''
        self.clinicPhone = ''
        self.NPI = NPI
    
    def add_clinic_name(self, clinicName):
        self.clinicName = clinicName
    def add_clinic_address(self, clinicAddress):
        self.clinicAddress = clinicAddress
    def add_clinic_phone(self, clinicPhone):
        self.clinicPhone = clinicPhone 
    def read_doctor(self):
        print("info in currentDoctor: ")
        print(self.NPI)
        print(self.lastName)
        print(self.firstName)
        print(self.city)
        print(self.state)
        

def main(driver):
    csvPath = './csv'
    csvDir = os.listdir(csvPath)
    excelPath = './Excels'
    excelDir = os.listdir(excelPath)
    if len(csvDir) != len(excelDir):  #this will convert excels to csv if they aren't already
        for file in excelDir:
            csvConverter()
    for file in csvDir:
        filepath = f"./csv/{file}"
        columnsNeeded = ['Prscrbr_NPI', 'Prscrbr_Last_Org_Name', 'Prscrbr_First_Name',
        'Prscrbr_City', 'Prscrbr_State_Abrvtn', 'Clinic_Address', 'Clinic_Name',
        'Clinic_Phone']
        df = pd.read_csv(filepath, dtype={"Clinic_Address": "string", "Clinic_Name": "string", "Clinic_Phone": "string"}, engine='python', usecols=columnsNeeded)
        print(df.shape)
        maxRow = df.shape[0]
        i = 1  #this is starting point 
        while i < maxRow:
            start_i = i
            print("in while loop in main, i: " + str(i))
            now = datetime.now().time()
            print(now)
            NPI = df.iloc[i, 0]
            lastName = df.iloc[i, 1]
            firstName = df.iloc[i, 2]
            city = df.iloc[i, 3]
            state = df.iloc[i, 4]
            currentDoctor = Doctor(NPI, lastName, firstName, city, state)
            skip = findDoctor(driver, currentDoctor)
            if skip == True:
                print("Unable to find doctor in healthgrades!")
                i = checkDupes(currentDoctor, df, i)
                continue
            time.sleep(7)
            currentDoctor = getData(driver, currentDoctor)
            i = logData(i, currentDoctor, df)
            if i == start_i:
                i = i+1
            csvPostPath = f"./csvPost/{file}"
            print("saving csv...")
            df.to_csv(csvPostPath, index=False)
            print("saved csv!")
        csvPostPath = f"./csvPost/{file}"
        read_file = pd.read_csv(csvPostPath)
        print("saving excel...")
        excelsPostPath = f"./ExcelsPost/{file}"
        read_file.to_excel(excelsPostPath, index = None, header=True)
        print("saved excel!")


if __name__ == '__main__': 
    driver = webdriver.Chrome()
    main(driver)