import codecs
import datetime
from datetime import datetime
import json
import math
import numpy as np
import os
from random import random
import pandas as pd
import shutil
import statistics
from statistics import mean
import time


from admin import reset_df
from admin import retrieve_list
from admin import retrieve_path
from admin import retrieve_ref

from list_pubs import list_pubs
from meta_pubs import meta_pubs
from geolocate_affs import geolocate_affs
from group_pubs import group_pubs
from write_geojson import write_geojson
from build_table import build_table
from contact_list import contact_list

def main():
    """
    analyze data
    """

    print("running main")

    tasks = [5, 6, 7]

    if 1 in tasks: list_pubs()
    if 2 in tasks: meta_pubs()
    if 3 in tasks: geolocate_affs()
    if 4 in tasks: group_pubs()
    if 5 in tasks: write_geojson()
    if 6 in tasks: build_table()
    if 7 in tasks: contact_list()

    print("completed main")


if __name__ == "__main__":
    main()
