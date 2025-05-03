import pandas as pd
import matplotlib.pyplot as plt

SHOW_AVG = True  # Set to False to show max only
LINEAR_SCALE = False  # Set to True to use linear scale

# Visualisation des résultats du benchmark

def plot_benchmark(csv_path="resultats_benchmark.csv"):
    df = pd.read_csv(csv_path)
    algos = df['algo'].unique()
    n_values = sorted(df['n'].unique())
    plt.figure(figsize=(15, 6))

    # Compute global min and max for 'temps'
    y_min = df['temps'].min()
    y_max = df['temps'].max()

    for algo in algos:
        plt.subplot(1, len(algos), list(algos).index(algo)+1)
        for n in n_values:
            y = df[(df['n'] == n) & (df['algo'] == algo)]['temps']
            x = [n]*len(y)
            plt.scatter(x, y, alpha=0.3, label=f"n={n}" if n==n_values[0] else "")
        # Enveloppe supérieure (max) des temps
        maxs = [df[(df['n'] == n) & (df['algo'] == algo)]['temps'].max() for n in n_values]
        plt.plot(n_values, maxs, color='red', marker='o', label='Max')
        if SHOW_AVG:
            avgs = [df[(df['n'] == n) & (df['algo'] == algo)]['temps'].mean() for n in n_values]
            plt.plot(n_values, avgs, color='blue', marker='x', linestyle='--', label='Moyenne')

        plt.xlabel('n')
        plt.ylabel('Temps (s)')
        plt.title(algo)
        plt.xticks(n_values)

        if not LINEAR_SCALE:
            plt.xscale('log')
            plt.yscale('log')

        plt.ylim(y_min, y_max)  # Set same y scale for all subplots
        plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_benchmark()
