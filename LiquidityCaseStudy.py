# -*- coding: utf-8 -*-
"""
@author: arora
"""
# Importing Modules.
import pandas as pd
import numpy as np
import datetime as dt
from dateutil import relativedelta as du

# Reading the Excel file
def ReadExcel(fileName, sheetName):
    '''Reads the given sheets from the Excel file and returns a dictionary of data frames with sheet name as Key'''    
    data = pd.read_excel(fileName, sheetname = sheetName)
    return data

# Tranche-level Projections for Liquidity date 
def Projections(data, dateRequested):
    '''Takes dictionary of Data and Requested Date as inputs and returns dataframe with Liquidation Dates and other information.'''
    
    # Creating separate dataframes for Fund Terms and Tranche Invesment Data.    
    fundTerms = pd.DataFrame(data['Fund Terms'])
    trancheInvestment = pd.DataFrame(data['Tranche Investment Data'])
    
    # Replacing NaN in the Gate with 1 (100%).
    fundTerms['Gate'].replace(np.nan, 1, inplace = True)
    
    # Creating Lists for Monthly, Quarterly, Semiannual and Annual Redemption Dates    
    startDate = dt.datetime(dateRequested.year,01,31)
    monthList = [startDate + du.relativedelta(months = i) for i in range(12)]
    quarterList = [startDate + du.relativedelta(months = (i*3)-1) for i in range(1,5)]
    semiannualList = [startDate + du.relativedelta(months = (i*6)-1) for i in range(1,3)]
    annualList = [startDate + du.relativedelta(months = (i*12)-1) for i in range(1,2)]
    
    # Creating empty list to store Liquidation Dates
    dateLiquidation = []    
    
    # Looping thorugh each entry in Tranche Investment Data
    for investment in trancheInvestment.values:
        
        # Reading values of Tranche Investement Data for each Fund.        
        fund, dateInvestment, amount = investment    
        
        # Extracting the Fund Terms for the particular fund.
        rFrequency, sPeriod, gate, lockup = fundTerms[fundTerms['Fund Name'] == fund].values[0][1:]
                
        # Preparing Redemption Date List respective to Fund
        if rFrequency == 'Monthly':
            datesRedemption = list(monthList)
            months = 1
        elif rFrequency == 'Quarterly':
            datesRedemption = list(quarterList)
            months = 3
        elif rFrequency == 'Semiannual':
            datesRedemption = list(semiannualList)
            months = 6
        elif rFrequency == 'Annual':
            datesRedemption = list(annualList)
            months = 12    
        
        # Setting the Request date to closest Redemption Date in future.
        for date in datesRedemption:
            if date >= dateRequested:
                dateRequested = date
                break
            else: continue
        
        dateFinal = np.nan
        # Lockup Period Check
        if dateInvestment + du.relativedelta(months = lockup) < dateRequested:
            
            # Setting the Liquidation date as Redemption date.            
            dateFinal = dateRequested
            
            # Gate value check. If not 100% then increase the liquation time.            
            if gate != 1:
                dateFinal += du.relativedelta(months = months * int(np.floor(1/gate - 1))) + du.relativedelta(days = int(sPeriod))
            else:
                dateFinal = dateRequested + du.relativedelta(days = int(sPeriod))
        dateLiquidation.append(dateFinal)
    trancheInvestment['Liquidation Date'] = dateLiquidation
    return trancheInvestment


# Function to calculate Weighted Average Time to Liquidation.
def WATL(df):
    '''Take the Liquidation DataFrame as input and returns a dataframe with Weighted Average Time to Liquidation.'''    
    
    # Calculating the portion of Portfolio formed from the respective fund.
    ratio = (df['Net Asset Value']) / float(sum(df['Net Asset Value']))
    
    # Calculating Weighted Average Time for Liquidation by multiplying ratio with "Time left in Liquidation" 
    df['WATL'] = ratio * (df['Liquidation Date'] - dateRequested)
    
    return df

# Starting Point.
if __name__ == "__main__":
    # File name and sheet names
    fileName = "MIO_Liquidity_Model_Case.xlsx"
    sheetName = ["Fund Terms", "Tranche Investment Data"]
    
    # Reading Data from Excel File.
    data = ReadExcel(fileName, sheetName)
    
    # Enter the Request Date.    
    dateRequested = dt.datetime(2017, 05, 31)
    
    # DataFrame containing Liquidation Dates.
    df = Projections(data, dateRequested)
    print "\nTranche-Level Projections\n\n", df
    
    # Calculating Weighted Average Time to Liquidation
    df = WATL(df)
        
    # Weighted Average time to Liquidity of the entire Portfolio (in days)   
    PortfolioWATL = df['WATL'].sum()
    print "\nWeighted Average Time to Liquidation for Portfolio:", PortfolioWATL
    
    # Weighted Average time to Liquidity of the entire Portfolio (in days)
    FundWATL = df[['Fund Name', 'WATL']].groupby('Fund Name').sum()
    print "\nWeighted Average Time to Liquidation by Fund:\n\n", FundWATL

    # Creating Graph for Funds Received over time.
    FundsGraph = df[['Fund Name', 'Liquidation Date', 'Net Asset Value']].groupby('Fund Name').max()
    FundsGraph = FundsGraph.dropna()
    FundsGraph = FundsGraph.sort_values(['Liquidation Date'])    
    FundsGraph['Cumulative Sum'] = FundsGraph['Net Asset Value'].cumsum()
    FundsGraph.plot(x='Liquidation Date', y='Cumulative Sum', label = 'Funds Received over time')