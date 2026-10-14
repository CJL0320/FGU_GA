# Mustafa — profile & reels brief

## Who
- Mustafa, e-commerce content creator + digital services (Birkhadem, Algiers).
- Instagram link: https://www.instagram.com/kabli_ms
- Instagram handle (confirmed by Mustafa, matches the link): @kabli_ms
- Phone: 0799858948
- WhatsApp: 0550205464
- Services: Meta Ads, e-commerce store ops (Shopify, Foorweb, Builddz, YouCan), digital support.
- Goal: grow his own brand and get better at editing Reels. Claude acts as his Reels editing + content copilot.

## CURRENT DEFAULT RECIPE (latest preferences — these win over older notes below)
- VISUAL IDENTITY = PALETTE C "violet + neon blue" + new K+M logo + new fonts (Readex Pro / Sora), chosen by Mustafa 2026-10-07 ("نغيرو هوية بصرية" -> بنفسجي + أزرق نيون, اللوغو, الخطوط). See "Brand colors — PALETTE C" below. Everything (captions, icons, badge, b-roll, end card, identity pack) uses it; palette B (navy + orange) is retired.
- Brand badge (his request): top-left for the whole reel (after the hook), a 3D coin with the K+M logo that spins around Y every 4 s, violet rim with a neon-blue glow, + fixed '@kabli_ms / E-COMMERCE • SPONSOR' pill. Remotion composition BrandBadge -> assets/_generated/rm_badge.mov (ProRes 4444 alpha), looped by edit_reel.py; `--no-badge` to hide.
- Remotion (Mustafa asked for it) = the motion-graphics engine for b-roll: project in remotion/ (React, `npm install` once, renders with the preinstalled headless Chromium). Tags: `[broll:rm_cube]` real CSS-3D product box, `[broll:rm_funnel]` animated sales funnel (إعلان → رسائل → طلبيات), `[broll:rm_phone]` 3D phone with WhatsApp messages, `[doc:TEXT]` documentary paper card with neon-blue highlighter + grain. `EndCard` = animated end card (see below). For rm_cube / rm_funnel the cue's key words become the graphic's title (no caption/icon drawn on top); doc cards with the same words also hide the caption. Remotion license: free for individuals and companies up to 3 people.
- Other illustration/motion b-roll (Python, tools/motion_gfx.py): `[broll:funnel]`, `[broll:merchant]` neon-rim merchant silhouette ("Personal Branding" style).
- Caption look (his reference "Personal Branding", palette C variant B chosen on a real frame): first word(s) in a big bold sans (Readex Pro Bold for Arabic / Sora ExtraBold for Latin) with an ice-blue -> neon-blue -> violet gradient fill, wide violet glow + tight neon-blue glow, light ice halo and glossy top half (constants CAP_* in edit_reel.py); last word in white handwriting script (Aref Ruqaa for Arabic, Great Vibes for Latin) overlapping it with a soft white glow. One-word captions = neon bold only. Captions stay inside the frame; on b-roll cues they sit lower.
- Caption placement: NEVER on his face — each caption goes just below or just above the face, wherever there is room (auto face detection at the cue's start AND middle because he moves, `caption_y`; uses the caption's visible rows, not its glow padding; if neither side fits it goes to the side with more room); in the cards layout it also stays clear of the small face card. Arabic script word sits a bit lower (`SCRIPT_DY_AR`) so it never hides the dots of the bold line (e.g. مليحة). Start of the reel (his rule 2026-10-07, keep the rest of the style as is): the hook card has its script word on its own row; captions/icons only start after the hook card (2.7 s); captions stay below the top-left @kabli_ms badge and above the WhatsApp badge; if an icon would sit on a caption, that caption is rendered narrower so the icon fits beside it.
- Icons = NEON GLASS style from his 3 violet reference images (house / doctor / person tiles, sent 2026-10-07): `tools/neon_icons.py` `tile()` — dark violet glass squircle with violet light top-left and a soft diagonal beam, thin neon-blue -> violet -> pink rim with glow, soft lavender-white 3D pictogram (Material Icons Round, bright outline, bevel), sparkle + dot, aura + shadow; emoji -> icon map `EMOJI_ICON` (✅❌💸💰🚨🔥👇💬🛒📦🤝📈📱🏠💡📣🏪👤⭐🚀🎯). Older description: dark night-violet glass squircle, glowing violet->neon-blue gradient rim, violet inner glow, diagonal sheen, clean white pictogram with a neon-blue glow (check, cross, $, warning, flame, box, cart, chat, arrow), small sparkle; pops in, sways in 3D, floats, glow pulses; placed next to the caption. Code: `render_icon3d_mov` (old glass version kept as `render_icon_glass_mov`).
- SAVED STYLE = reel3_v2_motion (Mustafa: "احفظ آخر تعديل وخدم بهذاك الأسلوب"). Run `tools/reel_mustafa.sh videos/reelN.mov subs/reelN.srt "hook"`; .srt template = subs/reel3_v7.srt (latest: key phrases starred, Remotion tags [broll:rm_phone] [broll:rm_funnel] [broll:rm_cube] [doc:TEXT], [circle], [ding], emoji); older one subs/reel3.srt.
- Upload: always the original .mov/.mp4 via GitHub (`main`); the chat turns videos into stills/GIFs (no sound) — never edit from those.
- Captions: KEY WORDS ONLY (`--keywords-only`), big neon captions (look above) drawn as images; `--accent 38BDF8` (neon blue) only colours a Latin hook's *key word*. Star whole short phrases (`*البيع ما كاش*`) so small words are never dropped. French words he says are written in French (confiance, créative, cliente, messages).
- Words come from his real speech: `tools/transcribe.py` (Whisper large-v3 on cleaned audio) gives timings + a draft; pick only clearly heard key words, ask him when unsure.
- Colours: keep his filter (`--grade none`) unless he asks; `pro` if the face lighting is bad. Never `cinema` (skin too pink).
- Motion: ONE zoom-out at the start only (`--zoom-mode intro`, default); ONE light shake (at the hook only); whoosh max ONCE per reel; click only on key words.
- Hook: `--hook` card in the top safe zone for the first 2.6 s, built from his own message (no invented numbers or promises).
- B-roll: 3D clips (`[broll:product3d]`, `[broll:trust3d]`, `[broll:chat3d]`), `[circle]` on his face, emoji; real filmed b-roll from him is better when available.
- Music: `--music beat --bpm 100` (generated, royalty-free) under the voice.
- Output: 1080x1920 (9:16). If > 30 MB, also make a `_send.mp4` copy (crf 25) to send in the chat.
- Layout: Mustafa CHOSE the Motion / After-Effects card style (`--layout cards`, now the tool default); `--layout full` only if he asks. Brand palette C (violet + neon blue) for end card, b-roll, badge, icons, identity pack.
- End card (3 s): animated Remotion `EndCard` (logo pops with a neon glow, @kabli_ms, "راسلني على واتساب", WhatsApp pill 0550 20 54 64 with a violet->blue border and light sweep, tagline). `--tagline` = the small line at the bottom. Cached in assets/_generated/rm_endcard_<hash>.mp4; falls back to the plain card if Remotion can't run.
- Cache: assets/_generated (git-ignored) is wiped and rebuilt automatically when `PALETTE_ID` in edit_reel.py changes — bump it after any brand change.
- Example: `python3 tools/edit_reel.py videos/reel3.mov --srt subs/reel3.srt --grade none --keywords-only --accent 38BDF8 --hook "عندك *créative* مليحة وما تبيعش؟" --music beat --bpm 100 --out videos/reel3_v1.mp4`

