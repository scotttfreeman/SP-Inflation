import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# Import SPX data from excel
data_excel = pd.read_excel('infl_rec.xlsx', index_col=0)

recession_start_high_infla = ['1948-12-31','1953-08-31','1970-01-31','1973-12-31','1980-02-29','1981-08-31']
recession_start_low_infla = ['1957-09-30','1960-05-31','1990-08-31','2001-04-30','2008-01-31']
recession_start_future = ['2024-03-31']

# Ensure that 'date' is in datetime format
data_excel.index = pd.to_datetime(data_excel.index)

def calculate_indexed(df, anchor_date, months=24):
    anchor_value = df.loc[anchor_date]
    start_date = max(anchor_date - pd.DateOffset(months=months), df.index.min())
    end_date = min(anchor_date + pd.DateOffset(months=months), df.index.max())
    period_data = df.loc[start_date:end_date]
    indexed_data = period_data / anchor_value * 100

    # compute the relative month index
    month_index = list(range(-months, months+1)) if end_date == anchor_date else list(range(-months, len(period_data)-months))
    indexed_data.index = month_index

    return indexed_data
def calculate_indexed_future(df, future_date, high_infla_dates, months=24):
    # Calculate average indexed values during high inflation recession periods
    high_infla_data = pd.concat([calculate_indexed(df, pd.to_datetime(date)) for date in high_infla_dates])
    avg_indexed_high_infla = high_infla_data.groupby(high_infla_data.index).mean()
    avg_indexed_high_infla.index = avg_indexed_high_infla.index.astype(int)
    avg_indexed_high_infla = avg_indexed_high_infla.iloc[::-1]  # Reverse your DataFrame

    # Calculate number of months from last available data to future recession start
    last_date = df.index.max()
    months_to_future = (future_date.year - last_date.year) * 12 + (future_date.month - last_date.month)

    # Get the relevant part of the average indexed values that aligns with the future recession period
    relevant_avg_indexed = avg_indexed_high_infla.loc[0:-months_to_future].copy()

    # Calcualte rate of change on indexed values
    rate_of_change = relevant_avg_indexed.iloc[::-1].pct_change().iloc[::-1]
    rate_of_change = rate_of_change.dropna()

    # print(rate_of_change)
    last_data_value = df.iloc[-1].reset_index(drop=True)
    # print(last_data_value)
    last_data_value = pd.DataFrame([df.iloc[-1]])
    # print(last_data_value)
    future_index_values = pd.DataFrame(columns=df.columns)

    for _, roc in rate_of_change.iloc[::-1].iterrows():
        # print(roc)
        last_data_value = last_data_value * (1 + roc)
        print(last_data_value)
        future_index_values = pd.concat([future_index_values, last_data_value])

    # Reset the index after the concatenation
    future_index_values.reset_index(drop=True, inplace=True)
    # print(future_index_values)
    
    # # Change the way you create your future_df DataFrame:
    future_index_values.index = range(-months_to_future+1, 1)
    # print(future_index_values)

    # Adjusted the indices here
    past_data = df.iloc[-(months-months_to_future):].copy()
    past_data.index = range(-months+1, -months_to_future+1)  # create the corresponding negative index
    # print(past_data)

    # Concatenate past_data and future_index_values
    indexed_data = pd.concat([past_data, future_index_values])

    # Normalize the indexed_data to 100 at 'future_date'
    indexed_data = indexed_data / indexed_data.loc[0] * 100

    return indexed_data

# # Calculate indexed values for future recession
recession_future = calculate_indexed_future(data_excel, pd.to_datetime(recession_start_future[0]), recession_start_high_infla)
recession_future = recession_future.iloc[:-9]
# print(recession_future.tail(24))

# Calculate indexed values for all dates in 'recession_start_high_infla' and 'recession_start_low_infla'
indexed_data_high_infla = pd.concat([calculate_indexed(data_excel, pd.to_datetime(date)) for date in recession_start_high_infla])
indexed_data_low_infla = pd.concat([calculate_indexed(data_excel, pd.to_datetime(date)) for date in recession_start_low_infla])

# Calculate the average indexed values
avg_indexed_high_infla = indexed_data_high_infla.groupby(indexed_data_high_infla.index).mean()
avg_indexed_low_infla = indexed_data_low_infla.groupby(indexed_data_low_infla.index).mean()
# avg_indexed_high_infla.to_excel('high_infla.xlsx')
# avg_indexed_low_infla.to_excel('low_infla.xlsx')

# Define the size of the grid
grid_rows = 3
grid_cols = 2

# Define your color scheme
color_scheme = ['#2e3948', '#d9cab8', '#5fcab7', 'cyan', 'magenta', 'yellow']

