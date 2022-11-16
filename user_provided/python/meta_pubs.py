from bs4 import BeautifulSoup
import codecs
import datetime
from datetime import datetime
import json
import math
import numpy as np
import os
from random import random
import random
import re
import requests
import pandas as pd
import shutil
import statistics
from statistics import mean
import time


from admin import make_color
from admin import reset_df
from admin import retrieve_df
from admin import retrieve_json
from admin import retrieve_list
from admin import retrieve_path
from admin import retrieve_ref

from group_pubs import find_pubs


def meta_pubs():
    """
    analyze data
    """

    print("running meta_pubs")

    tasks = [1]

    if 1 in tasks: json_meta()

    print("completed meta_pubs")


def json_meta():
    """
    save meta for json
    """

    crossref_not_found({'reset': 'reset'})
    list_crossref_without_aff({'reset': 'reset'})

    list_meta = []
    fil_src = os.listdir(retrieve_path('gscholar_json'))[-1]
    fol_src = os.path.join(retrieve_path('gscholar_json'), fil_src)
    json_src = retrieve_json(fol_src)

    for pub in json_src['results']:

        print('title = ')
        print(pub['title'])
        pub['title_search'] = search_scrub(pub['title'])
        pub_meta = search_crossref(pub['title_search'])

        for key in pub_meta.keys():
            pub[key] = pub_meta[key]

        if len(list_affs(pub)) == 0:
            pub = find_hardcoded_crossref_affs(pub)

        pub['affs'] = list_affs(pub)
        if len( list_affs(pub)) == 0:
            list_crossref_without_aff(pub)

        pub['groups'] = find_pubs(pub)
        pub['color'] = make_color()

        # don't add pubs if they don't have authors
        if 'author' not in pub.keys(): continue

        list_meta.append(pub)
        json_meta = {}
        json_meta['results_count'] = len(list_meta)
        json_meta['results'] = list_meta

        # save the dictionary as json
        fil_dst = os.path.join(retrieve_path('crossref_json'), fil_src)
        #print('fil_dst = ' + str(fil_dst))
        with open(fil_dst, "w") as fp:
            json.dump(json_meta, fp, indent = 8)
            fp.close()


def list_crossref_without_aff(pub):
    """
    list pub without affs
    """

    if 'reset' in pub.keys():
        pubs = []

    if 'reset' not in pub.keys():
        pubs = retrieve_json('crossref_missing_affs')['pubs']
        pubs.append(pub)

    pubs_json = {}
    pubs_json ['count'] = len(pubs)
    pubs_json ['pubs'] = pubs
    fil_dst = retrieve_path('crossref_missing_affs')
    with open(fil_dst, "w") as fp:
        json.dump(pubs_json , fp, indent = 8)
        fp.close()


def search_scrub(title):
    """
    convert to lowercase
    remove non number or letter characters

    """

    title = str(title)

    remove_strs = ['[HTML]', '[PDF]', '<scp>', '</scp>' , '<i>', '</i>', '[CITATION]' , '[C]' ]
    for remove_str in remove_strs:
        if remove_str in title:
            title = title.replace(remove_str, ' ')

    #title = re.sub(r'[\W_]+', '', title)
    if ' ' == title[0]: title = title[1:]
    if ' ' == title[-1]: title = title[:-1]
    title = title.lower()


    """
    #

    remove_strs = ['<scp>', '</scp>', '\n', '<i>', '</i>']
    for str in remove_strs:
        if str in title: title = title.replace(str, ' ')

    #title = re.sub('[html]', '', title)
    #title = re.sub('[pdf]', '', title)
    #title = re.sub(r'[\W_]+', '', title)
    title = re.sub(' +', ' ', title)

    """

    return(title)


def match_scrub(title):
    """
    return a title without spaces
    """

    title = search_scrub(title)
    title = re.sub('[^A-Za-z0-9]', '', title)
    #title = title.lower()

    return(title)


