import time
startTime = time.time()
import pandas as pd
import numpy as np
import datetime
import io
import config


"""
facility = 25
demandFacility = int(facilityIndex.iloc[facility, 0])
lossFacility = facilityIndex.iloc[facility, 2]
networkFacility = facilityIndex.iloc[facility, 1]
tariffType = networkTariffs.iloc[networkFacility,18]
"""

loadTime = time.time() - startTime
print("Load time: ",round(loadTime,2),'sec')
print('Please Open NEW GRAPHY in your web browser')
 
def spot_Component(demandFacility, lossFacility):
    spotPrem = float(1.0425)
    # 0.6% discrepancy with Excel model. Possible error in rounding
    spot = config.spotPrices.iloc[0:,0] * config.demandProfiles.iloc[0:,demandFacility] / 1000 * float(config.lossFactors.iloc[lossFacility, 0]) * float(config.lossFactors.iloc[lossFacility,1])*spotPrem
    spotDemandDF = pd.DataFrame(data = spot, index=config.demandProfiles.index, columns=['Wholesale Demand'])
    
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

def network_Component(demandFacility, networkFacility, tariffType): 
     
    networkChargeDF = pd.DataFrame(index=config.demandProfiles.index,columns=['Network Charge'])

    networkRate = config.demandProfiles.iloc[:, demandFacility] * config.timeOfUse.iloc[:,networkFacility] /100
    standingCharge = config.networkTariffs.iloc[networkFacility,8]/365/48
    capacityCharge = config.demandCapacity.iloc[networkFacility,1] * config.networkTariffs.iloc[networkFacility,12]/(365*48)
    totalNetworkCharge = networkRate + standingCharge + capacityCharge
    networkChargeDF['Network Charge'] = totalNetworkCharge
    
    sumN = networkChargeDF['Network Charge'].sum()
    networkTime = time.time() - startTime - loadTime
    print('Network Charges: $',round(sumN,2)," - Time: ", round(networkTime,2), 'sec')
    return networkChargeDF['Network Charge']
    
def demandCharge_Component(demandFacility, networkFacility, tariffType):
    pwrFactor = float(0.89)
    if tariffType == '2' or tariffType == 'NDM':
        demand = config.demandProfiles[(config.demandProfiles.index.dayofweek >=0) & (config.demandProfiles.index.dayofweek <=4) & (config.demandProfiles.index.hour >=15) & (config.demandProfiles.index.hour <21)]
        maxDemand = demand.iloc[0:, demandFacility]
        mnthMaxDF = pd.DataFrame(data = 0, index = [1,2,3,4,5,6,7,8,9,10,11,12], columns = ['Monthly Max'])
        for i in range(12):
                mnthMaxDF.iloc[i] = maxDemand[(maxDemand.index.month ==i+1)].max() * 2 /pwrFactor
            
    elif tariffType == '3' or tariffType == 'ND5':
        demandCharge = 0

    elif tariffType == '13' or tariffType == '14':
        demand = config.demandProfiles.between_time('15:00:00','19:00:00', True, False)
        maxDemand = demand.iloc[0:,demandFacility]
        dailyPeak = pd.DataFrame(data=0,index=range(365),columns=['Daily Peak'])
        for i in range(365):
            dailyPeak.iloc[i] = maxDemand[(maxDemand.index.dayofyear==i+1)].max()

        fiveDays = dailyPeak.sample(n=365)
        peakDemand = fiveDays.mean() * 2 / pwrFactor
        demandCharge = float(peakDemand * config.networkTariffs.iloc[networkFacility, 13] /(365*48))
        """ The following code activates the sensitivity analysis
        sensitivityDF = pd.DataFrame(data=0, index=range(50000), columns=['Demand Charge'])
        for i in range(50000):
            sample = dailyPeak.sample(n=5)
            sampleD = sample.mean() * 2/ pwrFactor
            sampleCharge = float(sampleD * networkTariffs.iloc[networkFacility, 13])
            sensitivityDF.iloc[i] = sampleCharge
        sensitivityDF.to_excel("INPUT DATA/Demand Charge Analysis.xlsx")
        """
    elif tariffType == 'LLV':
        demand = config.demandProfiles.iloc[0:, demandFacility]
        peakDemand = demand.max() * 2 / pwrFactor
        demandCharge = peakDemand * config.networkTariffs.iloc[networkFacility, 13] / (365*48)
        print(peakDemand)
    
    else:
        print('No Tariff Found')
        
    
    demandChargeDF = pd.DataFrame(data=0, index=config.demandProfiles.index, columns=['Demand Charge'])
    
    if tariffType == '2' or tariffType == 'NDM':
        for i in range(12):
            if i+1 == 1 or i+1==2 or i+1==3 or i+1==12:
                rate = config.networkTariffs.iloc[networkFacility, 14]
            else:
                rate = config.networkTariffs.iloc[networkFacility, 15]
            month = 30 #recode to get exact day in a given month
            demandChargeDF[(demandChargeDF.index.month==i+1)] = float(mnthMaxDF.iloc[i]) * float(rate)/(month*48) 
    else:
        demandChargeDF['Demand Charge'] = demandCharge

    sumD = demandChargeDF['Demand Charge'].sum()
    print('Demand Charge: $', round(sumD,2))
    return demandChargeDF['Demand Charge']
    
def market_Component(demandFacility, lossFacility):
    
    ancil = 0.08
    AEMOpool = 0.04
    LRET = 1.02
    VEET = 0.35
    SRES = 0.51

    combMarket = float(ancil + AEMOpool + LRET + VEET + SRES)
    market = config.demandProfiles.iloc[0:,demandFacility] * float(config.lossFactors.iloc[lossFacility,0]) * combMarket / 100
    marketChargeDF = pd.DataFrame(data = 0, index = config.demandProfiles.index, columns = ['Market Charge'])
    marketChargeDF['Market Charge'] = market
    
    sumM = marketChargeDF['Market Charge'].sum()
    print('Market Charge: $', round(sumM,2))
    return marketChargeDF['Market Charge']

def retailerFee_Component(demandFacility):
    
    serviceCharge = 1.1 # $/day
    poolMonitor = 0.15 # c/kWh
    CTlevy = 110 # $/yr
    meterCharge = 720 # $/yr
    
    staticFee = serviceCharge/48 + CTlevy/(365*48) + meterCharge/(365*48)
    fee = staticFee + poolMonitor * config.demandProfiles.iloc[0:,demandFacility] /100
    retailerFeeDF = pd.DataFrame(data = 0, index = config.demandProfiles.index, columns = ['Retailer Fee'])
    retailerFeeDF['Retailer Fee'] = fee

    sumR = retailerFeeDF['Retailer Fee'].sum()
    print("Retailer Fee: $", round(sumR,2))
    return retailerFeeDF['Retailer Fee']


"""
newTOUDF = pd.DataFrame(index=range(17520), columns=facilityIndex.index)
newTOUDF.index = demandProfiles.index
for i in range(32):
    t = tou(i)
    newTOUDF.iloc[:,i] = t
    print(time.time()-startTime)
newTOUDF.to_excel("INPUT DATA/TOU.xlsx")
"""

