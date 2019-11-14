#! /bin/python

import csv
import os
import pprint
import pickle
import re
import timeit

import pandas as pd
import datetime as dt

from collections import Counter, namedtuple

#### Ghetto Script Control ####

# original counts and initial processing
getBasicCounts = False
pickleRaws = False
initialPreprocess = False
firstReprocess = True

# run shortening for development
shortRun = False
stopAfter = 1       #Keep > 0 to process files

# airport customization
Airport = "SLC"
selectedAirportsCsv = "SelectedAirports.csv"

#### Globals ####

# Basic counts
if getBasicCounts:
    countsOrigin = Counter()
    countsDest = Counter()
    countsLink = {}

# Processed Dataframe
ord_df = pd.DataFrame()
selectedAirports_df = pd.DataFrame()

# Does python support enums?
# Standardize date time feature names for each flight leg.
flightStagePoints = {
    'ActualArrival': ['ArriveDate', 'ArrTime'], 
    'ActualDepart': ['DepartDate', 'DepTime'], 
    'SchedArrival': ['ArriveDate', 'CSRArrTime'], 
    'SchedDepart': ['DepartDate', 'CSRArrTime']
}

def InitialBasicCounts(csvFile):
    with open(csvFile) as openfile:
        airport = {}
        reader = csv.reader(openfile)
        header = True
        for row in reader:
            if header:
                fcnt = 0
                for field in row:
                    if field in ("Origin", "Dest"):
                        #print("{} is field {}".format(field, fcnt))
                        airport[field] = fcnt
                    fcnt += 1
                header = False
            else:
                countsOrigin[row[airport["Origin"]]] += 1
                countsDest[row[airport["Dest"]]] += 1
                if row[airport["Origin"]] in countsLink.keys():
                    countsLink[row[airport["Origin"]]][row[airport["Dest"]]] += 1
                else:
                    countsLink[row[airport["Origin"]]] = Counter()
                    countsLink[row[airport["Origin"]]][row[airport["Dest"]]] += 1

def CsvToPickledDataframe(csvFile):
    print("processing: {}".format(os.path.join("./RawData/", csvFile)))
    tmpdf = pd.read_csv(os.path.join("./RawData/", csvFile), encoding="ISO-8859-1")

    basename, _ = os.path.splitext(csvFile)
    outname = basename + "pkl"
    outfile = open(os.path.join("./pickles/", outname),'wb')
    pickle.dump(tmpdf, outfile)
    outfile.close

def IntToTime(intIn):
    try:
        intIn = int(intIn)
        timeMask = re.compile('(\d{2})(\d{2})')
        timeStr = str(intIn).zfill(4)
        timeParts = timeMask.match(timeStr)
        timeOut = dt.time(int(timeParts[1]), int(timeParts[2]))
        return timeOut
    except:
        #pprint.pprint("This can not be cast as an integer: {}".format(intIn))
        pass
    else:
        return "NaN"

def IntOrNaN(value):
    try:
        return int(value)
    except:
        pass
    else:
        return "NaN"

def TimedeltaOrNaN(value):
    try:
        return(dt.timedelta(minutes=(int(value))))
    except:
        pass
    else:
        return "NaN"

def GetNextDay(today):
    tomorrow = today + dt.timedelta(days=1)
    return tomorrow

def GetArrivalDate(record):

    # Assume sameday arrival
    ArriveDate = record['DepartDate']

    # if the arrival time is earlier than the departure time then the arrival date is the day after the departure date
    if  type(record['ArrTime']) == dt.time and type(record['DepTime']) == dt.time:
        nextDayArrival = record['ArrTime'] < record['DepTime']
        if nextDayArrival: 
            ArriveDate = record['DepartDate'] + dt.timedelta(days=1)

    return ArriveDate

def MergeDateTime(record, flightStage):
    #print("Date: {} Time: {}".format(record[flightStage[0]], record[flightStage[1]]))

    if type(record[flightStage[0]]) != "Date":
        print("found an invalid date {} of type: {}".format(record[flightStage[0]], type(record[flightStage[0]])))
    if type(record[flightStage[1]]) != "Time":
        print("found an invalid time {} of type: {}".format(record[flightStage[1]], type(record[flightStage[1]])))
    return True
    #return dt.datetime.combine(record[flightStage[0]], record[flightStage[1]])

