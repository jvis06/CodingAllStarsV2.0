from bs4 import BeautifulSoup
import requests
import csv
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from datetime import date, timedelta




def printer():
    with open("./apps/result.csv", 'w') as result:
        fieldnames = ["Course Name", "Course Link", "Coupon", "Expiration"]
        writer = csv.writer(result)

        writer.writerow(fieldnames)
        

        for i in range(len(coursename)):
            writer.writerow([coursename[i], courselink[i], couponcode[i], coursedate[i]])
    print("Scraping Completed! You're Welcome!")
    driver.quit()




def udemy(func): #udemy get
    driver.maximize_window()

    for data in finurls:
        time.sleep(2)
        driver.get(data)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        try:
            badge = soup.find('div', class_="clp-lead").find('div', class_="ud-badge").text.strip()
            if str(badge) == "Free tutorial":
                continue
            else:
                raise AttributeError
        except AttributeError:
            tempurl = driver.current_url
            tempcoursecode = tempurl.find("couponCode=")
            if tempcoursecode == -1:
                continue
            else:
                tempcourselink = tempurl.find("?")
                courselink.append(tempurl[:tempcourselink])
                couponcode.append(tempurl[tempcoursecode+11:])
                coursename.append(soup.find('h1', class_="clp-lead__title").text.strip())
                try:
                    tempexpire = soup.find('div', class_="buy-box--discount-expiration--22scc").find('b').text.strip()
                    if tempexpire.find('day') > -1:
                        tempexpire2 = tempexpire.find('day') - 1
                        coursedate.append(now + timedelta(days=tempexpire2))
                    elif tempexpire.find('hour') > -1:
                        tempexpire2 = tempexpire.find('hour') - 1
                        coursedate.append(now + timedelta(hours=tempexpire2))
                    elif tempexpire.find('min') > -1:
                        tempexpire2 = tempexpire.find('min') - 1
                        coursedate.append(now + timedelta(minutes=tempexpire2))
                    elif tempexpire.find('sec') > -1:
                        tempexpire2 = tempexpire.find('sec') - 1
                        coursedate.append(now + timedelta(seconds=tempexpire2))

                except AttributeError:
                    coursedate.append("No Expiration Date")
                
                if len(coursename) == 100:
                    break
            
    if len(coursename) == 100:
        printer()
    else:
        if func == "firstURL":
            finurls.clear()
            links.clear()
            print("Coupons not enough, I'm calling the 2nd URL..")
            driver.minimize_window()
            secURL(URL2)
        elif func == "secURL":
            finurls.clear()
            links.clear()
            print("Coupons still not enough, calling 3rd URL...")
            thirdURL(URL3)
        else:
            print("All links depleted. No more additional links.")
            printer()




def firstURL(url):

    driver.get(url)

    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located
        ((By.CLASS_NAME, "btn-primary")))
        time.sleep(2)
    except TimeoutException:
        print("\n\nPage TimeOut, please check your Internet Connection.")
        driver.quit()

    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    maincont = soup.find('div', class_="mt-4")
    cont = maincont.find_all('li')

    while len(cont) < 150:
        driver.find_element(By.CLASS_NAME, "btn-primary").click()
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        maincont = soup.find('div', class_="mt-4")
        cont = maincont.find_all('li')


    for data in cont:
        if not data.find('div', class_="mr-0").text.strip(): #get the timestamp of the container
            continue
        else:
            textcent = data.find('div', class_="mt-2").find_all('div', class_="text-center")
            tempdate = textcent[1].find('div', class_="mt-1").text.strip() #get the time of the container
            tempdate2 = tempdate[tempdate.find("hr")-1] #isolate the integer

            if int(tempdate2) < 49: #check if less than 2 days in hours
                links.append("https://www.real.discount" + data.find('a').get('href').strip())
            else:
                continue

    driver.minimize_window()

   
    print("Please be patient. I'll let you know if there's something wrong.")
    print("I'm parsing a lot of URLs, this might take a while..")

    for link in links:
        time.sleep(2)

        req = requests.get(link, params=params)

        if req.status_code != 200:
            print("Something wrong with the server - expected behavior")
        
        else:
            soup = BeautifulSoup(req.text, "html.parser")
            test = soup.find_all('div', class_="p-4")
            test2 = test[1].find_all('div', class_="mt-4")
            test3 = test2[1].find('a').get("href")

            if test3.find('https://www.udemy.com/course') > -1:
                if test3.find('couponCode=') > -1:
                    finurls.append(test3) #Main URL list with coupon codes
        

    udemy("firstURL")

    
    
    




