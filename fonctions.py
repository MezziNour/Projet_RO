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

def afficher_matrice_FF(titre, c, flot):
    # Affiche la matrice de flot sous la forme x/y, où x = flot actuel, y = capacité.
    n = len(c)
    cell_width = 9  # Largeur constante pour chaque cellule

    print(f"\nMatrice {titre} :")
    print("     ", end="")
    for j in range(n):
        print(f"{'v'+str(j+1):^{cell_width}}", end="│")
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
def plargeur_chaine_améliorante(c, flot, s, t, parent):
    n = len(c)
    visite = [False] * n
    file = deque()
    file.append(s)
    visite[s] = True
    parent[s] = -1

    print("\nParcours en largeur pour chercher une chaîne améliorante :")

    while file:
        u = file.popleft()
        for v in range(n):
            residuel = c[u][v] - flot[u][v]
            if not visite[v] and residuel > 0:
                parent[v] = u # Met à jour le tableau des parents quand un chemin est trouvé
                visite[v] = True
                file.append(v)
                print(f"    v{u+1} -> v{v+1} (capacité résiduelle = {residuel})")
                if v == t:
                    return True # Un chemin jusqu'au sommet final est trouvé
    return False # Aucun chemin trouvable

# Algorithme de Ford-Fulkerson 
def ford_fulkerson(c, s, t):
    n = len(c)
    flot = [[0]*n for _ in range(n)] # Initialisation du flot à 0
    parent = [-1] * n
    flot_max = 0
    i = 1 # Compteur d'itérations

    print("\nLe graphe résiduel initial est le graphe de départ.")
    
    while plargeur_chaine_améliorante(c, flot, s, t, parent):
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

        print(f"\nChaîne améliorante {i} : " + " -> ".join([f"v{u+1}" for u, _ in chemin] + [f"v{t+1}"]) + f" de flot : {flot_ajoute}")

        # Mise à jour des flots dans la matrice
        for u, v in chemin:
            flot[u][v] += flot_ajoute
            flot[v][u] -= flot_ajoute # Flot inverse pour maintenir la conservation

        flot_max += flot_ajoute
        afficher_matrice_FF(f"résiduelle {i}", c, flot)
        i += 1
        
    print("\nOn ne peut plus accéder au dernier sommet. Fin de l'agorithme.") 
    
    afficher_matrice_FF("finale", c, flot)
    
    return flot_max

def pousser_réétiqueter(c, s, t):
    n = len(c)
    # Initialize flow and height
    flow = [[0] * n for _ in range(n)]
    height = [0] * n
    excess = [0] * n
    height[s] = n

    # Initialize preflow: saturate all edges from source
    for v in range(n):
        if c[s][v] > 0:
            flow[s][v] = c[s][v]
            flow[v][s] = -flow[s][v]
            excess[v] = c[s][v]
            excess[s] -= c[s][v]

    # Afficher la matrice de flot initiale
    i = 0
    afficher_matrice_FF(f"initiale {i}", c, flow)
    
    def push(u, v):
        delta = min(excess[u], c[u][v] - flow[u][v])
        flow[u][v] += delta
        flow[v][u] -= delta
        excess[u] -= delta
        excess[v] += delta

    def relabel(u):
        min_height = float('inf')
        for v in range(n):
            if c[u][v] - flow[u][v] > 0:
                min_height = min(min_height, height[v])
        if min_height < float('inf'):
            height[u] = min_height + 1

    def find_excess_vertex():
        candidates = [u for u in range(n) if u != s and u != t and excess[u] > 0]
        if not candidates:
            return None
        # Sort by height (descending) and index (ascending)
        candidates.sort(key=lambda u: (-height[u], u))
        return candidates[0]

    while True:
        i += 1
        u = find_excess_vertex()
        if u is None:
            break

        pushed = False
        # Try to push flow
        for v in range(n):
            if c[u][v] - flow[u][v] > 0 and height[u] == height[v] + 1:
                push(u, v)
                pushed = True
                print("\n---------------------------------------------------------------------------------------\n")
                print(f"Pousser de v{u+1} à v{v+1} : {flow[u][v]} unités")
                if v == t:  # Prioritize pushing to t
                    break

        if not pushed:
            relabel(u)
            print("\n---------------------------------------------------------------------------------------\n")
            print(f"Réétiqueter v{u+1} : nouvelle hauteur = {height[u]}")

        # afficher la matrice de flot
        afficher_matrice_FF(f"itération {i}", c, flow)

    return sum(flow[s][v] for v in range(n))