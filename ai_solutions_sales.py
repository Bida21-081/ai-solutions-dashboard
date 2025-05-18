import matplotlib
matplotlib.use('TkAgg')  # Enable interactive backend

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np  # Optional: For pie chart

plt.ion()

# Load new dataset
df = pd.read_csv("ai_solutions_sales_data.csv")

# Add Hour column
df['Hour'] = pd.to_datetime(df['Time'], format='%H:%M:%S').dt.hour

# Categorize Request Type
df['RequestType'] = df['URL'].apply(lambda x: 'AI Assistant' if x == '/aiassistant.php'
                                    else 'Scheduled Demo' if x == '/scheduledemo.php'
                                    else 'Promotional Event' if x == '/event.php'
                                    else 'Job Request' if x in ['/job.php', '/prototype.php']
                                    else 'Other')

# --------- 1. Requests Over Time (Line Chart) ---------
plt.figure(figsize=(10, 5))
requests_per_hour = df['Hour'].value_counts().sort_index()
plt.plot(requests_per_hour.index, requests_per_hour.values, marker='o', linestyle='-', color='teal')
plt.title("Website Requests by Hour of Day")
plt.xlabel("Hour (0–23)")
plt.ylabel("Number of Requests")
plt.grid(True)
plt.tight_layout()
plt.savefig("requests_by_hour.png", dpi=300)
plt.show(block=True)

# --------- 2. Job Type Requests (Pie Chart) ---------
job_pages = ["/job.php", "/scheduledemo.php", "/aiassistant.php", "/event.php", "/prototype.php"]
df_jobs = df[df['URL'].isin(job_pages)]
plt.figure(figsize=(7, 7))
job_counts = df_jobs['URL'].value_counts()
colors = sns.color_palette('pastel')[0:len(job_counts)]
plt.pie(job_counts, labels=job_counts.index, autopct='%1.1f%%', colors=colors, startangle=140)
plt.title("Distribution of Job-Related Requests")
plt.tight_layout()
plt.savefig("job_requests_pie.png", dpi=300)
plt.show(block=True)

# --------- 3. Demo Requests by Country (Horizontal Bar Chart) ---------
demo_requests = df[df['URL'] == "/scheduledemo.php"]
demo_counts = demo_requests['Country'].value_counts()
plt.figure(figsize=(10, 6))
sns.barplot(x=demo_counts.values, y=demo_counts.index, palette='crest', hue=demo_counts.index, legend=False)
plt.title("Scheduled Demo Requests by Country")
plt.xlabel("Number of Demo Requests")
plt.ylabel("Country")
plt.tight_layout()
plt.savefig("demo_requests_by_country.png", dpi=300)
plt.show(block=True)

# --------- 4. AI Assistant vs Other Requests (Stacked Bar Chart) ---------
type_country = df.groupby(['Country', 'RequestType']).size().unstack().fillna(0)
type_country[['AI Assistant', 'Other']].plot(kind='bar', stacked=True, figsize=(12, 6), colormap='Set2')
plt.title("AI Assistant vs Other Requests per Country")
plt.ylabel("Number of Requests")
plt.xlabel("Country")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("ai_vs_other_requests.png", dpi=300)
plt.show(block=True)

# --------- 5. Revenue by Product (Bar Chart) ---------
product_sales = df.groupby('Product')['Revenue'].sum().sort_values(ascending=False)
plt.figure(figsize=(10, 6))
sns.barplot(x=product_sales.values, y=product_sales.index, palette='viridis', hue=product_sales.index, legend=False)
plt.title("Revenue by Product")
plt.xlabel("Revenue ($)")
plt.ylabel("Product")
plt.tight_layout()
plt.savefig("revenue_by_product.png", dpi=300)
plt.show(block=True)

# --------- 6. Sales by Country (Pie Chart) ---------
sales_by_country = df.groupby('Country')['Revenue'].sum()
plt.figure(figsize=(7, 7))
plt.pie(sales_by_country, labels=sales_by_country.index, autopct='%1.1f%%', startangle=140)
plt.title("Sales Distribution by Country")
plt.tight_layout()
plt.savefig("sales_by_country_pie.png", dpi=300)
plt.show(block=True)

# --------- 7. Sale Amount Distribution (Histogram) ---------
plt.figure(figsize=(10, 6))
sns.histplot(df[df['Revenue'] > 0]['Revenue'], bins=50, kde=True, color='green')
plt.title("Distribution of Sale Amounts")
plt.xlabel("Sale Value ($)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("sales_distribution_hist.png", dpi=300)
plt.show(block=True)
