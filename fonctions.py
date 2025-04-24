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
