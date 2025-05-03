from collections import deque
import os
import sys
from typing import List, Tuple, Optional

# Lecture des données et stockage en mémoire
def detecter_type_probleme(chemin: str) -> Tuple[str, int]:
    """
    Détecte le type de problème de flot à partir d'un fichier.
    Retourne (type_probleme, n) où type_probleme est 'flot_max' ou 'flot_min', et n est le nombre de sommets.
    Lève ValueError si le format du fichier est invalide.
    """
    with open(chemin, 'r', encoding='utf-8') as f:
        lignes = f.readlines()
    if not lignes:
        raise ValueError("Fichier vide.")
    try:
        n = int(lignes[0])
    except Exception as exc:
        raise ValueError("Première ligne du fichier invalide (doit être un entier).") from exc
    nb_lignes = len(lignes)
    if nb_lignes == n + 1:
        return "flot_max", n
    if nb_lignes == 2 * n + 1:
        return "flot_min", n

    raise ValueError("Format de fichier incorrect (lignes incohérentes avec n)")

def lire_flot_max(chemin: str) -> Tuple[int, List[List[int]]]:
    """
    Lit un problème de flot maximum à partir d'un fichier.
    Retourne (n, capacites) où n est le nombre de sommets et capacites est la matrice des capacités.
    """
    with open(chemin, 'r', encoding='utf-8') as f:
        n = int(f.readline())
        capacites = [list(map(int, f.readline().split())) for _ in range(n)]

    if len(capacites) != n or any(len(row) != n for row in capacites):
        raise ValueError("Matrice des capacités invalide.")

    return n, capacites


def lire_flot_min(chemin: str) -> Tuple[int, List[List[int]], List[List[int]]]:
    """
    Lit un problème de flot de coût minimal à partir d'un fichier.
    Retourne (n, capacites, couts) où n est le nombre de sommets, capacites la matrice des capacités, couts la matrice des coûts.
    """
    with open(chemin, 'r', encoding='utf-8') as f:
        n = int(f.readline())
        capacites = [list(map(int, f.readline().split())) for _ in range(n)]
        couts = [list(map(int, f.readline().split())) for _ in range(n)]

    if len(capacites) != n or len(couts) != n or any(len(row) != n for row in capacites + couts):
        raise ValueError("Matrices des capacités ou des coûts invalides.")

    return n, capacites, couts


# Affichage des tableaux
def afficher_matrice(matrice: List[List[int]], titre: str, other: Optional[List[List[int]]] = None, other_titre: str = None) -> None:
    """
    Affiche une matrice avec un titre de façon formatée.
    """
    print(f"\n{titre} :")
    n = len(matrice)
    cell_width = 7
    bold_start = "\033[1m"  # Code ANSI pour le texte en gras
    bold_end = "\033[0m"    # Code ANSI pour réinitialiser le style
    blue = "\033[34m"        # Bleu
    reset = "\033[37m"       # Réinitialisation

    print("     ", end="")
    for j in range(n):
        print(f"{'v'+str(j+1):^{cell_width}}", end="│")

    # Ligne de séparation
    print("\n    ├" + ("─" * cell_width + "┼") * (n - 1) + "─" * cell_width + "┤")

    # Corps de la matrice
    for i in range(n):
        print(f"{'v'+str(i+1):<3} │", end="")  # Nom de la ligne
        for j in range(n):
            if matrice[i][j] > 0:
                cell = f"{matrice[i][j]}"
                print(f"{blue}{bold_start}{cell:^{cell_width}}{bold_end}{reset}│", end="")
            else:
                cell = "0"
                print(f"{cell:^{cell_width}}│", end="")
        print()
    
    if other:
        print(f"\n{other_titre} :")
        print("     ", end="")
        for j in range(n):
            print(f"{'v'+str(j+1):^{cell_width}}", end="│")

        # Ligne de séparation
        print("\n    ├" + ("─" * cell_width + "┼") * (n - 1) + "─" * cell_width + "┤")
        for i in range(n):
            print(f"{'v'+str(i+1):<3} │", end="")  # Nom de la ligne
            for j in range(n):
                if matrice[i][j] > 0:
                    cell = f"{other[i][j]}"
                    print(f"{blue}{bold_start}{cell:^{cell_width}}{bold_end}{reset}│", end="")
                else:
                    cell = "0"
                    print(f"{cell:^{cell_width}}│", end="")
            print()

