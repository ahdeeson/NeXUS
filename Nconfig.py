"""
fanctions to work with Nexus config files

@author: Slawa
"""

import pandas as pd

motor_config_parameters=['vendor',
                         'SN',
                         'position',
                         'home position' ,
                         'units',
                         'limit min',
                         'limit max',
                         'com',
                         'NexusID',
                         'userID',
                         'left name',
                         'right name']

camera_config_parameters=['vendor',
                          'model',
                         'SN',
                         'IP',
                         'sensor size',
                         'pixel size',
                         'AOI',
                         'Tintegration',
                         'Naverage',
                         'crosshair position',
                         'NexusID',
                         'userID']

#in um
pixel_size_lib={'Basler-a2A2590-22gmBAS' : (2,2),
                'Basler-a2A5320-7gmBAS' : (2.74,2.74)}

def NexusIDs(data):
    """extract list of Nexus IDs from the config dictionary"""
    K=list(data.keys())
    return K, [data[k]['NexusID'] for k in K]

def findID(data,vendor,SN):
    """find elecment with given vandor and SN parameters in the config dictionary"""
    K=list(data.keys())
    items=[(data[k]['vendor'],data[k]['SN']) for k in K]
    # print('config items', items)
    # print('(vendor,SN)',(vendor,SN))

    if (vendor,SN) in items:
        return items.index((vendor,SN))
    else:
        return None