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
    # Initialisation des variables
    flot = [[0] * n for _ in range(n)]
    hauteur = [0] * n
    excedent = [0] * n
    hauteur[s] = n

    # Initialisation du pre-flot : saturer les arcs sortants du sommet source
    for v in range(n):
        if c[s][v] > 0:
            flot[s][v] = c[s][v]
            flot[v][s] = -flot[s][v]
            excedent[v] = c[s][v]
            excedent[s] -= c[s][v]

    # Afficher la matrice de flot initiale
    i = 0
    afficher_matrice_FF(f"initiale {i}", c, flot, hauteur)
    
    def pousser(u, v):
        delta = min(excedent[u], c[u][v] - flot[u][v])
        flot[u][v] += delta
        flot[v][u] -= delta
        ancien_excedent_v = excedent[v]
        excedent[u] -= delta
        excedent[v] += delta
         # Affichage adapté pour les valeurs négatives
        if delta < 0:
            print(f"Pousser de v{v+1} à v{u+1} : {ancien_excedent_v - excedent[v]} unités")
        else:
            print(f"Pousser de v{u+1} à v{v+1} : {delta} unités")

    def reetiqueter(u):
        min_hauteur = float('inf')
        for v in range(n):
            if c[u][v] - flot[u][v] > 0:
                min_hauteur = min(min_hauteur, hauteur[v])
        if min_hauteur < float('inf'):
            hauteur[u] = min_hauteur + 1

    def trouver_excedents():
        candidats = [u for u in range(n) if u != s and u != t and excedent[u] > 0]
        if not candidats:
            return None

        # Sort candidates by height (descending) and then by index (ascending)
        candidats.sort(key=lambda u: (-hauteur[u], u))
        return candidats[0]

    while True:
        i += 1
        print(f"\nItération {i} :")
        u = trouver_excedents()
        if u is None:
            print("Aucun sommet avec excédent trouvé. Fin de l'algorithme.")
            afficher_matrice_FF(f"Finale {i}", c, flot, hauteur)
            break

        poussee = False
        # Pousser
        for v in range(n):
            if c[u][v] - flot[u][v] > 0 and hauteur[u] == hauteur[v] + 1:
                pousser(u, v)
                poussee = True
                if v == t:  # Prioriser le flot vers t
                    break

        # Réétiqueter
        if not poussee:
            reetiqueter(u)
            print(f"Réétiqueter v{u+1} -> nouvelle hauteur = {hauteur[u]}")

        # afficher la matrice de flot
        afficher_matrice_FF(f"itération {i}", c, flot, hauteur)

    return sum(flot[s][v] for v in range(n))