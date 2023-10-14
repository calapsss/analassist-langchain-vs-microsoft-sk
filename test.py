import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("milexpend.csv")

# Group the dataframe by country and calculate the sum of military expenditure
grouped_df = df.groupby('country')['Military expenditure (current USD)'].sum()

# Create a pie chart using the grouped data
plt.pie(grouped_df, labels=grouped_df.index)

# Display the pie chart
plt.show()
