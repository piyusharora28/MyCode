sd(c(5,8,12))
which.min(c(4,1,6))


# WHO
WHO = read.csv('WHO.csv')

# Structure of  data
str(WHO)

# summary of data
summary(WHO)

# subsetting
#WHO_Europe = WHO[WHO$Region == 'Europe', ]
WHO_Europe = subset(WHO, Region == 'Europe')
str(WHO_Europe)

# save this to a csv file.
write.csv(WHO_Europe, "WHO_Europe.csv")
f = ls()
rm("WHO_Europe")

# Scatter plot
WHO$Under15
summary(WHO$Under15)

WHO$Country[which.min(WHO$Under15)]

plot(WHO$GNI, WHO$FertilityRate)

Outlier = subset(WHO, GNI > 10000 & FertilityRate > 2.5)
Outlier
Outlier[c("Country", "FertilityRate", "GNI")]

# Histograam
hist(WHO$CellularSubscribers)

# Boxplots
boxplot(WHO$LifeExpectancy ~ WHO$Region)

#table
table(WHO$Region)

# Tapply
tapply(WHO$ChildMortality, WHO$Region, mean)


############################################################

# Nutrition Data
USDA = read.csv("USDA.csv")


# plotting
plot(USDA$Protein, USDA$TotalFat, xlab = 'Protein', ylab = 'Total Fat', main = 'Protein vs Total Fat', pch = '*')

# Hist
hist(USDA$VitaminC, xlab = 'Vitamin C (mg)', main = 'Histogram of Vitamin C levels', xlim = c(0, 100), breaks = 2000)


# Boxplots
boxplot(USDA$Sugar, main = 'Boxplot of Sugar Level', ylab = 'Sugar (gm)')


# Adding Variables to the data frame.
USDA$HighSodium = as.numeric(USDA$Sodium > mean(USDA$Sodium, na.rm = TRUE))
USDA$HighProtein = as.numeric(USDA$Protein > mean(USDA$Protein, na.rm = TRUE))
USDA$HighFat = as.numeric(USDA$TotalFat > mean(USDA$TotalFat, na.rm = TRUE))
USDA$HighCarbs = as.numeric(USDA$Carbohydrate > mean(USDA$Carbohydrate, na.rm = TRUE))

# table
table(USDA$HighSodium)
table(USDA$HighSodium, USDA$HighProtein)

#t-apply
tapply(X = USDA$Iron, INDEX = USDA$HighProtein, FUN = mean, na.rm = TRUE)
tapply(X = USDA$VitaminC, INDEX = USDA$HighCarbs, max, na.rm = TRUE)
tapply(X = USDA$VitaminC, INDEX = USDA$HighCarbs, summary, na.rm = TRUE)


# Weekly assignment
MVT = read.csv("mvtWeek1.csv")
str(MVT)
max(MVT$ID)
min(MVT$Beat)
sum(MVT$Arrest)
length(MVT$Arrest)
sum(MVT$LocationDescription == 'ALLEY')
MVT$Date[4634]
DateConvert = as.Date(strptime(MVT$Date, "%m/%d/%y %H:%M"))
summary(DateConvert)
median(DateConvert)
MVT$Month = months(DateConvert)
MVT$Weekday = weekdays(DateConvert)
MVT$Date = DateConvert

# table
which.min(table(MVT$Month))
which.max(table(MVT$Weekday))

table(MVT$Month, MVT$Arrest)

# histogram
hist(MVT$Date, breaks = 100)

#Boxplots of dates sorted by arrests
boxplot(MVT$Date ~ MVT$Arrest)

# Table
table(MVT$Year, MVT$Arrest)


sort(table(MVT$LocationDescription))


# subsetting
Top5 = subset(MVT, LocationDescription == 'STREET' | LocationDescription == 'PARKING LOT/GARAGE(NON.RESID.)' | LocationDescription == 'ALLEY' | LocationDescription == 'GAS STATION' | LocationDescription == 'DRIVEWAY - RESIDENTIAL')
nrow(Top5)

str(Top5)
Top5$LocationDescription = factor(Top5$LocationDescription)
str(Top5)

table(Top5$LocationDescription, Top5$Arrest)

table(Top5$LocationDescription, Top5$Weekday)


# Stock Dynamics Data
IBM <- data.frame(read.csv("IBMStock.csv"))
GE <- data.frame(read.csv("GEStock.csv"))
ProcterGamble <- data.frame(read.csv("ProcterGambleStock.csv"))
CocaCola <- data.frame(read.csv("CocaColaStock.csv"))
Boeing <- data.frame(read.csv("BoeingStock.csv"))

