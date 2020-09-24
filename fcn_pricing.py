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

    for i in range(17520):
        
        spot = spotPrices.iloc[i,0] * demandProfiles.iloc[i,facility] / 1000 * lossFactors.iloc[facility, 0] * lossFactors.iloc[facility,1]*spotPrem
        spotDemand = np.append(spotDemand, [[demandProfiles.index[i],spot]], axis=0)
    spotDemandDF = pd.DataFrame(data=spotDemand[0:,1], index=spotDemand[0:,0], columns=['Wholesale Demand'])
    spotDemandDF['Wholesale Demand'].sum()


def network_Component():
    networkFacility = 25
    tariffType = networkTariffs.iloc[networkFacility,18]
    print(networkTariffs.iloc[networkFacility, 4])
    
    #print(demandProfiles.index[48].dayofweek)
    networkCharge = np.empty(shape=[0,2])
    
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

        elif tariffType == '14':
            TOU = tariffType14.iloc[hour, day]

        elif tariffType == 'NDM':
            TOU = tariffTypeNDM.iloc[hour, day]
        
        else:
            print('No Tariff Found')
        
        
        networkRate = demandProfiles.iloc[i, 30] * networkTariffs.iloc[networkFacility, 8+TOU] /100
        
        standingCharge = networkTariffs.iloc[networkFacility,8]/365/48
        totalNetworkCharge = networkRate + standingCharge
        networkCharge = np.append(networkCharge, [[demandProfiles.index[i],totalNetworkCharge]], axis=0)
    networkChargeDF = pd.DataFrame(data = networkCharge[0:, 1], index=networkCharge[0:,0], columns =['Network Charge'])
    networkChargeDF['Network Charge'].sum()
    



def market_Component():
    marketFacility = 9
    ancil = 0.08
    AEMOpool = 0.04
    LRET = 1.02
    VEET = 0.35
    SRES = 0.51

    combMarket = ancil + AEMOpool + LRET + VEET + SRES

    marketCharge = np.empty(shape=[0,2])

    for i in range(17520):

        market = combMarket * demandProfiles.iloc[i, 30] / 100 * lossFactors.iloc[marketFacility,0]
        marketCharge = np.append(marketCharge, [[demandProfiles.index[i],market]], axis=0)
    marketChargeDF = pd.DataFrame(data=marketCharge[0:,1], index=marketCharge[0:,0], columns=['Market Charge'])
    print(marketChargeDF['Market Charge'].sum())


