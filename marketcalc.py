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
MONTHLY_CONTRIB = 20000;
SAMPLING_PERIOD = 12;
MONTHS_SIMULATED_ARR = np.arange( 59 * 12, 60 * 12, 12 );

subzero_probabilities = [];
subinit_probabilities = [];
data = pd.read_csv( 'ie_data.xls - Data.csv', quotechar='"' )
for MONTHS_SIMULATED in MONTHS_SIMULATED_ARR:
    sim_data = np.array( [ INITIAL_VALUE for _ in range( NUM_SIMS ) ], dtype=np.float64 );
    sim_data.shape = (1,NUM_SIMS);
    for i in range( int( MONTHS_SIMULATED / SAMPLING_PERIOD ) ):
        new_array = sim_data[ -1 ] + RandomPeriodYield( data, sim_data[ -1 ], MONTHLY_CONTRIB, months=SAMPLING_PERIOD );
        sim_data = np.vstack( (sim_data, new_array) );

    print( f"mean: {np.mean( sim_data[ -1 ] )}" );
    print( f"median: {np.median( sim_data[ -1 ] )}" );

    if ( MONTHLY_CONTRIB < 0 ):
        MONTHLY_CONTRIB = 0;

    subzero = np.array( np.where( sim_data[ -1 ] <= 0 ) );
    subzero_prob = subzero.size / sim_data.shape[ 1 ];
    subinit = np.array( np.where( sim_data[ -1 ] <= INITIAL_VALUE + MONTHLY_CONTRIB * MONTHS_SIMULATED ) );
    subinit_prob = subinit.size / sim_data.shape[ 1 ];

    subzero_probabilities.append( subzero_prob );
    subinit_probabilities.append( subinit_prob );

    print( f"Hit zero probability: {subzero_prob*100}%" );
    print( f"Sub initial value probability: {subinit_prob*100}%" );
    
    plt.hist( sim_data[ -1 ], bins=300, density=True );
    plt.axvline( x=INITIAL_VALUE + MONTHLY_CONTRIB * MONTHS_SIMULATED, color='orange' );
    plt.axvline( x=0, color='red' );
    plt.axvline( x=np.mean( sim_data[ -1 ] ), color='blue' );
    plt.axvline( x=np.median( sim_data[ -1 ] ), color='green' );
    plt.show();

subzero_probabilities = np.array( subzero_probabilities );
subinit_probabilities = np.array( subinit_probabilities );

plt.plot( MONTHS_SIMULATED_ARR, subzero_probabilities, color='red' );
plt.plot( MONTHS_SIMULATED_ARR, subinit_probabilities, color='orange' );
plt.show();