IBM$Date <- as.Date(IBM$Date, "%m/%d/%y")
GE$Date <- as.Date(GE$Date, "%m/%d/%y")
ProcterGamble$Date <- as.Date(ProcterGamble$Date, "%m/%d/%y")
CocaCola$Date <- as.Date(CocaCola$Date, "%m/%d/%y")
Boeing$Date <- as.Date(Boeing$Date, "%m/%d/%y")

nrow(Boeing)
str(Boeing)

summary(c(IBM, GE, ProcterGamble, CocaCola, Boeing))

summary(IBM)
summary(GE)
mean(IBM$StockPrice)
summary(CocaCola)
summary(Boeing)
sd(ProcterGamble$StockPrice)

# plotting
plot(x = CocaCola$Date, y = CocaCola$StockPrice, type = 'l', lwd = 2)
lines(x = ProcterGamble$Date, y = ProcterGamble$StockPrice, lwd = 2, col = 'red', lty = 2)
abline(v = as.Date(c("1983-03-01")), lwd = 2)

# plotting between 1995-2005
plot(CocaCola$Date[301:432], CocaCola$StockPrice[301:432], lwd = 2, type = 'l', ylim = c(0,210))
lines(IBM$Date[301:432], IBM$StockPrice[301:432], lwd = 2, col = 'red', lty = 2)
lines(Boeing$Date[301:432], Boeing$StockPrice[301:432], lwd = 2, col = 'green', lty = 3)
lines(GE$Date[301:432], GE$StockPrice[301:432], lwd = 2, col = 'blue', lty = 4)
lines(ProcterGamble$Date[301:432], ProcterGamble$StockPrice[301:432], lwd = 2, col = 'yellow', lty = 5)
abline(v = as.Date(c("2004-01-01", "2005-12-31")))

# tapply
tapply(IBM$StockPrice, months(IBM$Date), mean)
tapply(CocaCola$StockPrice, months(CocaCola$Date), mean)
tapply(GE$StockPrice, months(GE$Date), mean)


# Linear Regression
wine = read.csv("wine.csv")
model1 = lm(Price ~ HarvestRain + WinterRain, data = wine)
summary(model1)

model2 = lm(Price ~ WinterRain + AGST + HarvestRain + Age, data = wine)
summary(model2)

wineTest = read.csv("wine_test.csv")
wineTest

predictTest = predict(model2, newdata = wineTest, type = 'response')

# Baseball
Baseball = read.csv("baseball.csv")
Moneyball = subset(Baseball, Year < 2002)
str(Moneyball)
Moneyball$RD = Moneyball$RS - Moneyball$RA
moneyballReg = lm(W ~ RD, data = Moneyball)
summary(moneyballReg)

runsReg = lm(RS ~ OBP + SLG, data = Moneyball)
summary(runsReg)

runsAllowedReg = lm(RA ~ OOBP + OSLG, data = Moneyball)

# correlation between team ranks and wins
teamRank = c(1,2,3,3,4,4,4,4,5,5)
wins2012 = c(94, 88, 95, 88, 93, 94, 98, 97, 93, 94)
wins2013 = c(97, 97, 92, 93, 92, 96, 94, 96, 92, 90)

cor(teamRank, wins2012)
cor(teamRank, wins2013)



# NBA Data
NBA = read.csv("NBA_train.csv")
NBA_test = read.csv("NBA_test.csv")
str(NBA)

NBA$PTSdiff = NBA$PTS - NBA$oppPTS
plot(NBA$PTSdiff, NBA$W)

nbaReg = lm(W ~ PTSdiff, data = NBA)
summary(nbaReg)


# ClimateChange
Climate = read.csv("climate_change.csv")
str(Climate)
plot(Climate$Year, Climate$Temp)

train = Climate$Year <= 2006
Climate_train = Climate[train, ]
Climate_test = Climate[!train, ]

tempReg = lm(Temp ~ MEI + CO2 + CH4 + N2O + CFC.11 + CFC.12 + TSI + Aerosols, data = Climate_train)
summary(tempReg)
cor(Climate[,-c(1,2)])

tempReg1 = lm(Temp ~ MEI + N2O + TSI + Aerosols, data = Climate_train)
summary(tempReg1)
tempRegStep = step(tempReg)
summary(tempRegStep)

tempPrediction = predict(tempRegStep, newdata = Climate_test, type = 'response')

RSS = sum((tempPrediction - Climate_test$Temp)^2)
TSS = sum((mean(Climate_train$Temp) - Climate_test$Temp)^2)
R2 = 1 - RSS/TSS