# Calculate the number of figures needed
num_figures = math.ceil(len(data_excel.columns) / (grid_rows*grid_cols))

# Iterate over the number of figures
for fig_num in range(num_figures):
    # Create a new figure and a grid of subplots
    fig, axes = plt.subplots(nrows=grid_rows, ncols=grid_cols, figsize=(15, 15))

    # Determine the start and end indices for the columns to be plotted in this figure
    start_idx = fig_num * grid_rows * grid_cols
    end_idx = min(start_idx + grid_rows * grid_cols, len(data_excel.columns))  # take care not to exceed the number of columns
    
    # Iterate over the relevant columns
    for i, column_name in enumerate(data_excel.columns[start_idx:end_idx]):
        # Calculate indexed values for all dates in 'recession_start_high_infla' and 'recession_start_low_infla'
        indexed_data_high_infla = pd.concat([calculate_indexed(data_excel[column_name], pd.to_datetime(date)) for date in recession_start_high_infla])
        indexed_data_low_infla = pd.concat([calculate_indexed(data_excel[column_name], pd.to_datetime(date)) for date in recession_start_low_infla])

        # Calculate the average indexed values
        avg_indexed_high_infla = indexed_data_high_infla.groupby(indexed_data_high_infla.index).mean()
        avg_indexed_low_infla = indexed_data_low_infla.groupby(indexed_data_low_infla.index).mean()

        # Get the relevant portion of the recession_future data
        recession_future_data = recession_future[column_name]

        # Plotting the data for the current column
        row = i // grid_cols
        col = i % grid_cols
        axes[row, col].plot(avg_indexed_high_infla, label='High Inflation Recessions', color=color_scheme[0])
        axes[row, col].plot(avg_indexed_low_infla, label='Low Inflation Recessions', color=color_scheme[1])
        axes[row, col].plot(recession_future_data, label='Current', color=color_scheme[2])

        # Set title and labels
        axes[row, col].set_title(column_name)
        axes[row, col].set_xlabel('Months from Recession Start')
        axes[row, col].set_ylabel('100 = level at start of recession')

        # Add legend
        axes[row, col].legend()
        axes[row, col].axvline(x=0, color='gray', linestyle='--') # Add a gray dotted vertical line at the 0 x-axis value
        axes[row, col].axhline(y=100, color='gray', linestyle='--') # Add a gray dotted horizontal line at the 100 y-axis value

    # Remove any unused subplots
    for i in range(end_idx-start_idx, grid_rows*grid_cols):
        row = i // grid_cols
        col = i % grid_cols
        fig.delaxes(axes[row, col])
        
    # Adjust layout and show the plot
    plt.tight_layout()
    # Adjust layout and show the plot
    plt.subplots_adjust(hspace = 0.2)
    plt.subplots_adjust(wspace = 0.15)
    plt.show()

# # Iterate over all the columns
# for column_name in data_excel.columns:
#     # Create a new figure and a single subplot
#     fig, ax = plt.subplots(figsize=(7.5, 7.5))

#     # Calculate indexed values for all dates in 'recession_start_high_infla' and 'recession_start_low_infla'
#     indexed_data_high_infla = pd.concat([calculate_indexed(data_excel[column_name], pd.to_datetime(date)) for date in recession_start_high_infla])
#     indexed_data_low_infla = pd.concat([calculate_indexed(data_excel[column_name], pd.to_datetime(date)) for date in recession_start_low_infla])

#     # Calculate the average indexed values
#     avg_indexed_high_infla = indexed_data_high_infla.groupby(indexed_data_high_infla.index).mean()
#     avg_indexed_low_infla = indexed_data_low_infla.groupby(indexed_data_low_infla.index).mean()

#     # Get the relevant portion of the recession_future data
#     recession_future_data = recession_future[column_name]

#     # Plotting the data for the current column
#     ax.plot(avg_indexed_high_infla, label='High Inflation Recessions', color=color_scheme[0])
#     ax.plot(avg_indexed_low_infla, label='Low Inflation Recessions', color=color_scheme[1])
#     ax.plot(recession_future_data, label='Current', color=color_scheme[2])

#     # Set title and labels
#     ax.set_title(column_name, fontweight='bold')
#     ax.set_xlabel('Months from Recession Start')
#     ax.set_ylabel('100 = Level at Start of Recession')

#     # Add legend
#     ax.legend()
#     ax.axvline(x=0, color='gray', linestyle='--') # Add a gray dotted vertical line at the 0 x-axis value
#     ax.axhline(y=100, color='gray', linestyle='--') # Add a gray dotted horizontal line at the 100 y-axis value

#     # Adjust layout and show the plot
#     plt.tight_layout()
#     plt.show()










