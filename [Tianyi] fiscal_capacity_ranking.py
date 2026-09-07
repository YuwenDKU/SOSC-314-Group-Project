import pandas as pd
import matplotlib.pyplot as plt

# Five cities' 2025 fiscal revenue data (RMB billion)
data = {
    'city': ['Shanghai', 'Hangzhou', 'Suzhou', 'Ningbo', 'Nanjing'],
    'revenue': [8500.9, 2693.2, 2490.2, 1795.3, 1620.9],
    'source_url': [
        'https://www.shanghai.gov.cn/nw12338/20260515/a97f758537314ce7b2c0e26614e179f6.html',
        'https://www.hangzhou.gov.cn/2026nhzslh/gzbg/art/2026/art_38cc25d5ba2a4e76b87c0695a9e02b05.html',
        'https://www.suzhou.gov.cn/szsrmzf/czyjsbg/202603/57f2227cdfff4bef8a8c37ee8580add5.shtml',
        'http://yjs.czj.ningbo.gov.cn/gkxxzl/nbcs/html/2026/10000000002017371.html',
        'https://czj.nanjing.gov.cn/njsczj/202603/P020260304332132680539.pdf'
    ]
}

df = pd.DataFrame(data)

# Sort by revenue from highest to lowest
df_sorted = df.sort_values('revenue', ascending=False).reset_index(drop=True)

# Assign fiscal capacity levels (ordered from highest to lowest capacity)
levels = ['Highest', 'High', 'High', 'Medium-High', 'Medium']
df_sorted['capacity_level'] = levels

# Calculate percentage of Shanghai's revenue (Shanghai = 100%)
df_sorted['ratio_to_shanghai'] = (df_sorted['revenue'] / df_sorted['revenue'].max() * 100).round(1)

# Add rank column (1 = highest fiscal capacity)
df_sorted['rank'] = [1, 2, 3, 4, 5]

# Print a separator line of 70 equal signs for visual clarity
print("=" * 70)

# Print the title of the ranking table
print("FISCAL CAPACITY RANKING (2025)")

# Print another separator line
print("=" * 70)

# Display the ranking table with selected columns (rank, city, revenue, capacity_level, ratio_to_shanghai)
# to_string(index=False) removes the default row numbers for cleaner output
print(df_sorted[['rank', 'city', 'revenue', 'capacity_level', 'ratio_to_shanghai']].to_string(index=False))

# Print a separator line
print("=" * 70)

# Print the total number of cities (len() counts rows in the dataframe)
print(f"Number of cities: {len(df_sorted)}")

# Print the revenue range (min to max values in the revenue column)
print(f"Range: {df_sorted['revenue'].min():.1f} to {df_sorted['revenue'].max():.1f} billion")

# Print the ratio between the highest and lowest revenue (showing the fiscal gap)
print(f"Max/Min ratio: {df_sorted['revenue'].max() / df_sorted['revenue'].min():.1f}x")

# Print a final separator line
print("=" * 70)

# Here we made the assumption that he 2025 fiscal ranking represents each city's long-term fiscal capacity rather than a year-specific fluctuation. 
#  To justify this assumption, we draw on Yan et al. (2024), who examined the fiscal conditions of 284 Chinese prefecture-level cities across three time points—2000, 2010, and 2020.
literature_url = "https://www.sciencedirect.com/science/article/pii/S014362282400167X"

# Visualization: Bar chart of fiscal capacity ranking
fig, ax = plt.subplots(figsize=(10, 6))

# Define colors for each city (consistent with ranking order)
colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd', '#d62728']
bars = ax.bar(df_sorted['city'], df_sorted['revenue'], color=colors, edgecolor='white', linewidth=1.5)

ax.set_xlabel('City', fontsize=10)
ax.set_ylabel('Revenue (RMB billion)', fontsize=12)
ax.set_title('Fiscal Capacity Ranking: 5 Eastern Chinese Cities (2025)', fontsize=14, fontweight='bold')
ax.set_ylim(0, 9500)

# Add revenue value and capacity level labels on each bar
for i, (bar, city, revenue, level) in enumerate(zip(bars, df_sorted['city'], df_sorted['revenue'], df_sorted['capacity_level'])):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 200,
            f'{revenue:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.text(bar.get_x() + bar.get_width()/2., height/2,
            level, ha='center', va='center', fontsize=10, color='white', fontweight='bold', rotation=90)

# Add rank labels below each bar
for i, bar in enumerate(bars):
    ax.text(bar.get_x() + bar.get_width()/2., -400,
            f'Rank #{i+1}', ha='center', va='top', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('fiscal_capacity_ranking.png', dpi=300)
plt.show()
