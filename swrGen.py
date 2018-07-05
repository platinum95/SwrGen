#!/usr/bin/env python3

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import csv
import argparse
import sys


parser = argparse.ArgumentParser( description='Get SWR from given spectral analysis.' )
parser.add_argument( 'baselineFilePath', type=str, 
                     action='store', 
                     help='The baseline CSV file' )
parser.add_argument( 'dutFilePath', type=str,
                      action='store', 
                     help='The DUT csv file' )
parser.add_argument( '-o', '--output', type=str,
                     action='store',
                     help='File to place the output' )
args = parser.parse_args()

def extractCsvData( filePath ):
    '''
    Take a file path to a CSV file of measured frequencies and power.
    We assume column 0 has the frequency, and column 1 has the power,
    along with row 0 being column names.
    Return a tuple of lists of frequency data and power.
    '''
    with open( filePath, 'r' ) as csvFile:
        csvReader = csv.reader( csvFile )
        freqData, dbData = map( list, zip( *csvReader ) )
        freqDataInt = [ int( val ) for val in freqData[ 1 : ] ]
        dbDataFloat = [ float( val ) for val in dbData[ 1 : ] ]
        return ( freqDataInt, np.asarray( dbDataFloat ) )
    # Shouldn't get here
    return ( None, None )

# Extract the data from the CSV files
( baseFreq, basePower ) = extractCsvData( args.baselineFilePath )
( dutFreq, dutPower ) = extractCsvData( args.dutFilePath )

# Make sure we're dealing with the same frequency range
assert baseFreq == dutFreq

# Get the Return Loss (baseline - dut power)
returnLoss = np.subtract( basePower, dutPower )

# Check for negative values (bad measurements)
if( np.amin( returnLoss ) < 0 ):
    print( "WARNING: Negative values in return loss, which means " +
           "some DUT power values are higher than the corresponding " +
           "baseline values.\nI'll try to minimise the impact," +
           "but ideally you should try taking a more accurate" +
           "measurement." )
    rlMean = np.average( [ x for x in returnLoss if x > 0.2 ] )
    # Get the smalled positive value, for adjusting the negative values
    for idx, val in enumerate( returnLoss ):
        if val < 0.2:
            returnLoss[ idx ] = 1000

# Calculate the SWR
swr = np.zeros( len( returnLoss ) )
for i, val in enumerate( returnLoss ):
    powVal = pow( 10.0, val / 20.0 )
    swr[ i ] = ( powVal + 1.0 ) / ( powVal - 1.0 )


fig, ax = plt.subplots()
fmt = [ ( x / 1e6 ) for x in baseFreq ]
ax.plot( fmt, swr )
ax.grid()
# Major ticks every 20, minor ticks every 5
fMin = np.amin( fmt )
fMax = np.amax( fmt )
major_ticks = np.arange(fMin, fMax, 20)
minor_ticks = np.arange(fMin, fMax, 5)

ax.set_xticks(major_ticks)
ax.set_xticks(minor_ticks, minor=True)

ax.set( xlabel='Frequency (MHz)', ylabel='SWR',
        title='SWR Analysis' )
if args.output:
    fig.savefig( args.output )
else:
    plt.show()


