options nonotes nosource nosource2 errors=0;
/**options notes source source2 errors=20;**/
%let libref=C:\Users\piyus\Documents\Study\FE517\Final Project;
LIBNAME project "&libref";


/** Importing the file with the Intraday Data **/
PROC IMPORT DATAFILE = "&libref\minbar1.csv" DBMS=CSV OUT = project.minbar replace;
RUN;

/** Sorting the Data by the Symbol **/
PROC SORT DATA = project.minbar ;
BY _RIC;
FORMAT Date_G_ mmddyy10.;
RUN;


/** Macro for Creating Dataset of the particular Symbol **/
/** This Macro calls 2 macros which are used to calculate RSI and Returns **/
%MACRO createDataset(stock= ,dataset=);
DATA project.&dataset ;
SET project.minbar;
IF _RIC="&stock" THEN OUTPUT project.&dataset;
RUN;

/** Invoking other Macros **/
%calculateRSI(dataset=&dataset);
%calculateReturns(dataset=&dataset, stock=&stock);
%MEND;

/** Macro for Calculating RSI **/
%MACRO calculateRSI(dataset=);
DATA project.&dataset;
SET project.&dataset;
BY _RIC;

RETAIN counter 0;
counter+1;

IF first._RIC THEN DO;
counter=1;
END;

lastPrice = LAG(Last);
IF Last>lastPrice THEN DO;
Gain = Last-lastPrice;
END;

IF Last<lastPrice THEN DO;
Loss = lastPrice-Last;
END;

IF Gain=. THEN Gain=0;
IF Loss=. THEN Loss=0;

RETAIN sumGain 0;
sumGain = sumGain + Gain;
RETAIN sumLoss 0;
sumLoss = sumLoss + Loss;

IF counter=16 THEN DO;
AvgGain=(sumGain-Gain)/14;
AvgLoss=(sumLoss-Loss)/14;
RS=AvgGain/AvgLoss;
RSI=100-(100/(1+RS));
END;

DROP sumGain sumLoss;
RUN;

PROC SQL NOPRINT;
SELECT COUNT(*) INTO :totalObs FROM project.&dataset; 
QUIT;

%DO i= 17 %TO (&totalObs);	/** runs till the last observation **/
DATA project.&dataset;
SET project.&dataset;

lastAvgGain = Lag(AvgGain); 
lastAvgLoss = Lag(AvgLoss);

IF counter =&i THEN DO;
AvgGain = (lastAvgGain*13+gain)/14;
AvgLoss = (lastAvgLoss*13+loss)/14;
RS=AvgGain/AvgLoss;
RSI=100-(100/(1+RS));		/** formula for RSI **/
END;
RUN;
%END;
%MEND;

/** Macro for calculating Return for closed positions **/
%MACRO calculateReturns(dataset=, stock=);
DATA project.&dataset;
SET project.&dataset;
BY _RIC;

RETAIN Position 0;
RETAIN price 0;

/** Range used for RSI is 30 and 70 **/
IF RSI<30 AND RSI ~=. AND Position=0 THEN DO;	/** 0 means position is open **/
price=Last;										/** 1 means position is closed **/				
Position=1;
END;

IF RSI>70 AND RSI~=. AND Position=1 THEN DO;
Position = 0;
Return=(Last/price)-1;	/** Calculating return**/
END;
RUN;

/** Calculating Mean Return and Standard Deviation **/
PROC MEANS DATA = project.&dataset;
VAR Return;
TITLE "Analysis for &stock";
RUN;
%MEND;

/** Invoking the Main Macro for each Symbol **/
%createDataset(stock=AAPL.OQ,dataset=apple);
%createDataset(stock=CSCO.OQ,dataset=cisco);
%createDataset(stock=AXP.N,dataset=axp);
%createDataset(stock=BA.N,dataset=ba);
%createDataset(stock=CAT.N,dataset=cat);
%createDataset(stock=CVX.N,dataset=cvx);
%createDataset(stock=DD.N,dataset=dd);
%createDataset(stock=DIS.N,dataset=dis);
%createDataset(stock=GE.N,dataset=ge);
%createDataset(stock=GS.N,dataset=gs);
%createDataset(stock=HD.N,dataset=hd);
%createDataset(stock=IBM.N,dataset=ibm);
%createDataset(stock=JNJ.N,dataset=jnj);
%createDataset(stock=JPM.N,dataset=jpm);
%createDataset(stock=KO.N,dataset=ko);
%createDataset(stock=MCD.N,dataset=mcd);
%createDataset(stock=MMM.N,dataset=mmm);
%createDataset(stock=INTC.OQ,dataset=intc);
%createDataset(stock=MSFT.OQ,dataset=msft);
%createDataset(stock=MRK.N,dataset=mrk);
%createDataset(stock=NKE.N,dataset=nke);
%createDataset(stock=PFE.N,dataset=pfe);
%createDataset(stock=PG.N,dataset=pg);
%createDataset(stock=UNH.N,dataset=unh);
%createDataset(stock=UTX.N,dataset=utx);
%createDataset(stock=V.N,dataset=v);
%createDataset(stock=VZ.N,dataset=vz);
%createDataset(stock=WMT.N,dataset=wmt);
%createDataset(stock=XOM.N,dataset=xom);
%createDataset(stock=TRV.N,dataset=trv);
