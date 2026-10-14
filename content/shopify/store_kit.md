# Store kit — VIOLET Vogue (Shopify, لبسة النسا، فخم، الهوية تاع Mustafa)

Nom de travail : **VIOLET Vogue** (proposé par l'outil de noms Shopify ; vérifier qu'il est libre avant de l'utiliser comme marque).
Tout ce qui est entre [crochets] = à compléter par Mustafa (prix, délais, tarifs). Rien n'est inventé.

## 1. Visuels (ce dossier)
| Fichier | Où le mettre dans Shopify |
|---|---|
| `logo_store.png` | Thème → En-tête → Logo (fond sombre) |
| `logo_store_dark.png` | Logo sur fond blanc (factures, e-mails) |
| `favicon.png` | Thème → Paramètres → Favicon |
| `banner_desktop.jpg` (1920×900) | Accueil → Bannière image (ordinateur) |
| `banner_mobile.jpg` (1080×1350) | Accueil → Bannière image (mobile) |
Regénérer : `python3 tools/shopify_kit.py`

## 2. Couleurs & polices du thème (Thème → Personnaliser → Paramètres du thème)
- Fond : `#140B34` (nuit violet) · Cartes / sections : `#2A1B5E` · Texte : `#EDE9FE`
- Boutons : `#8B5CF6` (violet) · Liens / accents : `#38BDF8` (bleu néon)
- Titres : **Sora** (si absente de la bibliothèque Shopify : Montserrat) · Texte : une sans-serif simple de la bibliothèque.

## 3. Navigation (Boutique en ligne → Navigation → Menu principal)
Nouveautés · Robes · Ensembles · Abayas · Promotions · Contact

## 4. Collections (Produits → Collections)
| Collection | Description courte |
|---|---|
| Nouveautés | Les dernières pièces arrivées en boutique. |
| Robes | Des robes élégantes pour chaque occasion. |
| Ensembles | Des ensembles assortis, prêts à porter. |
| Abayas | Des abayas fluides et raffinées. |
| Promotions | Des pièces sélectionnées à prix réduit. |

## 5. Page d'accueil (sections dans l'ordre)
1. **Bannière** : « NOUVELLE COLLECTION — L'élégance qui vous ressemble » · bouton « DÉCOUVRIR » → Nouveautés
2. **Barre d'annonce** (tout en haut) : « Paiement à la livraison • Livraison partout en Algérie »
3. **Collection en vedette** : Nouveautés (8 produits)
4. **Liste de collections** : Robes · Ensembles · Abayas
5. **Texte avec image** — titre « Pourquoi VIOLET Vogue ? » :
   - Vous payez à la réception de votre commande.
   - Nous vous appelons pour confirmer avant l'envoi.
   - Une équipe disponible sur WhatsApp pour vous conseiller (taille, couleur).
6. **Avis clientes** : à remplir uniquement avec de vrais avis (photos / messages de clientes, avec leur accord).
7. **Contact** : WhatsApp [numéro de la boutique]

## 6. Pages (Boutique en ligne → Pages)
**À propos**
> VIOLET Vogue, c'est une boutique en ligne de mode féminine pensée pour les femmes qui aiment l'élégance au quotidien. Chaque pièce est choisie avec soin pour sa coupe, sa matière et son confort. Commandez en quelques clics et payez à la livraison.

**Livraison & retours**
> Nous livrons partout en Algérie. Délai : [X à Y jours] selon la wilaya. Frais de livraison : [à domicile : … DA / point relais : … DA].
> Avant l'envoi, nous vous appelons pour confirmer votre commande.
> Échange possible sous [X jours] si l'article n'a pas été porté et garde son étiquette. Contactez-nous sur WhatsApp.

**Paiement à la livraison**
> Vous ne payez rien en ligne : vous réglez en espèces au livreur à la réception de votre colis.

**Contact**
> WhatsApp : [numéro] · Instagram : [@compte de la boutique] · Réponse rapide de [heure] à [heure].

## 7. Fiche produit (modèle à copier pour chaque article)
**Titre** : [Type] [Nom du modèle] – [Couleur]  (ex. « Robe Layla – Lilas »)
**Description** :
> [Une phrase sur l'effet : élégante, fluide, confortable…]
> • Matière : [ … ]
> • Coupe : [ … ]
> • Tailles : [S / M / L / XL] — Guide des tailles : [ … ]
> • Couleurs disponibles : [ … ]
> • Entretien : [ … ]
> Paiement à la livraison • Livraison partout en Algérie.
**Photos** : 4 minimum — face, dos, détail tissu, photo portée. Fond uni, lumière du jour.
**Variantes** : Taille + Couleur. **Prix** : [prix en DA] (prix barré seulement s'il y a une vraie promo).

## 8. Réglages (Paramètres)
- **Paiements** → Moyens de paiement manuels → **Paiement à la livraison (COD)**.
- **Expédition et livraison** → créer une zone **Algérie** → tarifs [domicile / point relais].
- **Paiement (Checkout)** → numéro de téléphone **obligatoire** (pour la confirmation).
- **Marchés / Devise** : Algérie, DZD.
- **Politiques** : coller le texte « Livraison & retours ».
- **Meta Pixel** : installer l'app Facebook & Instagram (Meta) et connecter le Pixel avant de lancer la pub.
