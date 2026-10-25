"""Télécharge ou met à jour toutes les données du projet."""
import time
import download_wather
import download_elec_consomation
import argparse



def main():
    etapes = {
            "energie": ("Consommation électrique (éCO2mix)", download_elec_consomation.main),
            "meteo": ("Météo ERA5 (Open-Meteo)", download_wather.main),
        }
    
    parser = argparse.ArgumentParser(description="Télécharge les données du projet.")
    parser.add_argument("--seulement", choices=list(etapes.keys()),
                        help="ne télécharger qu'une seule source")
    args = parser.parse_args()

    
    a_lancer = [etapes[args.seulement]] if args.seulement else list(etapes.values())
    erreurs = []

    for nom, fonction in a_lancer:
        print(f"\n=== {nom} ===")
        debut = time.perf_counter()
        try:
            fonction()
        except Exception as e:
            print(f"❌ Échec : {e}")
            erreurs.append(nom)
        else:
            print(f"✅ Terminé en {time.perf_counter() - debut:.0f} s")

    if erreurs:
        raise SystemExit(f"\nÉtapes en échec : {', '.join(erreurs)}")
    print("\nToutes les données sont à jour.")


if __name__ == "__main__":
    main()