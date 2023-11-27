import pandas as pd

# Read data from CSV file
df = pd.read_csv('simpsons_data.csv', parse_dates=['Month'])

# Display basic statistics
print("Basic Statistics:")
print(df.describe())

# Calculate additional statistics
max_value = df['the simpsons: (Worldwide)'].max()
min_value = df['the simpsons: (Worldwide)'].min()
average_value = df['the simpsons: (Worldwide)'].mean()

print("\nAdditional Statistics:")
print(f"Max Value: {max_value}")
print(f"Min Value: {min_value}")
print(f"Average Value: {average_value}")

# More complex statistics
median_value = df['the simpsons: (Worldwide)'].median()
std_deviation = df['the simpsons: (Worldwide)'].std()
variance = df['the simpsons: (Worldwide)'].var()

print("\nMore Complex Statistics:")
print(f"Median Value: {median_value}")
print(f"Standard Deviation: {std_deviation}")
print(f"Variance: {variance}")

# Plotting the data
df.plot(x='Month', y='the simpsons: (Worldwide)', title='The Simpsons Google Trends')
