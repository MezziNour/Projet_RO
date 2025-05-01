import pandas as pd
import matplotlib.pyplot as plt

def plot_ff_over_pr(csv_path="resultats_benchmark.csv"):
    df = pd.read_csv(csv_path)
    n_values = sorted(df['n'].unique())
    ratios = []
    for n in n_values:
        ff_max = df[(df['n'] == n) & (df['algo'] == 'ford_fulkerson')]['temps'].max()
        pr_max = df[(df['n'] == n) & (df['algo'] == 'pousser_reetiq')]['temps'].max()
        if pr_max > 0:
            ratios.append(ff_max / pr_max)
        else:
            ratios.append(float('nan'))
    plt.figure(figsize=(8, 5))
    plt.plot(n_values, ratios, marker='o', color='purple')
    plt.xscale('log')
    plt.xlabel('n')
    plt.ylabel(r'$\theta_{FF}/\theta_{PR}$ (max)')
    plt.title('Rapport des temps max Ford-Fulkerson / Pousser-Réétiqueter')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.show()

if __name__ == "__main__":
    plot_ff_over_pr()
