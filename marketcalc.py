import pandas as pd;
import random;
import numpy as np;
import matplotlib.pyplot as plt;

## Standard Program Parameters ##
def GetAnnualSalaryPreTax( age ):
    if ( age > RETIREMENT_AGE ):
        return 0;

    if ( age < 20 ):
        return 24440;
    if ( age < 30 ):
        return 32292;
    if ( age < 40 ):
        return 39988;
    if ( age < 50 ):
        return 42796;
    if ( age < 60 ):
        return 40456;
    return 36036;
STARTING_AGE = 23;
RETIREMENT_AGE = 50;
INITIAL_VALUE = 0;
MONTHLY_EXPENSES = 1200;
################################


## Non-standard Program Parameters ##
NUM_SIMS = 10000;
SAMPLING_PERIOD = 12;
MONTHS_SIMULATED_ARR = np.arange( 1 * 12, 60 * 12, 12 );
DIVIDEND_TAX_RATE = 0.5;
CAPGAINS_TAX_RATE = 0.2;
STANDARD_TAX_RATE = 0.3;
#####################################


## Program ##
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


data = pd.read_csv( 'ie_data.xls - Data.csv', quotechar='"' )

MONTHS_SIMULATED_MAX = MONTHS_SIMULATED_ARR[ -1 ];
sim_data = np.array( [ INITIAL_VALUE for _ in range( NUM_SIMS ) ], dtype=np.float64 );
sim_data.shape = (1,NUM_SIMS);
total_contributions = [];
total_withdrawn = [];
for i in range( int( MONTHS_SIMULATED_MAX / SAMPLING_PERIOD + 1 ) ):
    last_contribution = 0;
    last_withdrawn = 0;
    if ( len( total_contributions ) > 0 ):
        last_contribution = total_contributions[ -1 ];
        last_withdrawn = total_withdrawn[ -1 ];
    
    monthly_contrib = GetAnnualSalaryPreTax( STARTING_AGE + i * SAMPLING_PERIOD / 12 ) / 12 * ( 1 - STANDARD_TAX_RATE ) - MONTHLY_EXPENSES;

    # calculate withdrawal from capital gains tax
    monthly_contrib_taxincl = monthly_contrib;
    monthly_withdrawal = 0;
    if ( monthly_contrib < 0 ):
        if ( last_contribution - last_withdrawn < 0 ):
            monthly_contrib_taxincl = ( 1 + CAPGAINS_TAX_RATE ) * monthly_contrib;
        elif ( last_contribution - last_withdrawn + monthly_contrib * SAMPLING_PERIOD < 0 ):
            cap_gains_taxable = ( last_contribution - last_withdrawn + monthly_contrib * SAMPLING_PERIOD ) / SAMPLING_PERIOD;
            monthly_contrib_taxincl = ( monthly_contrib - cap_gains_taxable ) + ( 1 + CAPGAINS_TAX_RATE ) * cap_gains_taxable;
        else:
            monthly_contrib_taxincl = monthly_contrib;
        monthly_withdrawal = -monthly_contrib_taxincl;

    new_array = sim_data[ -1 ] + RandomPeriodYield( data, sim_data[ -1 ], monthly_contrib_taxincl, months=SAMPLING_PERIOD );
    sim_data = np.vstack( (sim_data, new_array) );
    if ( monthly_contrib < 0 ):
        monthly_contrib = 0;
    total_contributions.append( last_contribution + SAMPLING_PERIOD * monthly_contrib );
    total_withdrawn.append( last_withdrawn + SAMPLING_PERIOD * monthly_withdrawal );


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
    subinit = np.array( np.where( sim_data[ index ] < INITIAL_VALUE + total_contributions[ index ] ) );
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
#############