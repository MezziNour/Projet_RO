from fonctions import *

def main():
    while True:
        print("Résolution de problème de flot")
        numero = input("Entrez le numéro du fichier (0-10) : ").strip()
        chemin = f"data/{numero}.txt"

        try:
            type_probleme, n = detecter_type_probleme(chemin)
        except ValueError as e:
            print("Erreur :", e)
            continue

        if type_probleme == "flot_max":
            print("\nProblème détecté : Flot maximal")
            n, capacites = lire_flot_max(chemin)
            afficher_matrice(capacites, "Matrice des capacités")
            s = 0
            t = n - 1

            print("\nChoisissez l'algorithme :")
            print("1. Ford-Fulkerson")
            print("2. Pousser - Réétiqueter")
            choix = input("Votre choix (1 ou 2) : ")

            if choix == "1":
                valeur_flot = ford_fulkerson(capacites, s, t)
            #elif choix == "2":
                #fonction de l'algo pousser-réétiqueter
            else:
                print("Choix invalide.")
                continue

            print(f"\nValeur du flot maximal : {valeur_flot}")
            
        elif type_probleme == "flot_min":
            print("\nProblème détecté : Flot à coût minimal")
            n, capacites, couts = lire_flot_min(chemin)
            afficher_matrice(capacites, "Matrice des capacités")
            afficher_matrice(couts, "Matrice des coûts")

        else:
            print("Problème inconnu.")

        continuer = input("\nVoulez-vous résoudre un autre problème ? (o/n) : ").lower()
        if continuer != "o":
            print("\nFin du programme. Merci !")
            break

if __name__ == "__main__":
    main()
