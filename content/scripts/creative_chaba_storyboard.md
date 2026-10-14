# Storyboard — « ماشي كل فيديو شباب يبيع » (~42 s, Reel 9:16)
Style: saved preset (full screen, key-word neon captions, ONE intro zoom, ONE light shake, ONE swoosh, pro SFX, no music, WhatsApp badge, no end card).
Hook montage: `"ماشي كل فيديو *شباب* يبيع"`

| # | Temps | Audio (voix + SFX) | Visuel | Transition |
|---|---|---|---|---|
| 1 | 0–3 s | « الكريياتيف كانت شابة… بصح ما جابت حتى نتيجة. » + hit (hook) | Gros plan visage (voiture) + carte hook en haut ; option : 1 s d'une vraie créa jolie en incrustation | Zoom-out d'intro + flash |
| 2 | 3–6 s | « وهادي بزاف تاع التجار يطيحو فيها. » + pop | Plan moyen, caption *التجار* | Cut (jump cut) |
| 3 | 6–10 s | « يحسبو الفيديو الشباب معناه بيع. لا خويا، ماشي ديما. » + pop | Caption *شباب ≠ بيع* ❌ ; la secousse légère sur « ماشي ديما » | Cut |
| 4 | 10–11 s | « علاش؟ » + sparkle | Plan serré, icône ❓ | Cut |
| 5 | 11–16 s | « أولاً، 3 الثواني الأولى… يسكرولي ويروح. » + swoosh | B-roll téléphone 3D qui scrolle (`[broll:rm_phone]`), caption *3 ثواني* ⏱️ | Swoosh (le seul) vers le b-roll, cut retour |
| 6 | 16–22 s | « ثانياً، الفيديو لازم يتفهم: واش هو المنتوج، لمن، واش يحلّلو. » + pop | Face caméra, caption *يتفهم* ; 3 icônes l'une après l'autre (📦 · 👤 · 💡) | Cut |
| 7 | 22–27 s | « ثالثاً، ساعات المشكل ماشي في الفيديو: السعر، العرض، الـ confirmation. » + pop | Captions *السعر* 💰 → *العرض* → *confirmation* 📞 | Cut |
| 8 | 27–34 s | « احكم بالأرقام، ماشي بعينيك: شحال حبس يتفرج، شحال كليكا، شحال كلفك الميساج. » + sparkle | Caption *الأرقام* 📈 ; option : capture floue du Gestionnaire de pubs (sans chiffres lisibles) | Cut |
| 9 | 34–38 s | « جرّب فيديو بسيط بالتليفون… ساعات البسيط هو اللي يبيع. » + pop | Caption *فيديو بسيط* 📱 ; option : 1 s filmée au téléphone (produit en main) | Cut |
| 10 | 38–42 s | « تابعني باش ما تفوتكش المعلومة الجاية، وحاب تبدا الـ sponsor ابعثلي واتساب. » + chime | Face caméra, sourire ; badge WhatsApp bas-gauche (déjà là) | Fin nette (pas de carte de fin) |

## Guide de montage (rythme · SFX · couleur)
**Rythme**
- 0–10 s (accroche) : rapide, un plan toutes les 1,5–2,5 s ; silences coupés serrés (~0,15 s).
- 10–34 s (explication) : plus posé, plans de 3–5 s ; garder ~0,3 s de respiration entre les idées ; un mot-clé à l'écran à la fois.
- 34–42 s (solution + CTA) : calme, plan continu, pas d'effet sur la dernière phrase.
- Zoom : un seul (intro). Secousse : une seule (« ماشي ديما »). Swoosh : un seul (b-roll téléphone).

**SFX (sfx_pro, pas de musique)**
| Moment | Son | Niveau |
|---|---|---|
| 0 s hook | hit grave doux | −14 dB sous la voix |
| chaque mot-clé | pop bulle | −20 dB |
| icônes (❓ 📦 👤 💡 📈) | sparkle 3 notes | −22 dB |
| entrée b-roll téléphone | swoosh | −16 dB |
| fin (CTA) | chime | −20 dB |
Voix : passe-haut 80 Hz (bruit voiture), débruitage léger, −14 LUFS ; les SFX ne doivent jamais couvrir un mot.

**Couleur / ambiance**
- Image : garder son filtre (`--grade none`) ; `pro` seulement si le visage est sombre ou le toit ouvrant brûle l'image. Jamais `cinema` (peau trop rose).
- Peau naturelle, contraste léger, pas de teinte violette sur l'image : le violet / bleu néon reste dans les graphismes (captions, icônes, badge).
- Ambiance : « conseil entre amis, sérieux » — lumière du jour, fond voiture, pas d'effets flashy pendant l'explication.

## Prompts IA (b-roll) — anglais, 9:16, sans texte
Style commun : `vertical 9:16, cinematic, deep night-violet background (#140B34), violet (#8B5CF6) and neon blue (#38BDF8) rim lighting, soft glow, shallow depth of field, premium, clean, no text, no logos, no watermark`
Négatif : `text, letters, numbers, logo, watermark, brand names, distorted hands, extra fingers, blurry face, low quality`

1. Scène 1 (créa jolie mais vide) — image/vidéo : "A stunning fashion product video playing on a smartphone screen held in one hand, glossy and beautiful, but the phone sits in an empty, silent room; a single violet spotlight, dust particles floating, feeling of beautiful but unnoticed, slow push-in, 4 seconds" + style commun
2. Scène 5 (scroll) — vidéo : "Close-up of a thumb scrolling fast through a vertical social media feed on a smartphone, colorful posts blurring by in motion blur, one post flies past without stopping, neon blue reflections on the screen glass, 3 seconds" + style commun
3. Scène 6 (clarté) — image : "Three floating glass icons in a row: a gift box, a person silhouette, a light bulb, frosted violet glass with neon blue edges, isometric, studio lighting" + style commun
4. Scène 7 (prix / offre / confirmation) — image : "A price tag, a ribbon-wrapped offer box and a ringing phone floating above a dark violet surface, glossy 3D render, soft neon reflections" + style commun
5. Scène 8 (les chiffres) — vidéo : "Abstract analytics dashboard made of glowing bars and line charts rising, holographic, floating in dark violet space, numbers unreadable and blurred, slow orbit camera, 4 seconds" + style commun
6. Scène 9 (vidéo simple au téléphone) — vidéo : "Handheld smartphone filming a simple product in natural daylight on a wooden table, the phone screen shows the same shot, authentic, unpolished, warm daylight with a subtle violet rim light, 3 seconds" + style commun
Règles : pas de faux clients, pas de faux résultats ni de faux chiffres lisibles, pas de logos de marques (Meta, Instagram…).
