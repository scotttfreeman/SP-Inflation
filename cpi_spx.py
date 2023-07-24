import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Import SPX data from excel
data_excel = pd.read_excel('spx_weekly.xlsx', index_col=0)

# List of dates to get indexed performance for
# cpi_peak_dates = ['1951-04-30', '1957-04-30','1960-04-30', '1970-02-28','1974-11-30', '1980-03-31', '1990-10-31', '2000-03-31', '2008-07-31', '2011-09-30', '2022-06-30']
cpi_peak_dates_weekly = ['1951-04-27', '1957-04-26','1960-04-29', '1970-02-27','1974-11-29', '1980-03-28', '1990-10-26', '2000-03-31', '2008-07-25', '2011-09-30', '2022-06-24']

def calculate_indexed_performance(df, id, target_dates, pre_weeks=30, post_weeks=100):
    # Create an empty DataFrame to store the indexed performances
    indexed_df = pd.DataFrame()
    
    for date in target_dates:
        # Get the location of the target date in the DataFrame
        date_loc = df.index.get_loc(date)
       
        # Calculate start and end locations
        start_loc = max(0, date_loc - post_weeks)
        end_loc = min(len(df.index) - 1, date_loc + pre_weeks)
       
        # Select the rows before and after target date
        sliced_df = df.iloc[start_loc:end_loc+1][id]
        
        # Reverse the slice
        sliced_df = sliced_df[::-1]

        # Skip if there is no data in the range
        if sliced_df.empty:
            print(f"No data available for date {date}. Skipping...")
            continue  
       
        # Create new index representing weeks relative to the target date
        new_index = np.arange(-pre_weeks, len(sliced_df)-pre_weeks)
        sliced_df.index = new_index
       
        # Index to 100
        indexed_sliced_df = sliced_df / sliced_df.loc[0] * 100

        # Store the indexed performance in the DataFrame
        indexed_df = pd.concat([indexed_df, indexed_sliced_df], axis=1)
    
    # Name the columns after the target dates
    indexed_df.columns = target_dates
    
    return indexed_df

indexed_df = calculate_indexed_performance(data_excel, 'spx', cpi_peak_dates_weekly)
indexed_df['Average'] = np.mean(indexed_df.iloc[:,:-1],axis=1)
# indexed_df.to_excel('indexed_df.xlsx')

# plot data
plot_df = pd.concat([indexed_df['2022-06-24'], indexed_df['Average']], axis=1)
ax = plot_df.plot()
lines = ax.get_lines() # set line color, width
for line in lines:
    if line.get_label() == '2022-06-24':
        line.set_linewidth(2.5)
        line.set_color('#09A56C')
    if line.get_label() == 'Average':
        line.set_linewidth(2.5)
        line.set_color('#000000')

ax.axvline(x=0, color='black', linestyle='--') # Add a black dotted vertical line at the 0 x-axis value
ax.legend(['Current (Peak Inflation June 2022)', 'Historical Average', 'Peak Inflation'])
plt.title('S&P 500 vs Average Peak in Inflation (1950-Present)', fontweight='bold')
plt.xlabel('Weeks from Peak Inflation')
plt.ylabel('Indexed to 100 (0 weeks = 100)')
plt.show()