def PrepForTableau(original_df):

    # Make a copy of the dataframe to ensure we know what's being modified and included
    columnsToCopy = [ 
        ## Datetimes should be date times
        #"Year", "Month", "DayofMonth", 
        #"DepTime", "CRSDepTime", 
        #"ArrTime", "CRSArrTime", 
        
        ## Distances in integer miles
        #"Distance"
        
        ## Minutes are a form of timedelta
        #"TaxiIn", "TaxiOut", 
        #"ActualElapsedTime", "CRSElapsedTime", "AirTime", 
        #"CarrierDelay", "WeatherDelay", "NASDelay", "SecurityDelay", "LateAircraftDelay" 
        #"ArrDelay", "DepDelay"

        "DayOfWeek", 
        "Origin", "Dest", 
        "UniqueCarrier", "FlightNum", "TailNum", 
        "Cancelled", "CancellationCode", "Diverted", 
    ]
    #print("Straight Column Copy")
    preped_df = original_df[columnsToCopy].copy()

    # Calculating dates
    #print("Datetime Concatenation")
    preped_df['DepartDate'] = original_df.apply(lambda row: dt.date(row.Year, row.Month, row.DayofMonth), axis = 1)
    
    # Time is time
    clockTimes = ["DepTime", "CRSDepTime", "ArrTime", "CRSArrTime"]
    for ctime in clockTimes:
        #print("Converting {} to time".format(ctime))
        preped_df[ctime] = original_df.apply(lambda row: IntToTime(row[ctime]), axis = 1)

    # Distances are integer miles, not floats
    #print("Distances are whole numbers")
    preped_df['Distance'] = original_df.apply(lambda row: IntOrNaN(row['Distance']), axis = 1)

    # Timedeltas should be timedeltas
    measuredTimes = [
        "TaxiIn", "TaxiOut", "ActualElapsedTime", "CRSElapsedTime", "AirTime", "CarrierDelay", "WeatherDelay", 
        "NASDelay", "SecurityDelay", "LateAircraftDelay", "ArrDelay", "DepDelay" ]
    for mtime in measuredTimes:
        #print("Converting {} to timepart".format(mtime))
        preped_df[mtime] = original_df.apply(lambda row: TimedeltaOrNaN(row[mtime]), axis = 1)

    #print("Same or next day arrival")
    preped_df['ArriveDate'] = preped_df.apply(lambda row: GetArrivalDate(row), axis = 1)

    return preped_df

if pickleRaws | getBasicCounts:
    for csvFile in os.listdir("./RawData"):

        if pickleRaws:
            CsvToPickledDataframe(csvFile)
        
        if getBasicCounts:
            InitialBasicCounts(os.path.join("./RawData/", csvFile))
            #pprint.pprint(countsLink)
            #pprint.pprint(countsOrigin.most_common(10))
            #pprint.pprint(countsDest.most_common(10))
            print("Salt Lake City had: {} flights leave.".format(countsOrigin['SLC']))
            print("Salt Lake City had: {} flights arrive.".format(countsDest['SLC']))
            print("ord had: {} flights leave.".format(countsOrigin['ORD']))
            print("ord had: {} flights arrive.".format(countsDest['ORD']))
            print("{} flights from SLC went to ORD".format(countsLink['SLC']['ORD']))
            print("{} flights from ORD went to SLC".format(countsLink['ORD']['SLC']))

if initialPreprocess: 
    for pickled in os.listdir("./pickles"):
        # Orlando specific. Saved for posterity
        if (False):
            print("Processing: {}".format(pickled))
            tmp_df = pd.read_pickle(os.path.join("./pickles/", pickled))
            to_ord = tmp_df['Dest'] == "ORD"
            from_ord = tmp_df['Origin'] == "ORD"
            ord_df = pd.concat([ord_df, tmp_df[to_ord | from_ord]], sort=True)
            
        # Preprocess for selected airports
        if (stopAfter > 0):
            if shortRun: stopAfter -= 1

            print("Processing: {}".format(pickled))

            tmp_df = pd.read_pickle(os.path.join("./pickles/", pickled))
            dest_port = tmp_df['Dest'] == Airport
            from_port = tmp_df['Origin'] == Airport
            processed_df = PrepForTableau(tmp_df.loc[dest_port | from_port].copy())
            #pprint.pprint(processed_df)
            selectedAirports_df = pd.concat([selectedAirports_df, processed_df], sort=True)
        else: break

    # Orlando
    #pprint.pprint(ord_df)
    #pprint.pprint(ord_df.describe())
    #ord_df.to_csv("Orlando.csv")

    # Selected Airports
    pprint.pprint(selectedAirports_df)
    pprint.pprint(selectedAirports_df.describe())
    selectedAirports_df.to_csv("SelectedAirports.csv")

if firstReprocess:
    reloaded_df = pd.read_csv(selectedAirportsCsv, encoding="ISO-8859-1", low_memory=False)
    reprocessed_df = pd.DataFrame()

    # Drop the unnamed column of index numbers from previous dataframes
    #reloaded_df = reloaded_df.drop(reloaded_df.columns[0], axis=1)

    for flightStage in flightStagePoints.keys():
        #pprint.pprint(flightStagePoints[flightStage])
        #print("{} has fields {}".format(flightStage, flightStagePoints[flightStage]))
        reprocessed_df[flightStage] = reloaded_df.apply(lambda row: MergeDateTime(row, flightStagePoints[flightStage]), axis = 1)


    pprint.pprint(reprocessed_df)