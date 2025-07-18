import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Github copilot was used for most of the charts

nutrition_raw = pd.read_csv("nutrition/nutrition.csv")
cols_of_interest = ['Calories','Fat (g)', 'Saturated Fat', 'Sodium (mg)', 'Carbohydrates (g)', 'Fiber', 'Sugar', 'Protein (g)', 'Vitamin C', 'Iron']
nutrition_raw['Date'] = pd.to_datetime(nutrition_raw['Date']).dt.date
# Total calories/day
daily_totals = (
  nutrition_raw
  .groupby('Date')
  .agg({x: 'sum' for x in cols_of_interest})
  .reset_index()
)

# Daily Plots
def generate_plot(metric, color):
  plt.figure(figsize=(14, 7))
  sns.barplot(x='Date', y=metric, data=daily_totals, color=color, edgecolor='black')
  plt.title(f'Total {metric} per Day')
  plt.xticks(rotation=45, ha='right')
  overall_mean = daily_totals[metric].mean()
  plt.axhline(overall_mean, color='red', linestyle='--', linewidth=0.5)
  # Add label directly on the graph near the mean line
  ax = plt.gca()
  # Place label at the right edge of the plot, aligned with the mean line
  ax.text(
      x=ax.get_xlim()[0]*0.9,
      y=overall_mean,
      s=f'Average: {overall_mean:.1f}',
      color='red',
      va='bottom',
      ha='left',
      fontsize=9,
      bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, boxstyle='round,pad=0.2')
  )
  plt.tight_layout()
  plt.show()

# Plots for calories and other metrics
generate_plot('Calories', color='royalblue')
generate_plot('Protein (g)', color='lightgreen')
generate_plot('Carbohydrates (g)', color='skyblue')
generate_plot('Fat (g)', color='coral')
generate_plot('Saturated Fat', color='lightcoral')

# Plot calories per meal (stacked bar chart)
calories_by_meal = (
    nutrition_raw.groupby(['Date', 'Meal'])['Calories'].sum().reset_index()
)
pivot = calories_by_meal.pivot(index='Date', columns='Meal', values='Calories').fillna(0)
pivot = pivot.sort_index()
plt.figure(figsize=(14, 7))
bottom = np.zeros(len(pivot))
for meal in pivot.columns:
    plt.bar(pivot.index, pivot[meal], bottom=bottom, label=meal, width=0.9)
    bottom += pivot[meal].values
plt.title('Calories by Meal')
plt.xlabel('Date')
plt.ylabel('Calories')
plt.xticks(rotation=45, ha='right')
plt.legend(title='Meal')
plt.tight_layout()
plt.show()

# Plot normalized macros for each day (line chart)
macros = ['Protein (g)', 'Carbohydrates (g)', 'Fat (g)']
macros_per_day = nutrition_raw.groupby(['Date'])[macros].sum().reset_index()
macros_per_day['Total_Grams'] = macros_per_day[macros].sum(axis=1)
macros_normalized = macros_per_day.copy()
for macro in macros:
    macros_normalized[macro] = macros_per_day[macro] / macros_per_day['Total_Grams']
macros_normalized = macros_normalized.drop(columns=['Total_Grams'])

# Line chart for normalized macros
plt.figure(figsize=(14, 7))
for m in macros:
    plt.plot(macros_normalized['Date'], macros_normalized[m], label=m)
plt.title('Macro % per Day')
plt.xlabel('Date')
plt.ylabel('Proportion of Total Grams')
plt.xticks(rotation=45, ha='right')
plt.legend(title='Macro')
plt.tight_layout()
plt.show()

# Stacked Bar
macros_normalized = macros_normalized.sort_index()
plt.figure(figsize=(14, 7))
bottom = np.zeros(len(macros_normalized))
for m in macros:
    bars = plt.bar(macros_normalized.Date, macros_normalized[m], bottom=bottom, label=m, width=0.9)
    # Add value labels to each bar segment
    for bar, value, btm in zip(bars, macros_normalized[m], bottom):
        if value > 0.01:  # Only label if value is significant
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                btm + value / 2,
                f'{value*100:.0f}%',
                ha='center', va='center', fontsize=8, color='black', rotation=90
            )
    bottom += macros_normalized[m].values
plt.title('Macros Proportion per Day')
plt.xlabel('Date')
plt.ylabel('Proportion of Total Grams')
plt.xticks(rotation=45, ha='right')
plt.legend(title='Macro')
plt.tight_layout()
plt.show()

macros_normalized[macros].mean()
# usual is 25% protein, 15% fat, and 60% carbs