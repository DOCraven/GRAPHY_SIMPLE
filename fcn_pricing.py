import pandas as pd
import numpy as np
import io

spotPrices = pd.read_csv("INPUT Data/Spot Price.csv", index_col=0)
spotPrices.index = pd.to_datetime(spotPrices.index)

lossFactors = pd.read_csv("INPUT DATA/Loss Factors.csv", index_col=0)

demandProfiles = pd.read_csv("INPUT DATA/Input Demand Profile.csv", index_col=0)
demandProfiles.index = pd.to_datetime(demandProfiles.index)

#networkTariffs = pd.read_csv("INPUT Data/Network Tariffs.csv")

spotPrem = 1.0425
print(spotPrem)

#print(networkTariffs["Techone Facility name"])

#print(spotPrices.at['VIC1 Price'[5]],'VIC1 Price')

Test = 'Yarrawonga Offtake Pump station'
Time = 'Tue 01 Jan 2019 00:30'
#print(demandProfiles.loc[Time, Test])
#print(demandProfiles.index)

#spotPricedDmd = pd.DataFrame(index = demandProfiles.index)

def spot_Component():

    spotDemand = np.empty(shape=[0,2])
    price = 0

    for i in range(17520):
        
        spot = spotPrices.iloc[i,0] * demandProfiles.iloc[i,0] / 1000 * lossFactors.iloc[0, 0] * lossFactors.iloc[0,1]*spotPrem
        spotDemand = np.append(spotDemand, [[spotPrices.index[i],spot]], axis=0)
        price = price + spot

    print(price)


spot_Component()
