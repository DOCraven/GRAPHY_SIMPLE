import pandas as pd 
## file to define global variables ##

#interval data
Weekly_Interval_Data = []
Daily_Interval_Data = []
Monthly_Sum = []
Yearly_Sum = []
names = [] #placeholder for column headers (ie, site names) for interval data
chosen_site = ''

#pricing data
Daily_Pricing_Data = []
Weekly_Pricing_Data = []
Pricing_names = [] #placeholder for column headers for pricing data


Solar_Imported = False
Solar_Exists = False

Data_Uploaded = False

#figures - yes this is bad juju but I need it to work 
solar_figure_line = ''
solar_figure_summed = ''
yearly_summed_figure = ''


#importing stuff - related to parse_contents file 
Solar = pd.DataFrame() #empty dataframe for solar 
Consumption = pd.DataFrame() #empty dataframe for consumption  


reset_dataframes = False
number_of_files_uploaded = 0

#load shifting vars
plot_title = ''
shifted_site_to_save = pd.DataFrame() #empty dataframe
Checked_YEARLY_Interval_Data = pd.DataFrame() #dataframe for inputting into load shifter 
YEARLY_shifted_site = pd.DataFrame() #for saving the load shifted data after analysis
Entire_Yearly_Site_With_Single_Shifted = pd.DataFrame() #for shifted pricing data
yearly_summed_positive = 0
shifted_site_value = 0 #ie, the slider value for shifting
summed = 0 #total kWh hours summed
### PRICING DATA ###

# networkTariffs = pd.read_csv("INPUT Data/Network Tariffs.csv")
# networkTariffs['Tariff Structure'] = networkTariffs['Tariff Structure'].astype(str)
# networkTariffs['Capacity ($/kVA/year)'] = networkTariffs['Capacity ($/kVA/year)'].fillna(0)
# demandCapacity = pd.read_csv("INPUT DATA/Capacity Charges.csv")

# tariffTypeExcel = pd.ExcelFile("INPUT DATA/Tariff Type.xlsx")
# tariffType2 = pd.read_excel(tariffTypeExcel, sheet_name="Tariff2", index_col=0)
# tariffType3 = pd.read_excel(tariffTypeExcel, sheet_name="Tariff3", index_col=0)
# tariffType13 = pd.read_excel(tariffTypeExcel, sheet_name="Tariff13", index_col=0)
# tariffType14 = pd.read_excel(tariffTypeExcel, sheet_name="Tariff14", index_col=0)
# tariffTypeNDM = pd.read_excel(tariffTypeExcel, sheet_name="TariffNDM", index_col=0)
# tariffTypeLLV = pd.read_excel(tariffTypeExcel, sheet_name="TariffLLV", index_col=0)
# tariffTypeND5 = pd.read_excel(tariffTypeExcel, sheet_name="TariffND5", index_col=0)
# facilityIndex = pd.read_excel(tariffTypeExcel, sheet_name="FacilityIndex", index_col=0)
# timeOfUse = pd.read_excel(tariffTypeExcel, sheet_name="TOU", index_col=0)

spotPrices = pd.DataFrame()
lossFactors = pd.DataFrame()

networkTariffs = pd.DataFrame()
demandCapacity = pd.DataFrame()

tariffTypeExcel = pd.DataFrame()
tariffType2 = pd.DataFrame()
tariffType3 = pd.DataFrame()
tariffType13 = pd.DataFrame()
tariffType14 = pd.DataFrame()
tariffTypeNDM = pd.DataFrame()
tariffTypeLLV = pd.DataFrame()
tariffTypeND5 = pd.DataFrame()
facilityIndex = pd.DataFrame()
timeOfUse = pd.DataFrame()

demandProfiles = pd.DataFrame()   

total_site_bill = 0
total_NEW_bill = 0

