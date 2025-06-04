import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

# Portfolio data
portfolio_base = [
    ("SQD", 91343, 0.16, 0.24),
    ("GRASS", 120000, 1.81, 1.84),
    ("SYRUP", 47756, 0.21, 0.406),
    ("INIT", 300000, 0.86, 0.75),
    ("VIRTUALS", 200000, 1.84, 1.88),
    ("COOKIE", 100000, 0.25, 0.22)
]

# Create DataFrame
df = pd.DataFrame(portfolio_base, columns=["Token", "Number of Holdings", "Average Price", "Current Price"])

# Calculate values
df["Cost Basis"] = df["Number of Holdings"] * df["Average Price"]
df["Current Value"] = df["Number of Holdings"] * df["Current Price"]
df["$ Return"] = df["Current Value"] - df["Cost Basis"]
df["% Return"] = (df["$ Return"] / df["Cost Basis"]) * 100

# Mean and std deviation
mean_return = df["% Return"].mean()
std_return = df["% Return"].std()

# Plot normal distribution
x = np.linspace(mean_return - 4*std_return, mean_return + 4*std_return, 1000)
y = norm.pdf(x, mean_return, std_return)

plt.figure(figsize=(10, 6))
plt.hist(df["% Return"], bins=10, density=True, alpha=0.6, edgecolor='black', label="Actual Returns")
plt.plot(x, y, label="Normal Distribution", linewidth=2)
plt.axvline(mean_return, color='red', linestyle='--', label=f"Mean: {mean_return:.2f}%")
plt.title("Distribution of Token % Returns")
plt.xlabel("% Return")
plt.ylabel("Density")
plt.legend()
plt.grid(True)
plt.show()

# Output the average return
print(f"📊 Mean % Return: {mean_return:.2f}%")
print(f"📈 Std Dev % Return: {std_return:.2f}%")
