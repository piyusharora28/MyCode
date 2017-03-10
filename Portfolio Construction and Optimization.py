# -*- coding: utf-8 -*-
"""
Created on Thu Dec 01 12:42:38 2016

@author: arora
"""

# Packages.
import quandl as qd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import solve
import scipy.stats
from quadprog import solve_qp

# Setting up Quandl API key.
qd.ApiConfig.api_key = 'srQzVHv4VDymwk8Bxq-P'

start = "2016-01-01"
end = "2016-10-31"

marketCode = 'YAHOO/INDEX_DJI'
tickerCodes = list(pd.read_csv('dowjonesA.csv')['premium_code'])
tickerCodes.append(marketCode)

dataset = qd.get(tickerCodes, column_index = 4, returns = "pandas", start_date = start, end_date = end)
dataset.columns = [ticker.split('/')[1] for ticker in tickerCodes]

returnDataset = (dataset - dataset.shift(1)) * 100 / dataset.shift(1)

#covarianceMatrix = np.zeros((len(returnDataset.columns) - 1, len(returnDataset.columns) - 1))
#for i in range(len(returnDataset.columns) - 1):
#    for j in range(len(returnDataset.columns) - 1):
#        covarianceMatrix[i, j] = np.cov(returnDataset.iloc[1:,i], returnDataset.iloc[1:,j])[0,1]
#
#portfolioReturn = list()
#portfolioRisk = list()
#
#for w1 in np.linspace(0,1,100):
#    w2 = 1 - w1
#    rtn = w1 * np.mean(returnDataset['AAPL']) + w2 * np.mean(returnDataset['IBM']) * 252
#    rsk = ((w1 * np.std(returnDataset['AAPL']))**2 + (w2 * np.std(returnDataset['IBM']))**2 + 2 * w1 * w2 * np.cov(returnDataset['AAPL'][1:,], returnDataset['IBM'][1:,])[0,1]) * np.sqrt(252)
#    portfolioReturn.append(rtn)
#    portfolioRisk.append(rsk)
#
#plt.plot(portfolioRisk, portfolioReturn)


## solving for weights
#Er = np.array(np.mean(returnDataset.iloc[:,:30]))
#one = np.array(np.repeat(1, 30, axis = 0))
#M = np.hstack((covarianceMatrix, Er.reshape((30,1)), one.reshape((30,1))))
#M = np.vstack((M,np.hstack((Er,0,0)), np.hstack((one, 0, 0))))
#b = np.repeat(0, 30, axis = 0).reshape(30,1)
#b = np.vstack((b, 0.05, 1))
#weights = solve(M, b)[:30]

#np.dot(Er, weights)

# Mean Return (Annualized) and Risk of Securities.
meanReturn = np.array(np.mean(returnDataset)) * 252
sdReturn = np.array(np.std(returnDataset.iloc[:, :30]))

# Single Index Model
beta = list()
alpha = list()
omega = list()
N = len(returnDataset.columns) - 1
for x in range(N):
    regr = scipy.stats.mstats.linregress(x = returnDataset['INDEX_DJI'][1:,].to_frame(),y = returnDataset.iloc[1:, x].to_frame())
    beta.append(regr[0])
    alpha.append(regr[1])
    omega.append(regr[4])

varMarket = np.var(returnDataset['INDEX_DJI'])

# Covariance Matrix (Annualized)
covarianceMatrixSIM = (np.dot((np.array(beta) * varMarket).reshape(N,1), np.array(beta).reshape((1,N))) + np.diag(np.array(omega)**2)) * 252

# Evaluating weights using quadratic programming.
one = np.array(np.repeat(1, N))
tau = 2.0
lowerBound = np.array(np.repeat(-0.05, N))
upperBound = np.array(np.repeat(0.05, N))
I = np.eye(N)
A = np.hstack((one.reshape((N,1)), I, -I))
b = np.hstack((1, lowerBound, -upperBound))
me = 1
weightsSIM = solve_qp(covarianceMatrixSIM, meanReturn[0:N] * tau, A, b, meq = me)[0]

portfolioReturnSIM = np.dot(weightsSIM, meanReturn[0:N].reshape(N))
portfolioRiskSIM = np.sqrt(np.dot(np.dot(weightsSIM, covarianceMatrixSIM), weightsSIM))
sharpeRatioSIM = portfolioReturnSIM/portfolioRiskSIM

print "SIM Portfolio Return :", portfolioReturnSIM
print "SIM Portfolio Risk :", portfolioRiskSIM
print "SIM Sharpe Ratio :", sharpeRatioSIM

# Constant Correlation Model
correlation = np.ndarray((N,N))
for x in range(N):
    for y in range(N):
        correlation[x, y] = np.corrcoef(returnDataset.iloc[1:, x], returnDataset.iloc[1:, y])[0,1]

rho = np.mean(correlation)
covarianceMatrixCCR = np.ndarray((N,N))
for x in range(len(sdReturn)):
    for y in range(len(sdReturn)):
        if x == y:
            covarianceMatrixCCR[x, y] = sdReturn[x] * sdReturn[y]
        else:
            covarianceMatrixCCR[x, y] = sdReturn[x] * sdReturn[y] * rho

