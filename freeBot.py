from bs4 import BeautifulSoup
import requests
from datetime import datetime as dt
import time
import tkinter as tk
from tkinter import ttk
import smtplib
from email.mime.text import MIMEText

CRAIGSLIST = "https://sfbay.craigslist.org/search/sby/zip?nh=109&nh=119&nh=31&nh=32&nh=34&nh=35&nh=36&nh=37&nh=38&nh=39&nh=40&nh=41&nh=43&nh=44&nh=45#search=1~gallery~0~0"
NEXTDOOR=''

class SCRAPER:
    def __init__(self, frequency, email):
        self.last_item_cl=''
        self.new_items_cl=[]

        self.last_item_nd=''
        self.new_items_nd=[]

        self.email_addr=email
        self.send=False
        self.frequency = frequency * 60

    def send_email_alert(self):
        try:
            data=''
            # creates SMTP session
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login("", "") #add your email and app password key as parameters
            for i in self.new_items_cl:
                data+='\r\n'
                data+=(i)
            info_string = MIMEText(data)
            info_string['Subject']='New Free Items'
            s.sendmail("Web Scraper", self.email_addr, info_string.as_string())
            # terminating the session
            s.quit()
        except Exception as e:
            print(e)
        
    def nd_init(self):
        return
    
    def nd_update(self):
        return

    def cl_init(self):
        page = requests.get(CRAIGSLIST)
        page_html = BeautifulSoup(page.text, 'html.parser')

        post = page_html.find('li', class_="cl-static-search-result")
        self.last_item_cl=(post.find('div', class_="title").get_text())

        print('Most recent item: ' , self.last_item_cl)

    def cl_update(self):
        #Get HTML
        page = requests.get(CRAIGSLIST)
        page_html = BeautifulSoup(page.text, 'html.parser')

        #Return list of posts, iterate, and find if there are new postings
        posts = page_html.findAll('li', class_="cl-static-search-result")
        for post in posts:
            item = post.find('div', class_="title").get_text()
            
            if item != self.last_item_cl:
                self.new_items_cl.append(item)
                self.new_items_cl.append(str(post.find('a').get('href')))
                self.send=True
            if item == self.last_item_cl:
                break

    def print_alert(self):  
        i=0
        for items in self.new_items_cl:
            print('New CL Listing:' ,items)
            i+=1
        try:
            self.last_item_cl=self.new_items_cl[0]
        except:
            pass
        
    
def main(email_addr, x, cl, nd):
    #Init scraper object
    my_scraper = SCRAPER(x, email_addr)
    
    my_scraper.cl_init()
    if nd==1:
        my_scraper.nd_init()

    now = dt.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    while True:
        #if cl==1:
        my_scraper.cl_update()
        my_scraper.print_alert()

        if nd==1:
            my_scraper.nd_update()
            my_scraper.print_alert()

        if my_scraper.send==True:
            my_scraper.send_email_alert()
            my_scraper.send=False
            my_scraper.new_items_cl.clear() #Empty list of new items
            my_scraper.new_items_nd.clear() #Empty list of new items

        time.sleep(my_scraper.frequency)
        now = dt.now()
        current_time = now.strftime("%H:%M:%S")
        print("Current Time =", current_time)

m = tk.Tk()
m.title('Craigslist Scraper')
m.geometry("400x180")

CheckVar1 = tk.IntVar()
CheckVar2 = tk.IntVar()

# C1 = tk.Checkbutton(m, text = "Craigslist", variable = CheckVar1, \
#                  onvalue = 1, offvalue = 0)

#C2 = tk.Checkbutton(m, text = "NextDoor",  variable = CheckVar2, \
#                 onvalue = 1, offvalue = 0)
#C1.pack()
#C2.pack()

label=tk.Label(m, text="Enter Refresh Rate (Min:1)", font=('Calibri 15')).pack()
a=tk.Entry(m, width=35)
a.pack()
label=tk.Label(m, text="minutes", font=('Calibri 8')).pack()

label=tk.Label(m, text="Enter User Email", font=('Calibri 15')).pack()
email_addr=tk.Entry(m, width=35)
email_addr.pack()

C3 = tk.Button(m, text="Go", command=lambda: main(str(email_addr.get()), int(a.get()), CheckVar1.get(), CheckVar2.get()))
C3.pack()

label=tk.Label(m, text="", font=('Calibri 15'))
label.pack()

m.mainloop()