def search_crossref(title):
    """
    return result
    """

    print('search crossref title = ')
    print(title)

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
        pub['message'] = '01 Data did not load from webpage'
        crossref_not_found(pub)
        return(pub)

    # find the items in the crossref json
    if 'message' not in data.keys():
        pub = {}
        pub['success'] = 'No'
        pub['error'] = 'No message in data.keys'
        pub['url'] = specific_url
        pub['message'] = '02 Message Missing'
        crossref_not_found(pub)
        return(pub)

    message = data['message']

    if 'items' not in message.keys():
        pub = {}
        pub['success'] = 'No'
        pub['error'] = 'No items in data.message.keys'
        pub['url'] = specific_url
        pub['message'] = '03 No items in data.message.keys'
        crossref_not_found(pub)
        return(pub)

    items = message['items']

    if 'author' not in items[0].keys():
        pub = {}
        pub['success'] = 'No'
        pub['searched_title'] = title
        pub['error'] = '04 No author found in the items'
        pub['url'] = specific_url
        pub['message'] = '04 No author found in the items'
        crossref_not_found(pub)
        return(pub)


    found_title_first = items[0]['title'][0]
    found_title_first_scrub = match_scrub(found_title_first)

    for item in items:

        #if 'author' not in item.keys(): continue

        item['searched_title'] = title
        item['url'] = specific_url
        item['crossref_item_number'] = items.index(item)
        item['doi_url'] = str('http://dx.doi.org/' + item['DOI'])

        for item_title in item['title']:

            if title.lower() == item_title.lower():
                #if len(list_affs(item)) > 0:
                return(item)

            target_title = match_scrub(title)
            found_title =  match_scrub(item_title)

            if target_title[:86] == found_title[:86]:
                #if len(list_affs(item)) > 0:
                return(item)

            if target_title == found_title[1:]:
                #if len(list_affs(item)) > 0:
                return(item)

    item = {}
    item['searc_title'] = title
    item['found_title'] = found_title_first
    item['searc_title_scrub'] = target_title
    item['found_title_scrub'] = found_title_first_scrub
    item['affs_found'] = len(list_affs(items[0]))
    item['url'] = specific_url
    item['crossref_item_number'] = 'not found'

    item['match_found'] = False
    if target_title[:86] == found_title_first_scrub[:86]: item['match_found'] = True

    crossref_not_found(item)

    return(item)


def find_hardcoded_crossref_affs(pub_src):
    """

    """

    if 'author' not in pub_src.keys(): return(pub_src)

    ref_json = retrieve_json('crossref_with_affs')

    for pub in ref_json['pubs']:


        #if 'DOI' in pub.keys(): key = 'DOI'
        #elif 'title_link' in pub.keys():
        key = 'title_link'

        print('key = ' + str(key))

        doi_src = str(pub_src[key])
        print('1 doi_src = ' + str(doi_src))

        doi_ref = str(pub[key])
        print('2 doi_ref = ' + str(doi_ref))


        if doi_src != doi_ref: continue

        pub_src['author'] = pub['author']

        return(pub_src)

    return(pub_src)


def list_affs(pub):
    """
    return a list of affs
    """

    affs = []
    if 'author' not in pub.keys(): return(affs)
    for author in pub['author']:
        for name in author['affiliation']:
            aff = name['name']
            if aff not in affs: affs.append(aff)
    return(affs)


def crossref_not_found(item):
    """
    list crossref not found
    """

    missing_json = {}
    missing_json['pub_count'] = 0
    missing_json['pubs'] = []

    if 'reset' not in item.keys():

        try:
            missing_json = retrieve_json('missing_json')
        except:
            print('missing_json not found.')

        pubs = missing_json['pubs']
        pubs.append(item)

        missing_json['pub_count'] = len(pubs)
        missing_json['pubs'] = pubs

    fil_dst = os.path.join(retrieve_path('missing_json'))
    with open(fil_dst, "w") as fp:
        json.dump(missing_json, fp, indent = 8)
        fp.close()
