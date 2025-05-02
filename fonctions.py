from collections import deque

# Lecture des données et stockage en mémoire
def detecter_type_probleme(chemin): 
    with open(chemin, 'r') as f:
        lignes = f.readlines()
    n = int(lignes[0]) # Le nombre de sommets
    nb_lignes = len(lignes)
    if nb_lignes == n + 1:
        return "flot_max", n
    elif nb_lignes == 2 * n + 1:
        return "flot_min", n
    else:
        raise ValueError("Format de fichier incorrect (lignes incohérentes avec n)")
    # Retourne le type de problème et le nombre de sommets n 

def lire_flot_max(chemin):
    with open(chemin, 'r') as f:
        n = int(f.readline())
        capacites = [list(map(int, f.readline().split())) for _ in range(n)] # Matrice des capacités
    return n, capacites
   

def lire_flot_min(chemin):
    with open(chemin, 'r') as f:
        n = int(f.readline())
        capacites = [list(map(int, f.readline().split())) for _ in range(n)] # Matrice des capacités
        couts = [list(map(int, f.readline().split())) for _ in range(n)] # Matrice des coûts
    return n, capacites, couts


# Affichage des tableaux
def afficher_matrice(matrice, titre):
    print(f"\n{titre} :")
    n = len(matrice)
    cell_width = 7  

    # En-tête des colonnes
    print("     ", end="")
    for j in range(n):
        print(f"{'v'+str(j+1):^{cell_width}}", end="│")
    print()

    # Ligne de séparation
    print("    ├" + ("─" * cell_width + "┼") * (n - 1) + "─" * cell_width + "┤")

    # Corps de la matrice
    for i in range(n):
        print(f"{'v'+str(i+1):<3} │", end="")
        for j in range(n):
            print(f"{matrice[i][j]:^{cell_width}}│", end="")
        print()

def afficher_bellman(distances, parents):
    print("\nTable de Bellman :")
    print("Sommet │ Distance │ Prédécesseur")
    print("-------│----------│-------------")
    for i in range(len(distances)):
        pred = "-" if parents[i] == -1 else f"v{parents[i]+1}"
        print(f"v{i+1:^5} │ {distances[i]:^8} │ {pred:^11}")

def afficher_matrice_FF(titre, c, flot, h=None):
    # Affiche la matrice de flot sous la forme x/y, où x = flot actuel, y = capacité.
    n = len(c)
    cell_width = 9  # Largeur constante pour chaque cellule

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
            else:
                cell = "0"
            print(f"{cell:^{cell_width}}│", end="")
        print()

        
# Parcours en largeur
def plargeur_chaine_améliorante(c, flot, s, t, parent, verbose=False):
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
                parent[v] = u # Met à jour le tableau des parents quand un chemin est trouvé
                visite[v] = True
                file.append(v)
                if verbose:
                    print(f"    v{u+1} -> v{v+1} (capacité résiduelle = {residuel})")
                if v == t:
                    return True # Un chemin jusqu'au sommet final est trouvé
    return False # Aucun chemin trouvable

# Algorithme de Ford-Fulkerson 
def ford_fulkerson(c, s, t, verbose=False):
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
        print("\nOn ne peut plus accéder au dernier sommet. Fin de l'agorithme.") 
        afficher_matrice_FF("finale", c, flot)
    
    return flot_max

def pousser_réétiqueter(c, s, t, verbose=False):
    n = len(c)
    flot = [[0] * n for _ in range(n)]
    h = [0] * n
    e = [0] * n
    h[s] = n
    actifs = deque()

    # Pré-flot initial
    for v in range(n):
        if c[s][v] > 0:
            flot[s][v] = c[s][v]
            flot[v][s] = -c[s][v]
            e[v] = c[s][v]
            e[s] -= c[s][v]
            if v != s and v != t:
                actifs.append(v)

    def push(u, v):
        delta = min(e[u], c[u][v] - flot[u][v])
        if delta > 0:
            flot[u][v] += delta
            flot[v][u] -= delta
            e[u] -= delta
            e[v] += delta
            if v != s and v != t and e[v] == delta:
                actifs.append(v)
            return True
        return False

    def relabel(u):
        min_h = float('inf')
        for v in range(n):
            if c[u][v] - flot[u][v] > 0:
                min_h = min(min_h, h[v])
        if min_h < float('inf'):
            h[u] = min_h + 1

    cnt = 0
    while actifs:
        u = actifs.popleft()
        cnt += 1
        while e[u] > 0:
            pushed = False
            for v in range(n):
                if c[u][v] - flot[u][v] > 0 and h[u] == h[v] + 1:
                    if push(u, v):
                        pushed = True
                        break
            if not pushed:
                relabel(u)

    if verbose:
        print("Flot maximal =", sum(flot[s][v] for v in range(n)))
    return sum(flot[s][v] for v in range(n))

def afficher_table_bellman(snapshots, names):
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

    def print_line(left, mid, right):
        line = left
        for idx, w in enumerate(col_widths):
            line += '─' * (w + 2)
            line += mid if idx < len(col_widths)-1 else right
        print(line)

    def print_row(items):
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


def flot_cout_minimal(c, couts, s, t, flux_demandee, verbose=False):
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
    it = 1
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
                if dist[u] == float('inf'): continue
                for v in range(n):
                    if cap_res[u][v] > 0 and new_dist[u] + cout_res[u][v] < new_dist[v]:
                        new_dist[v] = new_dist[u] + cout_res[u][v]
                        new_parent[v] = u
                        updated = True
            dist, parent = new_dist, new_parent
            snapshots.append((dist.copy(), parent.copy()))
            if not updated:
                break

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
            if u == -1 or v in vus:  # Sécurité anti-boucle infinie et anti-cycle
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
            print(f"Chaîne augmentante {it} : {' -> '.join(names[u] for u, _ in chemin)} -> {names[t]} | flot potentiel = {delta}")

        # Mise à jour des flots, des coûts résiduels et du coût total
        for u, v in chemin:
            cap_res[u][v] -= delta
            cap_res[v][u] += delta
            if c[u][v] > 0:
                flot[u][v] += delta
                cout_total += delta * couts[u][v]
                cout_res[v][u] = -couts[u][v]  # Met à jour le coût résiduel inverse
            else:
                flot[v][u] -= delta
                cout_total -= delta * couts[v][u]
                cout_res[u][v] = -couts[v][u]  # Met à jour le coût résiduel inverse

        flux_courant += delta

        if verbose:
            print(f"\nGraphe résiduel après itération {it} :")
            afficher_matrice(cap_res, "capacités résiduelles")
            afficher_matrice(cout_res, "coûts résiduels")

        it += 1

    if flux_courant == flux_demandee:
        if verbose:
            print(f"\nAtteint le flot demandé = {flux_demandee} | coût minimal = {cout_total}\n")
        return flot, cout_total
    else:
        if verbose:
            print(f"\nImpossible d'atteindre le flot demandé = {flux_demandee} | flot courant = {flux_courant} | coût minimal = infini\n")
        return flot, float('inf')
