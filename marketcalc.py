import pandas as pd;
import random;
import numpy as np;
import matplotlib.pyplot as plt;

DIVIDEND_TAX_RATE = 0.3;
def MonthYield( data, date_index, real_amnt_invested ):
    real_price = data[ 'Real Price' ][ date_index ].to_numpy();
    real_next_price = data[ 'Real Price' ][ date_index + 1 ].to_numpy();
    shares = real_amnt_invested / real_price;
    if ( np.min( shares ) < 0 ):
        shares = np.where( shares > 0, shares, np.zeros( shares.size ) )
    real_dividend = data[ 'Real Dividend' ][ date_index + 1 ].to_numpy() / 12;
    return shares * ( real_next_price - real_price + real_dividend * ( 1 - DIVIDEND_TAX_RATE ) );

def RandomPeriodYield( data, real_amnt_invested, monthly_contrib, months ):
    real_amnt = real_amnt_invested.copy();
    date_index = np.array( [ random.randint( 0, len( data[ 'Date' ] ) - 2 - 3 - months ) for _ in range( real_amnt_invested.size ) ] );
    for i in range( 0, months ):
        real_amnt += MonthYield( data, date_index + i, real_amnt ) + monthly_contrib;
    return real_amnt - real_amnt_invested;

NUM_SIMS = 10000;
INITIAL_VALUE = 0;
MONTHLY_CONTRIB = 100000;
SAMPLING_PERIOD = 12;
MONTHS_SIMULATED_ARR = np.arange( 1 * 12, 60 * 12, 12 );

data = pd.read_csv( 'ie_data.xls - Data.csv', quotechar='"' )

MONTHS_SIMULATED_MAX = MONTHS_SIMULATED_ARR[ -1 ];
sim_data = np.array( [ INITIAL_VALUE for _ in range( NUM_SIMS ) ], dtype=np.float64 );
sim_data.shape = (1,NUM_SIMS);
for i in range( int( MONTHS_SIMULATED_MAX / SAMPLING_PERIOD + 1 ) ):
    new_array = sim_data[ -1 ] + RandomPeriodYield( data, sim_data[ -1 ], MONTHLY_CONTRIB, months=SAMPLING_PERIOD );
    sim_data = np.vstack( (sim_data, new_array) );

if ( MONTHLY_CONTRIB < 0 ):
    MONTHLY_CONTRIB = 0;

subzero_probabilities = [];
subinit_probabilities = [];
means = [];
medians = [];
percentiles = [];
for MONTHS_SIMULATED in MONTHS_SIMULATED_ARR:
    index = int( MONTHS_SIMULATED / SAMPLING_PERIOD );
    means.append( np.mean( sim_data[ index ] ) );
    medians.append( np.median( sim_data[ index ] ) );

    percentiles.append( np.percentile( sim_data[ index ], np.arange( 0, 100, 1 ) ) );

    subzero = np.array( np.where( sim_data[ index ] < 0 ) );
    subzero_prob = subzero.size / NUM_SIMS;
    subinit = np.array( np.where( sim_data[ index ] < INITIAL_VALUE + MONTHLY_CONTRIB * MONTHS_SIMULATED ) );
    subinit_prob = subinit.size / NUM_SIMS;

    subzero_probabilities.append( subzero_prob );
    subinit_probabilities.append( subinit_prob );

    #plt.hist( sim_data[ index ], bins=300, density=True );
    #plt.axvline( x=INITIAL_VALUE + MONTHLY_CONTRIB * MONTHS_SIMULATED, color='orange' );
    #plt.axvline( x=0, color='red' );
    #plt.axvline( x=np.mean( sim_data[ -1 ] ), color='blue' );
    #plt.axvline( x=np.median( sim_data[ -1 ] ), color='green' );
    #plt.show();

subzero_probabilities = np.array( subzero_probabilities );
subinit_probabilities = np.array( subinit_probabilities );
percentiles = np.array( percentiles );

pb = plt.axes( (0.1, 0.1, 0.3, 0.8) );
pb.set_title( 'Probabilities' );
pb.plot( MONTHS_SIMULATED_ARR, subzero_probabilities, color='red', label='subzero' );
pb.plot( MONTHS_SIMULATED_ARR, subinit_probabilities, color='orange', label='sub initial value' );
pb.set_xlabel( "Months since start" );
pb.set_ylabel( "Probability" );
pb.legend();

ret = plt.axes( (0.6, 0.1, 0.3, 0.8) );
ret.set_title( 'Estimated Returns' );
ret.plot( MONTHS_SIMULATED_ARR, means, color='red', label='Mean Value' );
ret.plot( MONTHS_SIMULATED_ARR, medians, color='orange', label='Median Value' );
ret.fill_between( MONTHS_SIMULATED_ARR, percentiles[ :, 5 ], percentiles[ :, 95 ], alpha=0.2, color='b', label='90% range' );
ret.fill_between( MONTHS_SIMULATED_ARR, percentiles[ :, 25 ], percentiles[ :, 75 ], alpha=0.4, color='b', label='50% range' );
ret.fill_between( MONTHS_SIMULATED_ARR, percentiles[ :, 40 ], percentiles[ :, 60 ], alpha=0.6, color='b', label='20% range' );
ret.set_xlabel( "Months since start" );
ret.set_ylabel( "Value" );
ret.legend();

plt.show();