# Covariance Matrix.
covarianceMatrixCCR = covarianceMatrixCCR * 252
one = np.array(np.repeat(1, N))
tau = 2.0
lowerBound = np.array(np.repeat(-0.05, N))
upperBound = np.array(np.repeat(0.05, N))
I = np.eye(N)
A = np.hstack((one.reshape((N,1)), I, -I))
b = np.hstack((1, lowerBound, -upperBound))
me = 1
weightsCCR = solve_qp(covarianceMatrixCCR, meanReturn[0:N] * tau, A, b, meq = me)[0]

portfolioReturnCCR = np.dot(weightsCCR, meanReturn[0:N].reshape(N))
portfolioRiskCCR = np.sqrt(np.dot(np.dot(weightsCCR, covarianceMatrixCCR), weightsCCR))
sharpeRatioCCR = portfolioReturnCCR/portfolioRiskCCR

print "CCR Portfolio Return :", portfolioReturnCCR
print "CCR Portfolio Risk :", portfolioRiskCCR
print "CCR Sharpe Ratio :", sharpeRatioCCR

# Creating Portfolios with $1 million
capital = 1000000
start = "2016-11-01" 
end = "2016-12-10"
priceDataset =  qd.get(tickerCodes, column_index = 4, returns = "pandas", start_date = start, end_date = end)
priceDataset.columns = dataset.columns

# Market Return in the given time period
marketReturnDaily = (priceDataset.iloc[:, 30] - priceDataset.iloc[:, 30].shift(1)) * 100 / priceDataset.iloc[:, 30].shift(1)
marketReturnDaily.index = priceDataset.index

# Portfolio 1: Single Index Model.
weightsSIM = pd.Series(weightsSIM, index = priceDataset.columns[:30])
stocksSIM = (weightsSIM * capital) / (priceDataset.iloc[0, :30])

# Rounding the number of stocks. 
stocksSIM[stocksSIM > 0.0] = np.floor(stocksSIM)
stocksSIM[stocksSIM < 0.0] = np.ceil(stocksSIM)

investmentInitial = sum(stocksSIM * (priceDataset.iloc[0, :30]))
cash = capital - investmentInitial

investmentFinal = sum(stocksSIM * (priceDataset.iloc[len(priceDataset) - 1, :30]))

# Holding Period Return of the Portfolio.
SIMPortfolioHPR =  (investmentFinal - investmentInitial) * 100 / investmentInitial

# Daily Return of the Portfolio
dailyValues = np.apply_along_axis(sum,1,(stocksSIM * (priceDataset.iloc[:, :30])))
dailyValues = pd.DataFrame(dailyValues, columns = ['Daily Value'])

SIMPortfolioReturnDaily = (dailyValues - dailyValues.shift(1)) * 100 / dailyValues.shift(1)
SIMPortfolioReturnDaily.index = priceDataset.index

#Mean Return and Risk of the SIM Portfolio (Annualized).
meanReturnSIM = np.mean(SIMPortfolioReturnDaily) * 252
riskSIM = np.std(SIMPortfolioReturnDaily) * np.sqrt(252)
sharpeRatioSIM = meanReturnSIM / riskSIM

#plt.plot(SIMPortfolioReturnDaily)

# Portfolio 2: Constant Correlation Model.
weightsCCR = pd.Series(weightsCCR, index = priceDataset.columns[:30])
stocksCCR = (weightsCCR * capital) / (priceDataset.iloc[0, :30])

# Rounding the number of stocks. 
stocksCCR[stocksCCR > 0.0] = np.floor(stocksCCR)
stocksCCR[stocksCCR < 0.0] = np.ceil(stocksCCR)

investmentInitial = sum(stocksCCR * (priceDataset.iloc[0, :30]))
cash = capital - investmentInitial

investmentFinal = sum(stocksCCR * (priceDataset.iloc[len(priceDataset) - 1, :30]))

# Holding Period Return of the Portfolio.
CCRPortfolioHPR =  (investmentFinal - investmentInitial) * 100 / investmentInitial

# Daily Return of the Portfolio
dailyValues = np.apply_along_axis(sum,1,(stocksCCR * (priceDataset.iloc[:, :30])))
dailyValues = pd.DataFrame(dailyValues, columns = ['Daily Value'])

CCRPortfolioReturnDaily = (dailyValues - dailyValues.shift(1)) * 100 / dailyValues.shift(1)
CCRPortfolioReturnDaily.index = priceDataset.index

#Mean Return and Risk of the CCR Portfolio (Annualized).
meanReturnCCR = np.mean(CCRPortfolioReturnDaily) * 252
riskCCR = np.std(CCRPortfolioReturnDaily) * np.sqrt(252)
sharpeRatioCCR = meanReturnCCR / riskCCR

# Plotting the returns.
comparison = plt.figure()
plt.plot(SIMPortfolioReturnDaily, 'r', label = 'Single-Index')
plt.plot(CCRPortfolioReturnDaily, 'b', label = 'Constant Correlation')
plt.plot(marketReturnDaily, 'g')
plt.title("Comparison of Daily Returns")
plt.xlabel("Holding Period")
plt.ylabel("Daily Return")
plt.legend(loc = 'upper right')
plt.show()
comparison.savefig("Comparison.pdf")
plt.legend()
