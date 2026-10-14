# Instructions for Claude (Mustafa's reels workspace)

SAVED STYLE (Mustafa's choice, = videos/reel3_v2_motion.mp4): every new reel uses
`tools/reel_mustafa.sh videos/reelN.mov subs/reelN.srt "hook with *key* word"` — FULL-SCREEN layout (no white card background, his request 2026-10-07), his own colours,
key words only as neon captions, hook, one intro zoom, one light shake, NO music, designed SFX `--sfx-style pro` (caption pop, icon sparkle, one swoosh, hook hit, end chime), Remotion/3D b-roll, circle,
neon icons from .srt tags, top-left K+M coin badge, WhatsApp number bottom-left (`--wa-badge`), NO end card, plus a _send.mp4 copy for the chat.
Only change it when he asks. Template .srt: subs/reel3_v7.srt.

VISUAL IDENTITY (his choice 2026-10-07) = PALETTE C "violet + neon blue": night violet #140B34, deep violet #2A1B5E,
violet #8B5CF6, neon blue #38BDF8 (gradient violet -> blue); fonts Readex Pro (Arabic) + Sora (Latin), script word
Aref Ruqaa / Great Vibes; new K+M logo (`tools/make_logo.py`, assets/brand/logo_*). Palette B (navy + orange) is retired
(archived in assets/brand/archive_palette_b/). After any brand change bump `PALETTE_ID` in tools/edit_reel.py so the
generated clips in assets/_generated are rebuilt.

CHANGELOG for Mustafa (Darija): profile/changelog.md — update it whenever something new is made or a preference changes.
REFERENCE-REEL LOOK (his choice 2026-10-09, = videos/reel4_v6.mp4): white title hook (`--hook-style title`), phone split + PIP, glass counter card,
typewriter search bar, CTA pills — `edit_reel.py ... --hook-style title --dump-timeline T.json` then `tools/ref_style.py base.mp4 T.json plan.json out.mp4`.
Content plans: profile/series_ecom_tip.md (E-COM TIP series), content/scripts/, Shopify kit content/shopify/ (store name VIOLET Vogue).

Start of every session:
1. Read `profile/mustafa.md` (who he is, tone, brand colors, contacts, audience, offer).
2. Reply in Algerian Darija (Arabic script), short and practical. Mustafa is a beginner in video editing: explain what you did in simple words.

Editing a reel (Mustafa uploads to `videos/`, sometimes on `main` — check `git fetch origin main` and pull the file from there):
1. `ffprobe` the file and look at a contact sheet of frames before deciding anything.
2. Ask for / write the subtitle script as an `.srt` (mixed Darija + French, emoji allowed: the tool overlays them as PNGs (needs `pip install pillow`)).
3. Run: `python3 tools/edit_reel.py videos/reelN.mov --srt subs.srt`
   - cuts silences, 1080x1920, light grade, loudness -14 LUFS, big subtitles, animated brand end card (Remotion EndCard) with WhatsApp + @kabli_ms.
   - Flags: `--no-silence-cut`, `--no-endcard`, `--srt-after-cut`, `--out`.
4. Check frames of the output (subtitle position/readability, end card) before delivering.
5. Commit to the current branch with the output at `videos/reelN_vX.mp4`; tell him the branch + path and how to download it (GitHub app/website, raw file).

Best pipeline (real timing): 1) `python3 tools/transcribe.py videos/reelN.mov` (Whisper large-v3, ~1 min) writes subs/reelN.draft.txt (Arabic-script DRAFT, partly wrong) + subs/reelN.words.json (reliable word timings). 2) Send him the draft; he corrects/rewrites it as script lines (one phrase per line, Latin Darija ok, *stars* on key words). 3) `python3 tools/auto_subs.py videos/reelN.mov script.txt 2 > subs/reelN.srt` — uses the real word timings when words.json exists (3rd arg = max words per caption). 4) edit_reel.py (`--grade pro` default = skin-friendly; also warm|natural|cinema|bright).

Auto captions (without words.json): Mustafa types (or dictates) what he says in a text file, then `python3 tools/auto_subs.py videos/reelN.mov script.txt > subs/reelN.srt` spreads the words over the speech (approx timing, check it), then run edit_reel.py with that .srt. Mark key words with *stars*.

Limits to remember: whisper (tools/transcribe.py) cannot transcribe Algerian Darija reliably, so words come from his script (style: see "Caption & color style" in profile); source quality is not improved by upscaling; no CapCut access.

Effects: see "Effects toolkit" in profile/mustafa.md. Add tags like `[sparks]`, `[flash]`, `[leak]`, `[money]`, `[broll:name]`, `[icon:name]` to cues in the .srt; emoji and *accent words* work too. Assets are auto-generated into assets/_generated (git-ignored) by tools/gen_assets.py; Mustafa's uploads in assets/{sparks,broll,icons} take priority.
