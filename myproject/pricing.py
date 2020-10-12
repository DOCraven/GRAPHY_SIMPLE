import time
import pandas as pd
import numpy as np
import datetime
import io
import sys

import config

#########################################
## CODE IS UP TO DATE AS OF 12/10/2020 ##
#########################################


startTime = time.time()

from fcn_pricing import spot_Component, network_Component, demandCharge_Component, market_Component, retailerFee_Component

def populate_NEW_Retail_Bill():
    newRetailBillDF = pd.DataFrame(index=range(17520), columns=config.facilityIndex.index)
    newRetailBillDF.index = config.demandProfiles.index
    for i in range(32):
        bill = total_Retail_Bill(i)
        newRetailBillDF.iloc[:,i] = bill
    try: 
        newRetailBillDF.to_excel("OUTPUT DATA/NEW Retail Bill.xlsx")
    except PermissionError: 
        pass 

    return newRetailBillDF


def total_Retail_Bill(facilityName):

    demandFacility = int(config.facilityIndex.iloc[facilityName, 0])
    lossFacility = config.facilityIndex.iloc[facilityName, 2]
    networkFacility = config.facilityIndex.iloc[facilityName, 1]
    tariffType = config.networkTariffs.iloc[networkFacility,18]
    print(config.networkTariffs.iloc[networkFacility, 4])
    bill = spot_Component(demandFacility, lossFacility) + network_Component(demandFacility, networkFacility, tariffType) + demandCharge_Component(demandFacility, networkFacility, tariffType) + market_Component(demandFacility, lossFacility) + retailerFee_Component(demandFacility)

    retailBillDF = pd.DataFrame(data=bill, index=config.demandProfiles.index, columns=['Retail Bill'])
    
    print('Total Annual Retail Bill: $', round(retailBillDF['Retail Bill'].sum(),2))
    endTime = time.time() - startTime
    print("Total time: ",round(endTime,2),'sec')
    return retailBillDF['Retail Bill']

def tou(facilityName): #Creates the Time of Use Network Rates DataFrame for all sites
    
    networkFacility = config.facilityIndex.iloc[facilityName, 1]
    tariffType = config.networkTariffs.iloc[networkFacility,18]
    print(config.networkTariffs.iloc[networkFacility, 4])

    touDF = pd.DataFrame(index=config.demandProfiles.index, columns=['TOU'])
    for i in range(17520):

        day = config.demandProfiles.index[i].dayofweek
        hour = config.demandProfiles.index[i].hour
        TOU = 0

        if tariffType == '2':
            TOU = config.tariffType2.iloc[hour, day]

        elif tariffType == '3':
            TOU = config.tariffType3.iloc[hour, day]

        elif tariffType == '13':
            TOU = config.tariffType13.iloc[hour, day]

        elif tariffType == '14':
            TOU = config.tariffType14.iloc[hour, day]

        elif tariffType == 'NDM':
            TOU = config.tariffTypeNDM.iloc[hour, day]
        
        elif tariffType == 'LLV':
            TOU = config.tariffTypeLLV.iloc[hour, day]

        elif tariffType == 'ND5':
            TOU = config.tariffTypeND5.iloc[hour, day]
        
        else:
            print('No Tariff Found')
            break
        
        touDF.iloc[i, 0] = config.networkTariffs.iloc[networkFacility, 8+TOU]

    return touDF['TOU']

