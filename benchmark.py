import time
import csv
import numpy as np
from fonctions import ford_fulkerson, pousser_reetiqueter, flot_cout_minimal

# Génération d'un problème de flot aléatoire

def generer_probleme_aleatoire(n, seed=None):
    if seed is not None:
        np.random.seed(seed)
    capacites = np.zeros((n, n), dtype=int)
    couts = np.zeros((n, n), dtype=int)
    nb_arcs = int((n * n) // 2)
    indices = [(i, j) for i in range(n) for j in range(n) if i != j]
    np.random.shuffle(indices)
    for (i, j) in indices[:nb_arcs]:
        capacites[i, j] = np.random.randint(1, 101)
        couts[i, j] = np.random.randint(1, 101)
    # source n'a pas d'arcs entrants
    capacites[:, 0] = 0
    # puits n'a pas d'arcs sortants
    capacites[n-1, :] = 0
    return capacites, couts

# Mesure le temps d'exécution d'une fonction

def mesurer_temps(f, *args, **kwargs):
    debut = time.perf_counter()
    resultat = f(*args, **kwargs, verbose=False)
    fin = time.perf_counter()
    return resultat, fin - debut

# Boucle d'expérimentation

def benchmark_algos(num_nodes, repetitions=100, output_file="resultats_benchmark.csv"):
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["n", "run", "algo", "temps"])
        for n in num_nodes:
            for run in range(repetitions):
                capacites, couts = generer_probleme_aleatoire(n)
                s, t = 0, n-1
                # Ford-Fulkerson
                res1, t_ff = mesurer_temps(ford_fulkerson, capacites.tolist(), s, t)
                writer.writerow([n, run, "ford_fulkerson", t_ff])
                # Pousser-Réétiqueter
                res2, t_pr = mesurer_temps(pousser_reetiqueter, capacites.tolist(), s, t)
                writer.writerow([n, run, "pousser_reetiq", t_pr])
                # Flot à coût min
                flot_max, _ = mesurer_temps(ford_fulkerson, capacites.tolist(), s, t)
                flot_demande = max(1, flot_max // 2)
                res3, t_min = mesurer_temps(flot_cout_minimal, capacites.tolist(), couts.tolist(), s, t, flot_demande)
                writer.writerow([n, run, "flot_cout_min", t_min])
                if res1 != res2 and res3 != flot_demande:
                    print(f"!!!!\tErreur de résultat pour n={n}, run={run+1}\t!!!!")
                    print(f"Ford-Fulkerson: {res1}, Pousser-Réétiqueter: {res2}, Flot à coût min: {res3}, flot demandé: {flot_demande}")
                else:
                    print(f"n={n} run={run+1}/ {repetitions} OK, temps : {t_ff:.4f} (Ford-Fulkerson), {t_pr:.4f} (Pousser-Réétiqueter), {t_min:.4f} (Flot à coût min)")

if __name__ == "__main__":
    n_values = [10, 20, 40, 100, 400, 1000, 4000, 10000]
    benchmark_algos(n_values)