def afficher_matrice_FF(titre: str, c: List[List[int]], flot: List[List[int]], h: Optional[List[int]] = None) -> None:
    """
    Affiche la matrice de flot sous la forme x/y (flot/capacité), éventuellement avec les hauteurs h.
    """
    n = len(c)
    cell_width = 9  # Largeur constante pour chaque cellule
    bold_start = "\033[1m"  # Code ANSI pour le texte en gras
    bold_end = "\033[0m"    # Code ANSI pour réinitialiser le style
    blue = "\033[34m"        # Rouge
    reset = "\033[37m"       # Réinitialisation

    print(f"\nMatrice {titre} :")
    print("     ", end="")
    for j in range(n):
        if h:
            header = f"v{j+1}({h[j]})"
        else:
            header = f"v{j+1}"
        print(f"{header:^{cell_width}}", end="│")
    print("\n    ├" + ("─" * cell_width + "┼") * (n - 1) + "─" * cell_width + "┤")

    for i in range(n):
        print(f"{'v'+str(i+1):<3} │", end="")  # Nom de la ligne
        for j in range(n):
            if c[i][j] > 0:
                cell = f"{flot[i][j]}/{c[i][j]}"
                print(f"{blue}{bold_start}{cell:^{cell_width}}{bold_end}{reset}│", end="")
            else:
                cell = "0"
                print(f"{cell:^{cell_width}}│", end="")
        print()

# Parcours en largeur
def plargeur_chaine_améliorante(
    c: List[List[int]], flot: List[List[int]], s: int, t: int, parent: List[int], verbose: bool = False
) -> bool:
    """
    Parcours en largeur pour trouver une chaîne améliorante dans le graphe résiduel.
    Retourne True si un chemin de s à t est trouvé, et met à jour parent.
    """
    n = len(c)
    visite = [False] * n
    file = deque()
    file.append(s)
    visite[s] = True
    parent[s] = -1

    if verbose:
        print("\nParcours en largeur pour chercher une chaîne améliorante :")

    while file:
        u = file.popleft()
        for v in range(n):
            residuel = c[u][v] - flot[u][v]
            if not visite[v] and residuel > 0:
                # Met à jour le tableau des parents quand un chemin est trouvé
                parent[v] = u
                visite[v] = True
                file.append(v)
                if verbose:
                    print(f"    v{u+1} -> v{v+1} (capacité résiduelle = {residuel})")
                if v == t:
                    return True
    return False

# Algorithme de Ford-Fulkerson
def ford_fulkerson(
    c: List[List[int]], s: int, t: int, verbose: bool = False
) -> int:
    """
    Algorithme de Ford-Fulkerson pour le flot maximum.
    Retourne la valeur du flot maximum.
    """
    n = len(c)
    flot = [[0]*n for _ in range(n)] # Initialisation du flot à 0
    parent = [-1] * n
    flot_max = 0
    i = 1 # Compteur d'itérations

    if verbose:
        print("\nLe graphe résiduel initial est le graphe de départ.")

    while plargeur_chaine_améliorante(c, flot, s, t, parent, verbose):
        if verbose:
            print(f"Itération {i} : ")
        chemin = []
        v = t
        flot_ajoute = float('inf') # Plus petit résiduel trouvé sur le chemin

        # Construction du chemin améliorant à partir du tableau des parents
        while v != s:
            u = parent[v]
            chemin.insert(0, (u, v)) # Ajoute au début du chemin
            flot_ajoute = min(flot_ajoute, c[u][v] - flot[u][v])
            v = u

        if verbose:
            print(f"\nChaîne améliorante {i} : " + " -> ".join([f"v{u+1}" for u, _ in chemin] + [f"v{t+1}"]) + f" de flot : {flot_ajoute}")

        # Mise à jour des flots dans la matrice
        for u, v in chemin:
            flot[u][v] += flot_ajoute
            flot[v][u] -= flot_ajoute # Flot inverse pour maintenir la conservation

        flot_max += flot_ajoute
        if verbose:
            afficher_matrice_FF(f"résiduelle {i}", c, flot)
        i += 1

    if verbose:
        print("\nOn ne peut plus accéder au dernier sommet. Fin de l'algorithme.")
        afficher_matrice_FF("finale", c, flot)

    return int(flot_max)

