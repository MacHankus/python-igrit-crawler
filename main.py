from typing import List
import pandas
from settings import settings
from client_intercations import get_date_from_user, get_words_from_user
import datetime as dt 
import crawler
import pandas as pd

def which_words_matched(text, words):
    which = []
    for word in words:
        if word.lower() in text.lower():
            which.append(word)
    return format_which(which)

def format_which(which):
    which = sorted(which)
    if len(which) == 0:
        return ""

    return ";".join(which)

class Main:
    date_stop: dt.datetime
    dataframe: pandas.DataFrame = pandas.DataFrame({"ad_type":[], "ad_date":[], "ad_text":[]})
    words: List[str] = []
    def __init__(self):
        print(f"Starting program ({settings.APP_NAME}).")
        self.date_stop = get_date_from_user("Provide MIN date: ", settings.DATE_FORMAT)
        self.words = get_words_from_user("Provide words separated by space (' '): ")
        print(f"Provided date : ({self.date_stop}).")

    def start_crawling(self):
        
        for category in settings.CATEGORY_URL_PARTS:
            main_url = settings.BASE_URL + category
            cr = crawler.MainCrawler(url = main_url, url_page_part= settings.PAGE_URL_PART , start_page= settings.STARTING_PAGE, stop_date=self.date_stop, time_between_requests= settings.API_TIME_BETWEEN_REQUESTS_SECONDS)
            cr.prepare()
            try:
                cr.analize()
            except Exception as e :
                print("There was a problem during analyzing data. Probably page was changed since last script modification or page couldnt be downloaded. Please contact with script creator.")
                raise 
            finally:
                data:list = cr.get_model()
                if len(data) > 0:
                    print("Some data exists and will be saved inside csv file.")
                    df_from_data = pandas.DataFrame([x.__dict__ for x in data])
                    self.dataframe = pd.concat([self.dataframe, df_from_data])
                    self.process_and_save_df()
                else:
                    print("Nothing fetched.")

    def process_and_save_df(self):
        new_dataframe = self.dataframe[self.dataframe['ad_type'].isin(settings.AD_TYPES)]
        new_dataframe = new_dataframe.drop_duplicates()
        new_dataframe['found_words'] = new_dataframe.apply(lambda x: which_words_matched(x['ad_text'], self.words), axis=1)
        new_dataframe.to_csv(settings.CSV_PATH + dt.datetime.now().strftime('%Y%m%d%H%M%S') + "_" + settings.CSV_FILENAME)

if __name__ == '__main__':
    main = Main()
    main.start_crawling()

