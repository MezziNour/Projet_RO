import pandas as pd
import matplotlib.pyplot as plt

# Visualisation des résultats du benchmark

def plot_benchmark(csv_path="resultats_benchmark.csv"):
    df = pd.read_csv(csv_path)
    algos = df['algo'].unique()
    n_values = sorted(df['n'].unique())
    plt.figure(figsize=(15, 6))
    for algo in algos:
        plt.subplot(1, len(algos), list(algos).index(algo)+1)
        for n in n_values:
            y = df[(df['n'] == n) & (df['algo'] == algo)]['temps']
            x = [n]*len(y)
            plt.scatter(x, y, alpha=0.3, label=f"n={n}" if n==n_values[0] else "")
        # Enveloppe supérieure (max) des temps
        maxs = [df[(df['n'] == n) & (df['algo'] == algo)]['temps'].max() for n in n_values]
        plt.plot(n_values, maxs, color='red', marker='o', label='Max')
        plt.xlabel('n')
        plt.ylabel('Temps (s)')
        plt.title(algo)
        plt.xscale('log')
        plt.yscale('log')
        plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_benchmark()
