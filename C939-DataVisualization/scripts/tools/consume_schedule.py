#!/usr/bin/python

import csv
import datetime as dt
def consume_schedule_csv(csvFile):
    '''
        Perform minimal data preparation on raw csv files for loading to mongodb
    '''
    rawSchedule = []
    with csv.DictReader(open(csvFile, 'r')) as reader:
        for row in reader:
            record = {
                'BaseDate': dt.datetime(year = int(row['Year']), month = int(row['Month']), day = int(row['DayofMonth'])),
                'DepartTime_Sched_localTZ': row['CRSDepTime'],
                'ArriveTime_Sched_localTZ': row['CRSArrTime'],
                'TravelTime_Sched': row['CRSElapsedTime'],
                'DepartTime_Actual_localTZ': row['DepTime'],
                'ArriveTime_Actual_localTZ': row['ArrTime'],
                'TravelTime_Actual': row['ActualElapsedTime'],
                'Carrier': row['UniqueCarrier'],
                'Number_Flight': row['FlightNum'],
                'Number_Tail': row['TailNum'],
                'Airport_Origin': row['Origin'],
                'Airport_Destination': row['Dest'],
                'TaxiTime_In': row['TaxiIn'],
                'TaxiTime_Out': row['TaxiOut'],
                'Cancelled': row['Cancelled'],
                'CancelCode': row['CancellationCode'],
                'Diverted': row['Diverted'],
                'DelayTime_Arrival': row['ArrDelayTime'],
                'DelayTime_Depart': row['DepDelayTime'],
                'DelayTime_Carrier': row['CarrierDelayTime'],
                'DelayTime_Weather': row['WeatherDelayTime'],
                'DelayTime_NAS': row['NASDelayTime'],
                'DelayTime_Security': row['SecurityDelayTime'],
                'DelayTime_LateAircraft': row['LateAircraftDelayTime']
            }
        rawSchedule.append(record)

    return rawSchedule