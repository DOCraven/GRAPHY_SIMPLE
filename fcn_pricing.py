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
tariffTypeLLV = pd.read_excel(tariffTypeExcel, sheet_name="TariffLLV", index_col=0)
tariffTypeND5 = pd.read_excel(tariffTypeExcel, sheet_name="TariffND5", index_col=0)
facilityIndex = pd.read_excel(tariffTypeExcel, sheet_name="FacilityIndex", index_col=0)


spotPrem = float(1.0425)

facility = 0
demandFacility = int(facilityIndex.iloc[facility, 0])
lossFacility = facilityIndex.iloc[facility, 2]
networkFacility = facilityIndex.iloc[facility, 1]
print(demandFacility ,lossFacility ,networkFacility )

"""
Test = 'Yarrawonga Offtake Pump station'
Time = 'Tue 01 Jan 2019 00:30'
print(demandProfiles.loc[Time, Test])
print(demandProfiles.index)
"""


def spot_Component():
    # 0.6% discrepancy with Excel model.
    spot = spotPrices.iloc[0:,0] * demandProfiles.iloc[0:,demandFacility] / 1000 * float(lossFactors.iloc[lossFacility, 0]) * float(lossFactors.iloc[lossFacility,1])*spotPrem
    spotDemandDF = pd.DataFrame(data = spot, index=demandProfiles.index, columns=['Wholesale Demand'])
    
    """
    spotDemand = np.empty(shape=[0,2])
    
    for i in range(17520):
        
        spot = spotPrices.iloc[i,0] * demandProfiles.iloc[i,demandFacility] / 1000 * lossFactors.iloc[lossFacility, 0] * lossFactors.iloc[lossFacility,1]*spotPrem
        spotDemand = np.append(spotDemand, [[demandProfiles.index[i],spot]], axis=0)
    spotDemandDF = pd.DataFrame(data=spotDemand[0:,1], index=spotDemand[0:,0], columns=['Wholesale Demand'])
    """
    sumS = spotDemandDF['Wholesale Demand'].sum()
    print(sumS)
    
    return spotDemandDF['Wholesale Demand']


def network_Component():
    
    tariffType = networkTariffs.iloc[networkFacility,18]
    print(networkTariffs.iloc[networkFacility, 4])
    
    networkCharge = np.empty(shape=[0,2])
    
    for i in range(17520):

        day = demandProfiles.index[i].dayofweek
        hour = demandProfiles.index[i].hour
        TOU = 0

        if tariffType == '2':
            TOU = tariffType2.iloc[hour, day]

        elif tariffType == '3':
            TOU = tariffType3.iloc[hour, day]

        elif tariffType == '13':
            TOU = tariffType13.iloc[hour, day]

        elif tariffType == '14':
            TOU = tariffType14.iloc[hour, day]

        elif tariffType == 'NDM':
            TOU = tariffTypeNDM.iloc[hour, day]
        
        elif tariffType == 'LLV':
            TOU = tariffTypeLLV.iloc[hour, day]

        elif tariffType == 'ND5':
            TOU = tariffTypeND5.iloc[hour, day]
        
        else:
            print('No Tariff Found')
            break
        
        
        networkRate = demandProfiles.iloc[i, demandFacility] * networkTariffs.iloc[networkFacility, 8+TOU] /100
        
        standingCharge = networkTariffs.iloc[networkFacility,8]/365/48
        totalNetworkCharge = networkRate + standingCharge
        networkCharge = np.append(networkCharge, [[demandProfiles.index[i],totalNetworkCharge]], axis=0)
    networkChargeDF = pd.DataFrame(data = networkCharge[0:, 1], index=networkCharge[0:,0], columns =['Network Charge'])
    sumN = networkChargeDF['Network Charge'].sum()
    print(sumN)
    return networkChargeDF['Network Charge']
    

def market_Component():
    
    ancil = 0.08
    AEMOpool = 0.04
    LRET = 1.02
    VEET = 0.35
    SRES = 0.51

    combMarket = float(ancil + AEMOpool + LRET + VEET + SRES)
    market = demandProfiles.iloc[0:,demandFacility] * float(lossFactors.iloc[lossFacility,0]) * combMarket / 100
    marketChargeDF = pd.DataFrame(data = 0, index = demandProfiles.index, columns = ['Market Charge'])
    marketChargeDF['Market Charge'] = market
    #print(marketChargeDF)
    """
    marketCharge = np.empty(shape=[0,2])

    for i in range(17520):

        market = combMarket * demandProfiles.iloc[i, demandFacility] / 100 * lossFactors.iloc[lossFacility,0]
        marketCharge = np.append(marketCharge, [[demandProfiles.index[i],market]], axis=0)
    marketChargeDF = pd.DataFrame(data=marketCharge[0:,1], index=marketCharge[0:,0], columns=['Market Charge'])
    """
    sumM = marketChargeDF['Market Charge'].sum()
    print(sumM)
    return marketChargeDF['Market Charge']


def retailerFee_Component():
    

    serviceCharge = 1.1 # $/day
    poolMonitor = 0.15 # c/kWh
    CTlevy = 110 # $/yr
    meterCharge = 720 # $/yr
    
    staticFee = serviceCharge/48 + CTlevy/(365*48) + meterCharge/(365*48)
    fee = staticFee + poolMonitor * demandProfiles.iloc[0:,demandFacility] /100
    retailerFeeDF = pd.DataFrame(data = 0, index = demandProfiles.index, columns = ['Retailer Fee'])
    retailerFeeDF['Retailer Fee'] = fee

    """
    retailerFee = np.empty(shape=[0,2])

    for i in range(17520):

        fee = serviceCharge/48 + CTlevy/(365*48) + meterCharge/(365*48) + poolMonitor*demandProfiles.iloc[i, demandFacility] / 100
        retailerFee = np.append(retailerFee, [[demandProfiles.index[i], fee]], axis=0)
    retailerFeeDF = pd.DataFrame(data=retailerFee[0:,1], index = retailerFee[0:,0], columns=['Retailer Fee'])
    """
    sumR = retailerFeeDF['Retailer Fee'].sum()
    print(sumR)
    return retailerFeeDF['Retailer Fee']


def total_Retail_Bill():

    bill = spot_Component() + network_Component() + market_Component() + retailerFee_Component()

    retailBillDF = pd.DataFrame(data=bill, index=demandProfiles.index, columns=['Retail Bill'])
    
    print(retailBillDF['Retail Bill'].sum())
    


total_Retail_Bill()