## Language
- User writes in Algerian Darija (Arabic script). Reply in Darija, short and practical.
- On-screen text language for reels: to confirm per reel (Darija / French / mix).

## Tone of voice
- Professional but friendly, direct, practical, results-driven, trustworthy.
- Keywords: growth, performance, conversions, sales, tech support, stability, real results.
- Avoid: exaggeration/hype, unexplained jargon, stiffness.
- Terms to keep consistent: Meta Ads, ROAS, Foorweb, Builddz, Shopify, Landing Pages.

## Brand colors — PALETTE C "violet + neon blue" (chosen by Mustafa 2026-10-07; replaces palette B navy + orange)
- Night Violet #140B34 — backgrounds
- Deep Violet #2A1B5E — cards, depth
- Violet #8B5CF6 — main brand colour (logo arrow start, rims, chips, glows)
- Neon Blue #38BDF8 — neon accent (caption gradient, glows, progress bar, highlighter, Latin hook key word)
- Tints: Lavender #C4B5FD, Ice #BAE6FD, Cream #EDE9FE; White #FFFFFF text; Ink #0B0620 shadows
- Signature gradient: violet #8B5CF6 -> neon blue #38BDF8. Older notes below that say "orange"/"green accent" now mean violet / neon blue.
- In code: edit_reel.py `BRAND` (navy/blue/accent/neon), `VIOLET`/`BLUE`/`NIGHT`, `CAP_*`; remotion/src/brand.tsx `C`; make_logo.py; make_identity.py; gen_assets.py / broll3d.py / motion_gfx.py.
- Palette B logo/files are kept in assets/brand/archive_palette_b/ (in case he wants to go back).

