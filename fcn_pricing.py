import pandas as pd
import numpy as np
import datetime
import io


spotPrices = pd.read_csv("INPUT Data/Spot Price.csv", index_col=0)
spotPrices.index = pd.to_datetime(spotPrices.index)

lossFactors = pd.read_csv("INPUT DATA/Loss Factors.csv", index_col=0)

demandProfiles = pd.read_csv("INPUT DATA/Input Demand Profile.csv", index_col=0)
demandProfiles.index = pd.to_datetime(demandProfiles.index)

networkTariffs = pd.read_csv("INPUT Data/Network Tariffs.csv")
networkTariffs['Tariff Structure'] = networkTariffs['Tariff Structure'].astype(str)


tariffTypeExcel = pd.ExcelFile("INPUT DATA/Tariff Type.xlsx")
tariffType2 = pd.read_excel(tariffTypeExcel, sheet_name="Tariff2", index_col=0)
tariffType3 = pd.read_excel(tariffTypeExcel, sheet_name="Tariff3", index_col=0)
tariffType13 = pd.read_excel(tariffTypeExcel, sheet_name="Tariff13", index_col=0)
tariffType14 = pd.read_excel(tariffTypeExcel, sheet_name="Tariff14", index_col=0)
tariffTypeNDM = pd.read_excel(tariffTypeExcel, sheet_name="TariffNDM", index_col=0)



"""
tariffType2.index = pd.to_datetime(tariffType2.index)
tariffType3.index = pd.to_datetime(tariffType3.index)
tariffType13.index = pd.to_datetime(tariffType13.index)
tariffType14.index = pd.to_datetime(tariffType14.index)
"""
spotPrem = 1.0425
print(spotPrem)



#print(spotPrices.at['VIC1 Price'[5]],'VIC1 Price')

Test = 'Yarrawonga Offtake Pump station'
Time = 'Tue 01 Jan 2019 00:30'
#print(demandProfiles.loc[Time, Test])
#print(demandProfiles.index)

#spotPricedDmd = pd.DataFrame(index = demandProfiles.index)

def spot_Component():
    facility = 0

    spotDemand = np.empty(shape=[0,2])
    price = 0

    for i in range(17520):
        
        spot = spotPrices.iloc[i,0] * demandProfiles.iloc[i,facility] / 1000 * lossFactors.iloc[facility, 0] * lossFactors.iloc[facility,1]*spotPrem
        spotDemand = np.append(spotDemand, [[demandProfiles.index[i],spot]], axis=0)
        price = price + spot

    print(price)


def network_Component():
    networkFacility = 25
    tariffType = networkTariffs.iloc[networkFacility,18]
    print(networkTariffs.iloc[networkFacility, 4])
    
    #print(demandProfiles.index[48].dayofweek)
    networkCharge = np.empty(shape=[0,2])
    charge = 0
    print(demandProfiles.index[0].hour, " , ", demandProfiles.index[1].hour, " , ", demandProfiles.index[2].hour)
    print(tariffType14.iloc[0,5])
    print(tariffType14.iloc[7,5])
    print(tariffType14.iloc[6,5])
    for i in range(17520):

        day = demandProfiles.index[i].dayofweek
        hour = demandProfiles.index[i].hour
        TOU = 0

        if tariffType == '2.00':
            TOU = tariffType2.iloc[hour, day]

        elif tariffType == '3.00':
            TOU = tariffType3.iloc[hour, day]

        elif tariffType == '13.00':
            TOU = tariffType13.iloc[hour, day]

        elif tariffType == '14.00':
            TOU = tariffType14.iloc[hour, day]

        elif tariffType == 'NDM':
            TOU = tariffTypeNDM.iloc[hour, day]
        
        else:
            print('No Tariff Found')
        
        
        networkRate = demandProfiles.iloc[i, 30] * networkTariffs.iloc[networkFacility, 8+TOU] /100
        
        


        standingCharge = networkTariffs.iloc[networkFacility,8]/365/48
        totalNetworkCharge = networkRate + standingCharge
        networkCharge = np.append(networkCharge, [[demandProfiles.index[i],totalNetworkCharge]], axis=0)
        charge = charge + totalNetworkCharge

    print(charge)
    print(demandProfiles.iloc[0, 30])

network_Component()
