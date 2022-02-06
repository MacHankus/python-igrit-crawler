from abc import abstractmethod
from time import sleep
from typing import List, Optional
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
import datetime as dt
from bs4 import Tag
from exceptions import PageChangedException

def filter_endline(arr):
    return list(filter(lambda x: x !='\n', arr))

def get_from_nested_contents(tag : Tag, arr: list):
    if len(arr) == 1:
        poped = arr.pop(0)
        return filter_endline(tag.contents)[poped]
    else:
        poped = arr.pop(0)
        return get_from_nested_contents(filter_endline(tag.contents)[poped], arr )


class Selectors():
    main_div_selector:str = 'body > div.content > div.row.grid > div.col-2'
    all_cards_from_main_div:str = 'div.card-panel > div.card' 
    all_children_from_main:str = 'div.card-panel > *' 

class CardData(BaseModel):
    ad_type: str
    ad_date: dt.datetime
    ad_text: str

class BaseCrawler():

    @abstractmethod
    def analize(self):
        pass
    
    @abstractmethod
    def get_model(self):
        pass

class CardCrawler(BaseCrawler):
    ad_type: str
    ad_date: dt.datetime
    ad_text: str

    def __init__(self, card: Tag):
        self.card= card

    def ad_date_cleaner(self, d:str ) :
        to_delete = "\n \t \r"
        new_d = d.strip()
        for x in to_delete.split(' '):
            new_d = new_d.replace(x, '')
        
        return self.convert_ad_date_cleaner_to_datetime(new_d)
        
    def convert_ad_date_cleaner_to_datetime(self, d: str ) -> dt.datetime :
        try:
            return dt.datetime.strptime(d, '%d.%m.%Y %H:%M')
        except:
            print(f'Exception occured for date string: ({d})')
            raise

    def analize(self):
        items = filter_endline(self.card.contents) 
        header = items[0]
        header_ad_type_and_date = filter_endline(get_from_nested_contents(header, [0]).contents)
        """First child is ad type."""
        self.ad_type = header_ad_type_and_date[0].get_text()
        """Second child is ad date."""
        self.ad_date = self.ad_date_cleaner(header_ad_type_and_date[1].get_text())

        text = items[1]
        self.ad_text = get_from_nested_contents(text,[0,0,1]).get_text()        
            
    def get_model(self) -> CardData:
        return CardData(ad_type=self.ad_type, ad_date=self.ad_date,ad_text=self.ad_text)


class MainCrawler(BaseCrawler):
    cards_data: List[CardData] = []
    def __init__(self, url: str, start_page:int, stop_date: dt.datetime,url_page_part:str,time_between_requests:float, step: int = 1):
        self.url = url
        self.start_page = start_page
        self.step = step
        self.stop_date = stop_date
        self.url_page_part = url_page_part
        self.time_between_requests = time_between_requests
    def get(self, page_number):
        created_url = self.url + self.url_page_part + str(page_number)
        print(f"Getting url: {created_url}")
        response = requests.get(url=created_url)
        if not response.ok:
            raise Exception(f"Something gone wrong during request to the page ({created_url}). Error message got from request : ({response.text})")
        return BeautifulSoup(response.text, 'html.parser')
        
    def prepare(self):
        soup = self.get(1)
        main = soup.select_one(Selectors.main_div_selector) 
        children = main.select(Selectors.all_children_from_main)
        pages = children[-2]
        self.max_page = int(get_from_nested_contents(pages, [1, 0, -2, 0]).get_text())
        print(f"""
        Process prepared with parameters: 
            max_page: ({self.max_page})
            start_page: ({self.start_page})
            step: ({self.step})
            stop_date: ({self.stop_date})
        """)
    def analize(self):
        for page_number in range(self.start_page, self.max_page + 1):
            sleep(self.time_between_requests)
            soup = self.get(page_number)
            main = soup.select_one(Selectors.main_div_selector)
            cards = main.select(Selectors.all_cards_from_main_div)
            max_date_from_all_cards = None
            for card in cards:
                cc = CardCrawler(card)
                cc.analize()
                model = cc.get_model()
                if model.ad_date >= self.stop_date : self.cards_data.append(model)
                if max_date_from_all_cards is None :
                    # if None then insert for future check
                    max_date_from_all_cards = model.ad_date
                elif model.ad_date > max_date_from_all_cards:
                    # max_date_from_all_cards should not be None here, just check dates
                    max_date_from_all_cards = model.ad_date
            # now check if max_date from cards is lower than stop_date. It suggests that next page have no data with dates > than stop_date, so it should not be analized and program should stop.
            if max_date_from_all_cards < self.stop_date:
                print('Stop date found. Proces going down.')
                return
        print("Last page was analyzed.")

            
                

    def get_model(self)  -> List[CardData]:
        return self.cards_data