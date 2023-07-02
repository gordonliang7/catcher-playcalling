import numpy as np 
import pandas as pd

from requests import get
from bs4 import BeautifulSoup as bs

soup = bs(get('https://www.fangraphs.com/guts.aspx?type=cn').content,'html.parser')

trs = soup.find_all('tr')[15].find_all('tr')

cols = [i.string for i in trs[0].find_all('th')]
data = [i.find_all('td') for i in trs[1:]]

weights = pd.DataFrame({cols[ind]:[float(i[ind].string) for i in data] for ind in range(14)})
weights['Season'] = [int(i) for i in weights['Season']]
weights = weights.set_index('Season')

valid_events=['catcher_interf','double', 'double_play', 'field_error',
       'field_out', 'fielders_choice', 'fielders_choice_out', 'force_out',
       'grounded_into_double_play', 'single', 'sac_fly', 'hit_by_pitch', 'walk',
       'home_run', 'other_out', 'sac_bunt_double_play',
       'sac_fly_double_play', 'strikeout',
       'strikeout_double_play', 'triple', 'triple_play',]

def dissect_events(lst):
    missing_events = [i for i in valid_events if i not in pd.Series(lst).values]
    val_counts = pd.Series(lst).value_counts()
    for i in missing_events:
        val_counts[i] = 0
    ret_dict = {event: val_counts[event] for event in ['single','double','triple','home_run','strikeout',
    'walk','hit_by_pitch']}
    ret_dict['hits'] = sum([val_counts[i] for i in ['single','double','triple','home_run']])
    ret_dict['PA'] = len([i for i in lst if i in valid_events])
    ret_dict['AB'] = len([i for i in lst if i in [j for j in valid_events if j not in ['walk','sac_fly','sac_bunt','hit_by_pitch']]])
    return ret_dict

def wOBA_calculator(lst,year=2020):
    '''insert a list of events and get an approximate wOBA value'''
    lst = dissect_events(lst)
    yd=weights.loc[year]
    return ((yd['wBB']*lst['walk'])+
    (yd['wHBP']*lst['hit_by_pitch'])+(yd['w1B']*lst['single'])+
    (yd['w2B']*lst['double'])+(yd['w3B']*lst['triple'])+(yd['wHR']*lst['home_run']))/(lst['PA'])

def OPS_calculator(lst):
    return (sum([lst[i] for i in ['single','double','triple','home_run','hit_by_pitch','walk']])/lst['PA'])+((lst['single']+(2*lst['double'])+(3*lst['triple'])+(4*lst['home_run']))/lst['AB'])