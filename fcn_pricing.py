import time
startTime = time.time()
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
networkTariffs['Capacity ($/kVA/year)'] = networkTariffs['Capacity ($/kVA/year)'].fillna(0)
demandCapacity = pd.read_csv("INPUT DATA/Capacity Charges.csv")


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
pwrFactor = float(0.89)

facility = 11
demandFacility = int(facilityIndex.iloc[facility, 0])
lossFacility = facilityIndex.iloc[facility, 2]
networkFacility = facilityIndex.iloc[facility, 1]
tariffType = networkTariffs.iloc[networkFacility,18]


loadTime = time.time() - startTime
print("Load time: ",round(loadTime,2),'sec')
print(networkTariffs.iloc[networkFacility, 4]) 
def spot_Component():
    # 0.6% discrepancy with Excel model. Possible error in rounding
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
    print('Wholesale Demand: $',round(sumS,2))
   
    return spotDemandDF['Wholesale Demand']


def network_Component(): 
     
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
        capacityCharge = demandCapacity.iloc[networkFacility,1] * networkTariffs.iloc[networkFacility,12]/(365*48)
        totalNetworkCharge = networkRate + standingCharge + capacityCharge
        networkCharge = np.append(networkCharge, [[demandProfiles.index[i],totalNetworkCharge]], axis=0)
    networkChargeDF = pd.DataFrame(data
     = networkCharge[0:, 1], index=networkCharge[0:,0], columns =['Network Charge'])
    sumN = networkChargeDF['Network Charge'].sum()
    networkTime = time.time() - startTime - loadTime
    print('Network Charges: $',round(sumN,2)," - Time: ", round(networkTime,2), 'sec')
    return networkChargeDF['Network Charge']
    


def demandCharge_Component():

    if tariffType == '2' or tariffType == 'NDM':
        demand = demandProfiles[(demandProfiles.index.dayofweek >=0) & (demandProfiles.index.dayofweek <=4) & (demandProfiles.index.hour >=15) & (demandProfiles.index.hour <21)]
        maxDemand = demand.iloc[0:, demandFacility]
        mnthMaxDF = pd.DataFrame(data = 0, index = [1,2,3,4,5,6,7,8,9,10,11,12], columns = ['Monthly Max'])
        for i in range(12):
                mnthMaxDF.iloc[i] = maxDemand[(maxDemand.index.month ==i+1)].max() * 2 /pwrFactor
            
    elif tariffType == '3' or tariffType == 'ND5':
        demandCharge = 0

    elif tariffType == '13' or tariffType == '14':
        demand = demandProfiles.between_time('15:00:00','19:00:00', True, False)
        maxDemand = demand.iloc[0:,demandFacility]
        dailyPeak = pd.DataFrame(data=0,index=range(365),columns=['Daily Peak'])
        for i in range(365):
            dailyPeak.iloc[i] = maxDemand[(maxDemand.index.dayofyear==i+1)].max()

        fiveDays = dailyPeak.sample(n=365)
        peakDemand = fiveDays.mean() * 2 / pwrFactor
        demandCharge = float(peakDemand * networkTariffs.iloc[networkFacility, 13] /(365*48))
        
        
    elif tariffType == 'LLV':
        demand = demandProfiles.iloc[0:, demandFacility]
        peakDemand = demand.max() * 2 / pwrFactor
        demandCharge = peakDemand * networkTariffs.iloc[networkFacility, 13] / (365*48)
        print(peakDemand)
    
    else:
        print('No Tariff Found')
        
    
    demandChargeDF = pd.DataFrame(data=0, index=demandProfiles.index, columns=['Demand Charge'])
    
    if tariffType == '2' or tariffType == 'NDM':
        for i in range(12):
            if i+1 == 1 or i+1==2 or i+1==3 or i+1==12:
                rate = networkTariffs.iloc[networkFacility, 14]
            else:
                rate = networkTariffs.iloc[networkFacility, 15]
            month = 30 #recode to get exact day in a given month
            demandChargeDF[(demandChargeDF.index.month==i+1)] = float(mnthMaxDF.iloc[i]) * float(rate)/(month*48) 
    else:
        demandChargeDF['Demand Charge'] = demandCharge

    sumD = demandChargeDF['Demand Charge'].sum()
    print('Demand Charge: $', round(sumD,2))
    return demandChargeDF['Demand Charge']
    


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
   
    
    sumM = marketChargeDF['Market Charge'].sum()
    print('Market Charge: $', round(sumM,2))
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

    sumR = retailerFeeDF['Retailer Fee'].sum()
    print("Retailer Fee: $", round(sumR,2))
    return retailerFeeDF['Retailer Fee']


def total_Retail_Bill():

    bill = spot_Component() + network_Component() + demandCharge_Component() + market_Component() + retailerFee_Component()

    retailBillDF = pd.DataFrame(data=bill, index=demandProfiles.index, columns=['Retail Bill'])
    
    print('Total Annual Retail Bill: $', round(retailBillDF['Retail Bill'].sum(),2))
    endTime = time.time() - startTime
    print("Total time: ",round(endTime,2),'sec')

total_Retail_Bill()