def secURL(url):
    
    print("I'm still here. No need to worry..")
    req = requests.get(url, params=params)

    if req.status_code != 200:
        print("Something wrong with the server - expected behavior")

    else:
        soup = BeautifulSoup(req.text, "html.parser")
        maxp = soup.find('ul', class_="pagination3").find_all('li')
        maxpage = maxp[6].find('a').text.strip() #getmaxpage

        for page in range(1, int(maxpage)):
            
            req = requests.get(url + str(page), params=params)

            if req.status_code != 200:
                print("Something wrong with the server - expected behavior")

            else:
                maincont = soup.find('article', class_="four").find_all('section', class_="card")
                
                for data in maincont:
                    try:
                        tempdate = data.find('div', class_="label").text.strip()
                        if tempdate.find("Today") > -1 or tempdate.find("Yesterday") > -1:
                            links.append(data.find('a',class_="card-header").get("href").strip())
                    except:
                        continue

                    if len(links) > 150:
                        break
            if len(links) > 150:
                break
    

    for data in links:

        req = requests.get(data, params=params)

        if req.status_code != 200:
                print("Something wrong with the server - expected behavior")
        else:
            soup = BeautifulSoup(req.text, "html.parser")
            templink = soup.find('a', class_="discBtn").get('href').strip()

            req2 = requests.get(templink, params=params)

            if req.status_code != 200:
                print("Something wrong with the server")
            else:
                soup = BeautifulSoup(req2.text, "html.parser")
                cou = soup.find(id="couponLink").get('href').strip()

                if cou.find("couponCode=") > -1:
                    finurls.append(cou)
    
    print("Relax, I'm still parsing the URLs..")

    udemy("secURL")





def thirdURL(url):
    driver.get(url)
    time.sleep(2)

    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    maxp = soup.find('div', class_="pagination")
    maxp2 = maxp.find_all('li')
    maxpages = maxp2[4].find('a').text.strip()

    maincont = soup.find("div", class_="pt5").find_all('article', class_="col_item")

    for i in range(1, int(maxpages)):
        driver.get(url + "page/" + str(i))
        time.sleep(2)

        for data in maincont:
            datetest = data.find('span', class_="date_ago").text.strip()
            if datetest.find("sec") > -1 or datetest.find("min") > -1 or datetest.find("hour") > -1 or datetest.find("1 day") > -1:
                links.append(data.find('a', class_="img-centered-flex").get('href'))

            if len(links) > 150:
                break
        if len(links) > 150:
            break
    
    for link in links:
        driver.get(link)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        testlink = soup.find('span', class_="rh_button_wrapper").find('a').get('href')
        
        while testlink.find("javascript:void(0)") > -1:
            soup = BeautifulSoup(driver.page_source, "html.parser")
            testlink = soup.find('span', class_="rh_button_wrapper").find('a').get('href')
            time.sleep(1)
        
        finurls.append(testlink)

    print("Almost Done...")
    udemy("thirdURL")
    
        


                    


                
                
                

    








    

    
    
    



links = []
links2 = []
finlinks = []
finurls = []

coursename = []
coursedate = []
courselink = []
couponcode = []


now = date.today()

URL = "https://www.real.discount/"
URL2 = "https://www.discudemy.com/all/"
URL3 = "https://couponscorpion.com/"

params = {
    "count": 10
}
print("\n\nUdemy Coupon Scraping starts now!")
driver = uc.Chrome()
firstURL(URL)

