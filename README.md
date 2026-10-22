# Syster Descrambler

Outil expérimental de restauration de vidéos issues de l'ancien
brouillage analogique Syster/Nagravision (permutation de lignes).
Il reconstitue l'ordre des lignes par analyse de continuité de l'image,
sans clé.

## Utilisation
    pip install -r requirements.txt
    python descramble.py entree.mp4 sortie.mp4

Option : `--flip` si l'image sort à l'envers.

Pour récupérer le son d'origine :

    ffmpeg -i sortie.mp4 -i entree.mp4 -map 0:v -map 1:a -c copy final.mp4

## Limites
Résultats partiels sur des vidéos recompressées (ex. YouTube).

## Avertissement
À utiliser uniquement sur des enregistrements dont vous détenez les droits
(archives personnelles, restauration). Aucune vidéo ne doit être publiée
dans ce dépôt.