def pousser_reetiqueter(
    c: List[List[int]], s: int, t: int, verbose: bool = False
) -> int:
    """
    Algorithme Push-Relabel (pousser-réétiqueter) pour le flot maximum.
    Retourne la valeur du flot maximum.
    """
    n = len(c)
    flot = [[0] * n for _ in range(n)]
    h = [0] * n
    e = [0] * n
    h[s] = n
    i = 0
    actifs = deque()
    actifs.append(s)
    for v in range(n):
        if c[s][v] > 0:
            flot[s][v] = c[s][v]
            flot[v][s] = -c[s][v]
            e[v] = c[s][v]
            e[s] -= c[s][v]
            if v != s and v != t:
                actifs.append(v)
    if verbose:
        afficher_matrice_FF("initiale (0)", c, flot, h)

    def push(u: int, v: int) -> bool:
        delta = min(e[u], c[u][v] - flot[u][v])
        flag = False
        if delta > 0:
            if verbose and flot[u][v] + delta < 0:
                print(f"Flot poussé de v{u+1} -> v{v+1} : {delta}")
                flag = True
            flot[u][v] += delta
            flot[v][u] -= delta
            e[u] -= delta
            e[v] += delta
            if v != s and v != t and e[v] == delta and v not in actifs:
                actifs.append(v)
            if verbose and not flag:
                print(f"Flot poussé de v{u+1} -> v{v+1} : {flot[u][v]}")
            return True
        return False

    def relabel(u: int) -> None:
        min_h = float('inf')
        for v in range(n):
            if c[u][v] - flot[u][v] > 0:
                min_h = min(min_h, h[v])
        if min_h < float('inf'):
            h[u] = min_h + 1
        if verbose:
            print(f"Réétiquetage de v{u+1} : {h[u]}")

    def select_highest_active() -> Optional[int]:
        """
        Sélectionne le sommet actif avec la hauteur la plus grande.
        En cas d'égalité, retourne celui avec l'indice le plus petit.
        """
        max_height = -1
        selected = None
        for u in actifs:
            if h[u] > max_height or (h[u] == max_height and (selected is None or u < selected)):
                max_height = h[u]
                selected = u
        actifs.remove(selected)
        return selected

    while actifs:
        u = select_highest_active()
        while e[u] > 0:
            i += 1
            if verbose:
                print(f"\nItération {i} :")
            pushed = False
            if c[u][t] - flot[u][t] > 0 and h[u] == h[t] + 1:
                if push(u, t):
                    pushed = True
            else:
                for v in range(n):
                    if c[u][v] - flot[u][v] > 0 and h[u] == h[v] + 1:
                        if push(u, v):
                            pushed = True
                            break
            if not pushed:
                relabel(u)
            
            if verbose:
                afficher_matrice_FF(f"({i})", c, flot, h)

    return int(sum(flot[s][v] for v in range(n)))

def afficher_table_bellman(snapshots: List[Tuple[List[float], List[int]]], names: List[str]) -> None:
    """
    Affiche la table de Bellman pour chaque itération (pour le flot de coût minimal).
    """
    header = ["k"] + names[:]
    rows = []
    for k, (dist, parent) in enumerate(snapshots):
        row = [str(k)]
        for i in range(len(names)):
            if dist[i] == float('inf'):
                cell = "+∞"
            else:
                if parent[i] == -1:
                    cell = str(dist[i])
                else:
                    cell = f"{names[parent[i]]}{dist[i]}"
            row.append(cell)
        rows.append(row)

    stop = len(rows) - 1
    for i in range(1, len(rows)):
        if rows[i][1:] == rows[i-1][1:]:
            stop = i
            break

    rows = rows[:stop+1]

    table = [header] + rows
    col_widths = [max(len(r[j]) for r in table) for j in range(len(header))]

    def print_line(left: str, mid: str, right: str) -> None:
        line = left
        for idx, w in enumerate(col_widths):
            line += '─' * (w + 2)
            line += mid if idx < len(col_widths)-1 else right
        print(line)

    def print_row(items: List[str]) -> None:
        row = '│'
        for idx, item in enumerate(items):
            row += ' ' + item.center(col_widths[idx]) + ' ' + '│'
        print(row)

    print()
    print_line('┌', '┬', '┐')
    print_row(header)
    print_line('├', '┼', '┤')
    for row in rows:
        print_row(row)
    print_line('└', '┴', '┘')


