#-*-coding:utf-8-*-

from selenium import webdriver
import time
import datetime
import pandas as pd


url_ref_list=[
    ('https://www.taptap.com/category/e16?page=1', u'日新发现'),
    ('https://www.taptap.com/category/e12?page=1', u'新游预约'),
    ('https://www.taptap.com/category/e24?page=1', u'游戏测试'),
    ('https://www.taptap.com/category/e16?page=2', u'日新发现'),
    ('https://www.taptap.com/category/e12?page=2', u'新游预约'),
    ('https://www.taptap.com/category/e24?page=2', u'游戏测试')
]


def start():
    chromedriver = "./chromedriver_235.exe"
    driver = webdriver.Chrome(chromedriver)
    dm = DataManager()

    df = pd.DataFrame(columns=['title', 'url', 'type', 'rating', 'ref', 'update_date', 'img'])
    for url,ref in url_ref_list:
        print('dealing with %s' % url)
        driver.get(url)
        print('got url:' + url)
        scroll_untill_bottom_stepbystep(driver)
        print('scrolling')
        df_new=dm.scan_and_get(driver, ref)
        print('got df')
        df = pd.concat([df,df_new], ignore_index=True)
    df.to_csv('./new_game_%s.csv' % datetime.datetime.now().strftime('%Y%m%d'), encoding='utf_8_sig',index=False)
    dm.save_history()
    driver.quit()
    print("DONE:)")

def scroll_untill_bottom_stepbystep(driver, steps=3):
    """按时滚屏"""
    SCROLL_PAUSE_TIME = 1

    # Get scroll height
    for i in range(steps):
        s_size = (i + 1) * 600
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, %d);" % s_size)
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)
    print("BOTTOM NOW:)")


class DataManager():
    def __init__(self):
        self.df_history=pd.read_csv('./new_game_history.csv', encoding='utf_8_sig')

    def save_history(self):
        self.df_history.to_csv('./new_game_history.csv', encoding='utf_8_sig',index=False)

    def scan_and_get(self, driver, ref):
        df = pd.DataFrame(columns=['title', 'url', 'type', 'rating', 'ref', 'update_date', 'img'])
        items = driver.find_elements_by_class_name('taptap-app-item')
        date_str = datetime.datetime.now().strftime('%Y%m%d')
        for item in items:
            e_href = item.find_elements_by_class_name('app-item-image')
            href   = e_href[0].get_attribute('href').strip() if e_href != [] else ''

            e_detail = item.find_elements_by_tag_name('img')
            title  = e_detail[0].get_attribute('title') if e_detail != [] else ''
            imgsrc = e_detail[0].get_attribute('src').strip()    if e_detail != [] else ''

            e_rating = item.find_elements_by_class_name('caption-label-rating')
            rating   = e_rating[0].text.strip() if e_rating != [] else ''

            e_gametype = item.find_elements_by_css_selector('div > span > a')
            gametype   = e_gametype[0].text.strip() if e_gametype != [] else ''

            if title not in set(self.df_history.title):
                row = pd.Series([title, href, imgsrc, gametype, rating, ref, date_str],
                          index=['title', 'url', 'img', 'type', 'rating','ref', 'update_date'])
                self.df_history=self.df_history.append(row, ignore_index=True) # append to history
                df=df.append(row, ignore_index=True) # add to new
        return df

if __name__ == '__main__':
    start()


#start()