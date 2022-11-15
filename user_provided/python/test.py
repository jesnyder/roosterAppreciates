from bs4 import BeautifulSoup
import datetime
import json
import math
import numpy as np
import os
import pandas as pd
import random
import re
import requests
import time

from admin import print_progress
from admin import reset_df
from admin import retrieve_df
from admin import retrieve_json
from admin import retrieve_path
from admin import save_json

from list_titles import search_scrub_title


def query_crossref():
    """
    create crossref.json
    """
    crossref_not_found('', 'reset', '', '')
    lookup_crossref()


def lookup_crossref():
    """
    create crossref.json
    """

    crossrefs = []

    pubs_dict = retrieve_json('pubs_raw')
    pubs = pubs_dict['pubs']

    for pub in pubs:

        i = pubs.index(pub)

        if i == 0: counter = 0
        counter = print_progress(pub, pubs, counter)

        title = pub['title_ref']

        crossref_dict = crossref(title)
        crossref_dict['title_ref'] = title

        crossrefs.append(crossref_dict)
        crossrefs_dict = {}
        crossrefs_dict ['item_count'] = len(crossrefs)
        crossrefs_dict ['pubs'] = crossrefs
        save_json(crossrefs_dict , 'crossref')

        test = retrieve_json('crossref')


def crossref(title):
    """
    return result
    """

    # create crossref url
    cross_ref_url = 'https://api.crossref.org/works?query.'
    title_url = cross_ref_url + 'title'
    specific_url = title_url + '=' + title.replace(' ', '+')
    url_response = requests.get(specific_url)

    try:
        text = url_response.text
        data = json.loads(text)
    except:
        pub = {}
        pub['success'] = 'No'
        pub['error'] = 'Data did not load from webpage'
        pub['url'] = specific_url
        crossref_not_found('01 Data Missing', title, ' ', specific_url)
        return(pub)

    # find the items in the crossref json
    if 'message' not in data.keys():
        pub = {}
        pub['success'] = 'No'
        pub['error'] = 'No message in data.keys'
        pub['url'] = specific_url
        crossref_not_found('02 Message Missing', title, ' ', specific_url)
        return(pub)

    message = data['message']

    if 'items' not in message.keys():
        pub = {}
        pub['success'] = 'No'
        pub['error'] = 'No items in data.message.keys'
        pub['url'] = specific_url
        crossref_not_found('03 Items Missing', title, ' ', specific_url)
        return(pub)

    items = message['items']

    for item in items:

        #if 'author' not in item.keys(): continue

        item['searched_title'] = title
        item['url'] = specific_url
        item['crossref_item_number'] = items.index(item)

        for item_title in item['title']:

            target_title = search_scrub_title(title)
            found_title = search_scrub_title(item_title)
            if target_title[:86] == found_title[:86]:
                return(item)

            if target_title == found_title[1:]:
                return(item)

            if prescribed_matches(target_title, found_title) == True:
                return(item)

    item = {}
    item['searched_title'] = title
    item['url'] = specific_url
    item['crossref_item_number'] = 'not found'
    try:
        item['first title'] = items[0]['title'][0]
        crossref_not_found('04 No title match', title, items[0]['title'][0], specific_url)
    except:
        crossref_not_found('05 No title match', title, ' ', specific_url)

    return(item)


def prescribed_matches(t1, t2):
    """
    return True if match found
    """

    r1 = 'biomimetic mineralized collagen fibrils and their effect on osteogenic differentiation'
    r2 = 'Biomimetic mineralized collagen scaffolds and their effect on osteogenic differentiation'
    if search_scrub_title(r1) == search_scrub_title(t1):
        if search_scrub_title(r2) == search_scrub_title(t2):
            return(True)

    r1 = 'a functional three dimensional microphysiological model of myeloma bone disease'
    r2 = 'A functional three‐dimensional microphysiological human model of myeloma bone disease'
    if search_scrub_title(r1) == search_scrub_title(t1):
        if search_scrub_title(r2) == search_scrub_title(t2):
            return(True)

    return(False)


def crossref_not_found(error, title, title_found, url):
    """
    list crossref not found
    """

    if  title == 'reset':
        df = pd.DataFrame()
        df['error'] = []
        df['target'] = []
        df['found'] = []
        df['url'] = []
        df.to_csv(retrieve_path('crossref_not_found'))
        return(df)

    df = retrieve_df('crossref_not_found')
    errors = list(df['error'])
    targets = list(df['target'])
    founds = list(df['found'])
    urls = list(df['url'])

    if title not in targets:
        errors.append(error)
        targets.append(title)
        founds.append(title_found)
        urls.append(url)

        df_new = pd.DataFrame()
        df_new['error'] = errors
        df_new['target'] = targets
        df_new['found'] = founds
        df_new['url'] = urls
        df_new = reset_df(df_new.sort_values(by='error'))
        df_new.to_csv(retrieve_path('crossref_not_found'))
