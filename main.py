from fonctions import *

def main():
    #generateTraces()
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
            print("1. Edmonds-Karp")
            print("2. Pousser - Réétiqueter")
            choix = input("Votre choix (1 ou 2) : ")

            if choix == "1":
                valeur_flot = ford_fulkerson(capacites, s, t, verbose=True)
            elif choix == "2":
                valeur_flot = pousser_reetiqueter(capacites, s, t, verbose=True)
            else:
                print("Choix invalide.")
                continue

            print(f"\nValeur du flot maximal : {valeur_flot}")

        elif type_probleme == "flot_min":
            print("\nProblème détecté : Flot à coût minimal")
            n, capacites, couts = lire_flot_min(chemin)
            afficher_matrice(capacites, "Matrice des capacités", couts, "Matrice des coûts")

            s = 0
            t = n-1

            flux_demandee = None
            while flux_demandee is None:
                try:
                    flux_demandee = int(input("\nEntrez la valeur de flot souhaitée : "))
                except ValueError:
                    print("Veuillez entrer un entier valide.")

            cout_total = flot_cout_minimal(capacites, couts, s, t, flux_demandee, verbose=True)
            print(f"\nRésultat : Coût minimal pour un flot de {flux_demandee} = {cout_total}")

        else:
            print("Problème inconnu.")

        continuer = input("\nVoulez-vous résoudre un autre problème ? (o/n) : ").lower()
        if continuer != "o":
            print("\nFin du programme. Merci !")
            break

if __name__ == "__main__":
    main()