def flot_cout_minimal(
    c: List[List[int]], couts: List[List[int]], s: int, t: int, flux_demandee: int, verbose: bool = False
) -> float:
    """
    Algorithme de flot de coût minimal (chemins augmentants successifs, Bellman-Ford).
    Retourne (flot, cout_total). Si le flot demandé n'est pas atteignable, cout_total vaut float('inf').
    """
    n = len(c)
    # Réseau résiduel des capacités
    cap_res = [row[:] for row in c]
    # Matrice des coûts résiduels
    cout_res = [[0]*n for _ in range(n)]
    for u in range(n):
        for v in range(n):
            if c[u][v] > 0:
                cout_res[u][v] = couts[u][v]

    flot = [[0]*n for _ in range(n)]
    flux_courant = 0
    cout_total = 0
    it = 0
    names = ['s'] + [chr(ord('a')+i) for i in range(n-2)] + ['t']

    while flux_courant < flux_demandee:
        # Initialisation Bellman
        dist = [float('inf')] * n
        parent = [-1] * n
        dist[s] = 0
        snapshots = [(dist.copy(), parent.copy())]

        for _ in range(n-1):
            updated = False
            new_dist = dist.copy()
            new_parent = parent.copy()
            for u in range(n):
                if dist[u] == float('inf'):
                    continue
                for v in range(n):
                    if cap_res[u][v] > 0 and dist[u] + cout_res[u][v] < new_dist[v]:
                        new_dist[v] = dist[u] + cout_res[u][v]
                        new_parent[v] = u
                        updated = True
            dist, parent = new_dist, new_parent
            snapshots.append((dist.copy(), parent.copy()))
            if not updated:
                break

        it += 1

        # Affichage du tableau de Bellman
        if verbose:
            print(f"\nItération {it} :")
            afficher_table_bellman(snapshots, names)

        # Pas de chemin si parent[t] = -1
        if parent[t] == -1:
            if verbose:
                print("Pas de chemin résiduel disponible – arrêt de l'algorithme.")
            break

        # Reconstruction de la chaîne augmentante
        chemin = []
        v = t
        vus = set() # Ensemble des sommets visités pour éviter les cycles
        while v != s:
            u = parent[v]
            if u == -1 or v in vus:
                chemin = []
                break
            chemin.insert(0, (u, v))
            vus.add(v)
            v = u

        if not chemin:
            break

        # Capacité minimale le long du chemin
        flot_potentiel = min(cap_res[u][v] for u, v in chemin)
        delta = min(flot_potentiel, flux_demandee - flux_courant)

        if verbose:
            print(f"Chaîne améliorante {it} : {' -> '.join(names[u] for u, _ in chemin)} -> {names[t]} | flot potentiel = {delta}")

        # Mise à jour des flots, des coûts résiduels et du coût total
        for u, v in chemin:
            cap_res[u][v] -= delta
            cap_res[v][u] += delta

            # Met à jour flot et coût
            if c[u][v] > 0:
                flot[u][v] += delta
                cout_total += delta * couts[u][v]
                cout_res[u][v] = couts[u][v]
                cout_res[v][u] = -couts[u][v]
            else:
                flot[v][u] -= delta
                cout_total -= delta * couts[v][u]
                cout_res[v][u] = couts[v][u]
                cout_res[u][v] = -couts[v][u]


        flux_courant += delta
        
        if verbose:
            print(f"\nGraphe résiduel après itération {it} :")
            afficher_matrice(cap_res, "capacités résiduelles", cout_res, "coûts résiduels")


    if flux_courant == flux_demandee:
        if verbose:
            print(f"\nAtteint le flot demandé = {flux_demandee} | coût minimal = {cout_total}\n")
        return cout_total

    if verbose:
        print(f"\nImpossible d'atteindre le flot demandé = {flux_demandee} | flot courant = {flux_courant} | coût minimal = infini\n")
    return float('inf')

def generateTraces():
    data_folder = 'data'
    for fichier in os.listdir(data_folder):
        if fichier.endswith('.txt'):
            file_number = fichier.split(' ')[-1].split('.')[0]

            type_probleme, n = detecter_type_probleme(f"data/{file_number}.txt")
            
            try:
                if type_probleme == "flot_max":
                    for i in range(2):
                        n, capacites = lire_flot_max(f"data/{file_number}.txt")
                        s = 0
                        t = n - 1
                        if i == 0:
                            output_file = f'trace/B4-trace{file_number}-FF.txt'
                            sys.stdout = open(output_file, 'w', encoding='utf-8')
                            afficher_matrice(capacites, "Matrice des capacités")
                            valeur_flot = ford_fulkerson(capacites, s, t, verbose=True)
                        else:
                            output_file = f'trace/B4-trace{file_number}-PR.txt'
                            sys.stdout = open(output_file, 'w', encoding='utf-8')
                            afficher_matrice(capacites, "Matrice des capacités")
                            valeur_flot = pousser_reetiqueter(capacites, s, t, verbose=True)
                        print(f"\nValeur du flot maximal : {valeur_flot}")
                elif type_probleme == "flot_min":
                    output_file = f'trace/B4-trace{file_number}-MIN.txt'
                    sys.stdout = open(output_file, 'w', encoding='utf-8')                  
                    n, capacites, couts = lire_flot_min(f"data/{file_number}.txt")
                    afficher_matrice(capacites, "Matrice des capacités", couts, "Matrice des coûts")
                    s = 0
                    t = n - 1
                    flot_max = ford_fulkerson(capacites, s, t)
                    cout_total = flot_cout_minimal(capacites, couts, s, t, flot_max, verbose=True)
                    print(f"\nRésultat : Coût minimal pour un flot de {flot_max} = {cout_total}")
            except Exception as e:
                print(f"Erreur lors du traitement du fichier {fichier}: {e}")
            
            # Close the file
            sys.stdout.close()
    
    # Reset stdout to the original state
    sys.stdout = sys.__stdout__