## Fonts (identity C)
- Readex Pro Bold — Arabic headlines + captions; Readex Pro Medium — Arabic body.
- Sora ExtraBold — Latin headlines, numbers, @kabli_ms; Sora SemiBold — labels.
- Script accent (the overlapping white word in captions): Aref Ruqaa (Arabic), Great Vibes (Latin).
- Static .ttf instances made from the Google variable fonts with fontTools (tools/fonts). Sora/Readex have no "→" glyph: use "»".

## Reel structure (default)
- 0-3s hook (number / problem / result), 3-10s problem or story, 10-22s solution in 3 points with on-screen text, last 5-8s CTA.
- Fast cuts (1-2s), big subtitles (most watch muted), light zoom on key words, quiet music under voice.
- Export: 1080x1920, H.264, ~-14 LUFS audio.

## Workflow
- Videos uploaded to videos/ in this repo; Claude edits with FFmpeg and gives cut-by-cut plans for CapCut.
- Source in videos/reelN.*, outputs as videos/reelN_vX.mp4.

## Audience & offer (confirmed)
- Audience: beginner online merchants.
- Offer: Meta Ads + store creation for beginners.
- Footage: Mustafa talks to camera (talking-head).
- Language: mix (Darija + French) for speech and on-screen text.

## Content identity (confirmed by Mustafa)
- Mustafa talks about e-commerce and gives practical e-commerce tips (not only selling services).
- All his content and Reels editing must keep the SAME consistent style (same tone, colors, subtitle look, end card, pacing) so the account feels recognisable.
- He wants to keep improving himself: Claude should explain each editing choice in simple words, suggest one improvement per reel, and track what he learns.
- Note: the old perfume unboxing video (reel1) was only a test, not his niche.

## Niche & service (clarified by Mustafa)
- Niche: advising online merchants (e-commerce) and running their sponsoring ("sponsor" / paid ads on Meta) for them.
- His core service = sponsoring (Meta Ads management for merchants). In Algerian usage "sponsor/صبونصور" means paid ads.
- Audience = online merchants (beginners). Content = tips on e-commerce + ads, with the sponsoring service as the call to action.
- Use his word "sponsor / سبونسور" in on-screen text and CTAs, alongside "Meta Ads".

