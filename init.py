from app import db
from db_funcs import insert_data, add_toponyms, add_locs, check_toponyms, geocode_toponyms, check_geocoding
#from celery import Celery
import schedule
import sys
import time

def init():
    db.drop_all()
    db.create_all()

def update():
    insert_data(20)
    add_toponyms()
    geocode_toponyms()
    add_locs()

def job():
    update()

def main():
    init()
    schedule.every().day.at("01:00").do(job)
    #schedule.every(1).minutes.do(job)
    while True:
        schedule.run_pending()

if __name__ == "__main__":
    #check_geocoding()
    #check_toponyms()
    #update()
    main()
    #init()
    