## Caption & color style (reference: @nazih_motivation reels, chosen by Mustafa — take the technique, not a copy)
- Captions: huge bold condensed font (Anton), UPPERCASE for Latin/Arabizi Darija ("TKUN FL CLAN TA3I"), centered, lower-middle of the frame (~60-65% height), 2-3 short lines, max ~4 words per screen.
- Key word of each phrase gets an accent colour (brand Growth Green #38A169) and is slightly bigger; pop-in animation (small scale-up, 0.1s).
- Arabic captions: DejaVu Sans Bold, no letter spacing (spacing breaks Arabic joining), same position, accent word coloured.
- Emoji: write them in the .srt (e.g. `... 🔥`); the tool strips them from the text and overlays them as colour PNGs near the top of the frame (clear of face and caption), max 2 per caption.
- Zoom: alternating punch zoom-OUT (1.14x -> 1.0 in 0.6s) and slow push-IN (1.0 -> 1.10) restarted at every caption / jump cut. Disable with `--no-zoom`; emoji with `--no-emoji`.
- Colour grade: warm golden/orange, a bit more contrast + saturation, soft dark vignette (face lit, edges dark). Option `--grade natural` if the footage is already warm.
- Extras seen in the reference (to add later when assets exist): light-leak/transition flashes on punchy moments, falling-money overlay for money topics, cutout face over blurred warm background.
- Tool: `python3 tools/edit_reel.py videos/reelN.mov --srt subs.srt` — mark accent words with *stars* in the .srt (e.g. `SPONSOR MA YJIBLEK *TLABAT*`).

## Style reference #2 (screen recording of a second reel, `videos/1005 (2).mov` on main, 18s, 640x480)
- Same creator style: talking head in front of a **green screen / neon-green background**, subject centred, big caption in the lower-middle.
- Captions: one or two words at a time (SALEM, ARWAH, NHOTEK, YBDA, 3ID RASSEK, SUIVI-MOI, 1 MIN), huge white bold with soft glow; emphasis words get an effect (red text, glowing green text, text sitting behind the hand/body).
- B-roll inserts for 1-2 s to illustrate words: newspaper "DAILY MAIL" clip, red/city clip, small icons (speaker, mail) next to the word.
- Punchy moments: close face zoom with orange spark/fire particles, flashes, quick zoom in/out every phrase.
- Takeaway for Mustafa's reels: very short caption chunks (1-3 words), more B-roll/icons per sentence, a glow on captions, sparks/flash on the key claim.

## Effects toolkit (built by Claude, no downloads needed)
- Tags go at the end of a cue in the .srt: `[sparks]` violet/neon-blue sparks, `[flash]` white flash, `[leak]` violet/blue light leak, `[money]` falling dollars, `[broll:growth_chart]` full-frame b-roll clip for the cue, `[icon:NAME]` PNG icon from assets/icons.
- Generated assets live in `assets/_generated/` (git-ignored; rebuilt automatically or with `python3 tools/gen_assets.py`).
- Mustafa's own files go in `assets/sparks/`, `assets/broll/`, `assets/icons/` (uploaded via GitHub on `main`); file name = tag name, and his files win over generated ones. Only use royalty-free sources (Pexels, Pixabay, Mixkit, CapCut library).
- Example cue: `00:00:02,600 --> 00:00:05,500` / `MASHI MOSHKIL FL *META* 🔥 [flash]`

## Content message (Mustafa, reel2 "work with your face")
- In this era, to sell you must work with your FACE: videos of people holding the product in hand, talking about it and selling it, so people trust them.
- Captions for reel2 are key phrases paraphrased from his summary (subs/reel2.srt), not word-for-word; whisper cannot transcribe Algerian Darija reliably, so Mustafa types the words (tools/transcribe.py only gives timings).

## Editing upgrades (reel2 v3)
- Captions cut to 1-3 words each (~1.5-2s), accent word green; splitting a phrase gives a faster rhythm.
- Auto SFX: soft whoosh on every caption change, pop when an emoji/effect appears (`--no-sfx` to disable). Green progress bar on top (`--no-bar`).
- End card tagline via `--tagline "BACH NAS DIR FIK ETHIQA"` (used when the trust line doesn't fit in the video).
- Command: `python3 tools/edit_reel.py videos/reel2.mov --srt subs/reel2_v3.srt --tagline "..." --out videos/reel2_final_v3.mp4`
- Next ideas: royalty-free background music under the voice, B-roll of products/stores, stronger hook in the first 2 seconds.

## Meta Ads tips (general; Mustafa asked to remove his campaign results — do not mention or reuse them)
- Conversations are not sales: always track conversations -> orders -> delivered, and quote the real cost per order.
- Budget: raise ~20% every 2-3 days (not +50% at once), don't edit audience/creative of a winning ad, add a second ad with a new hook instead, answer messages within 5 minutes, switch creative if frequency > 3, merge similar ad sets.

## Hook library (from Mustafa's brief; use in the first 2-3 seconds, Darija/French mix)
- Problem & solution: "تحرق البادجت في السبونسور بلا مبيعات؟ هذا هو الحل" / "راك تخسر في Facebook Ads؟ شوف هذه الطريقة".
- Shock / myth-busting: "تخدم متجرين في نفس الوقت = غلط يضيع أرباحك" / "كل ما تعرفه على الـ Pixel غلط".
- Numbers / proof: only with real numbers Mustafa gives for that reel (none stored here).
- Curiosity gap: "السر لي يخلي الكليان يكمل الشراء" / "3 أخطاء تدمر متجرك على Foorweb أو Builddz".
- Niche call-out: "إذا راك تخدم E-commerce في الجزائر، الفيديو هذا ليك" / "لكل صاحب صفحة ودروبشيبر، اسمع مليح".
- Script table format for a new reel: seconds | on-screen text hook | voiceover | visuals/B-roll/transitions | SFX. Typical length 30-45 s.
- B-roll ideas: screen recordings of Meta Ads Manager, Foorweb / Builddz dashboards, zoom-in on key buttons.

## Decisions taken (were open points)
- Handle: @kabli_ms (confirmed; "kabli.ms" in a brief was a typo).
- Palette: C chosen 2026-10-07 (violet #8B5CF6 + neon blue #38BDF8 on night violet #140B34); palette B retired.
- Fonts: Readex Pro (Arabic) + Sora (Latin) everywhere; Aref Ruqaa / Great Vibes only for the script word in captions.
- Logo: new K+M monogram with a violet->blue rising arrow in a neon app-icon squircle (assets/brand/logo_*).

## Logo (identity C, made by Claude, `python3 tools/make_logo.py` -> assets/brand/)
- K+M monogram with rounded strokes; the K's upper arm is a rising arrow in a violet -> neon-blue gradient; app-icon squircle (dark violet glass + violet->blue neon rim), same family as his reel icons.
- Files: logo_mark (app icon), logo_mark_white (videos / dark backgrounds / badge coin), logo_mark_dark (light backgrounds), logo_profile.png (Instagram profile picture, circle-safe), logo_horizontal.png (banner), SVG sources. remotion/public/logo_white.png + logo_icon.png are copies.
- Old palette B logo + Canva candidate (design DAHXMVIM1B8) archived in assets/brand/archive_palette_b/.

## Visual identity pack for e-commerce tips (tools/make_identity.py -> assets/brand/identity/)
- brand_board.png (palette C, fonts, sample neon caption, rules), reel_cover_template.png (1080x1920), tip_post_template.png (1080x1350), highlight_{tips,ads,store,results,me,contact}.png (IG highlight covers in the neon glass icon style, no text: bulb / megaphone / storefront / chart / person / chat). Icon sheet: `python3 tools/icons_preview.py` -> assets/brand/icons_preview.png + icon_check_anim.gif.
- Fonts in tools/fonts: Sora ExtraBold/SemiBold (Latin), Readex Pro Bold/Medium (Arabic), Aref Ruqaa / Great Vibes (script). Older fonts (Anton, Montserrat, Tajawal, Lalezar...) stay in the folder but are no longer the brand fonts. Pillow+raqm shapes Arabic itself: do NOT use arabic-reshaper/bidi.
- Rules: key words only (neon ice-blue -> violet + one script word), caption max 3 words, hook in 2 seconds, CTA = WhatsApp 0550 20 54 64, handle @kabli_ms, K+M mark bottom-left.
- Canva (identity C, saved 2026-10-07 with his approval): design "KABLI_MS — Identité visuelle C (violet + bleu néon)", id DAHXUgyfHps, edit link https://www.canva.com/d/nlggEdCHk0E4ydO — 8 pages: 1 profile logo (2000x2000), 2 editable TIP post (1080x1350), 3 editable reel cover (1080x1920), 4-7 highlight covers (1080x1080), 8 brand board (1920x1080). Updated 2026-10-07 (his OK): pages 4-9 = 6 neon glass highlight covers (tips, sponsor, matjer, nata2ij, ANA, CONTACT), page 10 brand board, pages 11-12 = two blank pages he added himself (leave them). Texts are real Canva text boxes (default Canva font: he can switch them to Sora / Readex Pro in Canva); backgrounds = assets/brand/identity/canva_bg_{post,cover}.png (make_identity.py `canva_backgrounds`).
- Canva uploads (media ids): neon glass highlights tips MAHXUvwMGyM, ads MAHXUorUZrw, store MAHXUiAp7lg, results MAHXUnH0rCA, me MAHXUgBYVVY, contact MAHXUmzaYB0; logo_mark MAHXUuo87dg, logo_mark_white MAHXUjwJgFU, logo_profile MAHXUpkIg4I, logo_horizontal MAHXUiIOL2g, bg_post MAHXUql8rbA, bg_cover MAHXUnVqVUA, highlights MAHXUvHrrqQ / MAHXUp1UnJU / MAHXUpUfIgk / MAHXUoEtuSA, brand board MAHXUmOIy1k.
- Canva AI generation (create-design / generate-design) failed 2026-10-07 with "credit quota exceeded" on his account: build designs by copy-design + edit-design (add_page with size, update_fill backgrounds, add_text + format_text) instead, and get his OK before committing.
- Old palette B Canva work: logo DAHXMVIM1B8 (kept), 4 tip-post candidates never saved.

## Caption font & motion update (reel2 F)
- Arabic captions are drawn as images (Pillow+raqm) because this ffmpeg/libass cannot shape Arabic with Google fonts; default font Lalezar (bold display), `--ar-font` to change (any .ttf in tools/fonts). Latin captions stay Anton via libass.
- Zoom is soft by default (`--zoom 0.45`; 1 = old strong punch, 0 = off) — Mustafa asked for less zoom-out.
- Generated B-roll cutaways (palette B, text in the upper half so captions stay readable): `[broll:trust]` handshake/CONFIANCE, `[broll:chat]` WhatsApp customer messages, `[broll:product]` box/PRODUIT, `[broll:face]` camera/B WJHEK, `[broll:growth_chart]`. Don't cover his face when he says "قدامك"/"أنا هاني".

## Hook, beat sync, safe zones (reel2 G)
- `--hook "ليش الناس ما *يشريوش* منك؟"`: big hook card in the top safe zone for 0-2.6 s, white flash at 0, low impact sound, strong first punch zoom.
- `--music beat --bpm 100`: royalty-free beat generated by tools/make_beat.py (kick/clap/hats/sub-bass), mixed low under the voice, faded at the end; zoom punches snap to the nearest beat (within 0.15 s). `--music path.mp3` for his own track (must be royalty-free).
- Safe zones for IG Reels: captions centred around 60% height and shifted left (right ~200 px kept clear of like/comment buttons), nothing important in the bottom ~18% (username/caption) or very top bar.
- Content focus answer: his reels = educational tips for e-commerce merchants + personal brand, with sponsoring as CTA.

## 3D B-roll (reel2 H)
- tools/broll3d.py = own tiny 3D renderer (perspective, flat shading, extruded text, floor grid): `[broll:product3d]` spinning cardboard box, `[broll:trust3d]` gold coin flipping with the handshake + CONFIANCE, `[broll:chat3d]` phone swinging in perspective with WhatsApp messages popping. Animations finish in ~0.7 s because cues are ~1 s.
- Generated on demand into assets/_generated (git-ignored). Real filmed b-roll from Mustafa still beats generated b-roll for trust.
- Colour: default grade is now `pro` (Mustafa found the face lighting/colours off): light denoise, highlights rolled off (sunroof light on his forehead), less red in skin, normal contrast. `cinema` made his skin too pink.
- Zoom: Mustafa wants ONE zoom-out at the very start only (`--zoom-mode intro`, now the default: 1.16x -> 1.0 over 0.8 s, then static). `--zoom-mode all` brings back a zoom on every caption.

## Pro-editing checklist (from Mustafa's brief) — all available as .srt tags
- Dynamic captions word-by-word or phrase-by-phrase (auto_subs.py 3rd arg), white + orange accent, black outline.
- Animated emoji (slide in, top), `[circle]` red ring drawn around his FACE (auto face detection, opencv<5) or `[circle:x,y]`, `[arrow:x,y]` bouncing red arrow, `[notif:TEXT]` WhatsApp notification banner sliding from the top (use real wording; don't fake orders/results).
- Camera: one intro zoom-out (default), `[shake]` impact shake (+boom), hook shake automatic; b-roll enters with a fast whip-in from the right.
- SFX: click on every caption, whoosh on b-roll, pop on emoji/overlays, ding on `[ding]`/`[flash]`/`[money]`, boom on `[shake]`/hook; generated beat under the voice.
- 3D: broll3d.py (box, coin, phone).
- Mustafa's preferences (latest): whoosh at most ONCE per reel; camera shake only once, light (at the hook); French words he says (confiance, produit, commande...) are written in French (Latin letters) inside Arabic captions — the caption renderer handles mixed Arabic/French word order.
- Captions: Mustafa wants ONLY the key words on screen (`--keywords-only`: only the *starred* words, big, drawn as images, Arabic and French alike). (Old test colour yellow FFD60A — replaced by the palette C neon captions.)

## "After Effects" card style (reference: reel recorded on a laptop, "4 hours of editing for 20 seconds")
- `--layout cards`: light grid-paper background with soft window-light shadows, the video in a big rounded card (800x1422) with drop shadow that slides up at the start, a small face card (auto face crop, white border, from the clean talking-head stream) sliding in from the left at 1 s, big "#" and a barcode as decorations. Captions/hook/emoji sit on top.
- Example: `python3 tools/edit_reel.py videos/reel2.mov --srt subs/reel2_L.srt --layout cards --keywords-only --accent FFD60A --hook "..." --music beat`

## reel3 (car, black t-shirt, 63 s) — "créative مليحة وما تبيعش؟"
- Source: `1006 (1)(2).mov` uploaded to main (the chat converts videos to GIF — always upload the .mov via GitHub). Saved as videos/reel3.mov.
- Story heard (Whisper large-v3, cleaned audio): a client had a good créative and messages were coming, but the problem was in selling; the fix = "اعرف وين تشري" (know where to buy / sourcing).
- Mustafa asked to keep his filter: `--grade none`. Keywords-only neon captions (palette C); star whole short phrases (e.g. `*البيع ما كاش*`) so small words like "ما" are never dropped.

- 2026-10-07: Mustafa asked to REMOVE the white grid background of the cards layout -> saved style now uses `--layout full` (video fills the screen; badge, captions, icons, b-roll, end card unchanged). reel3_v11 = this look.
- 2026-10-07: NO music; sound effects = ONLY the caption sound (soft "bubble pop" when a key word / icon appears), no whoosh / ding / boom -> preset uses `--text-sfx-only`, no `--music`. reel3_v12 = this sound.
- 2026-10-07 ("طور نفسك sound effects"): designed SFX `tools/sfx_pro.py` via `--sfx-style pro` (preset default, still NO music): soft bubble pop on key-word captions, 3-note bell sparkle on icons, ONE moving swoosh on the first b-roll, soft deep hit on the hook, C-E-G chime on the end card. reel3_v13 = this sound. (`--text-sfx-only` = pops only, if he wants it quieter.)
- 2026-10-07: faceless motion-graphics reels (when he has no footage): `python3 tools/motion_reel.py subs/<name>.json videos/<name>.mp4` (Remotion TipReel scenes: kicker/title/sub/icon, neon text, glass icons ic_* in remotion/public, sfx_pro sounds, end card). First one: videos/reel_motion1.mp4 (3 errors that burn the sponsor budget).
- 2026-10-07: sponsoring PRICE LIST in identity C: `python3 tools/price_list.py` -> assets/brand/identity/price_list.png (1920x1080). Prices/reach copied from HIS own price image (5/7/10/15 days, 1 mois premium + 2 levels each) — edit PLANS in the script when he changes them; never invent prices.
- 2026-10-07: WhatsApp badge (green logo + 0550 20 54 64 pill) bottom-left for the whole reel (`--wa-badge`), and NO end card (`--no-endcard`) — both in the preset. New b-roll `[broll:rm_dress]` (Remotion Dress3D: dress on hanger) for clothing products. reel4_v3 = this.

## Series « E-COM TIP » (his idea 2026-10-07)
- One small useful e-commerce tip per Reel, numbered (#01, #02…), fixed format + same cover each time. Plan, 20 episode ideas and script #01: profile/series_ecom_tip.md.

## Shopify store (2026-10-08)
- Women's clothing store, luxury, palette C + Sora/Readex. Name kept = **VIOLET Vogue** (his choice; the K+M / KABLI_MS logo stays for his personal account only). Kit: content/shopify/ (store_kit.md, logos, banners, favicon; `python3 tools/shopify_kit.py`). Connected Shopify shop is blocked for API access (billing/plan) until he fixes it; never invent prices/delivery fees/delays.

## "Reference reel" look (his choice 2026-10-09, reel4_v6)
- From a reel he liked (studio creator): big WHITE bold hook title, no plate (`--hook-style title`, "line1 / line2", *word* = neon blue); full-frame split with tilted 3D phone + his face shrinking into a PIP + neon-blue label pill; glass card with a counter (only real figures he says); search bar that types itself; WhatsApp / Instagram / Partage pills at the end. No music, pro SFX (+ typing clicks).
- How: edit_reel.py ... `--hook-style title --dump-timeline T.json` then `python3 tools/ref_style.py base.mp4 T.json plan.json out.mp4` (plan times = source timeline; Remotion comps in remotion/src/RefStyle.tsx). Analysis of the reference: content/scripts/ref_reel_1009_analysis.md.

- Covers: always pick a frame with his MOUTH CLOSED, teeth not visible, neutral look (his rule 2026-10-09).

- "Light" edits (his request 2026-10-13: «ما تكثرش من موشن ديزاين»): hook title + keyword captions + few icons + badges only, no phone split / cards / b-roll (= videos/reel5_v1.mp4).
