# سجل التغييرات — كل واش درنا (Mustafa / @kabli_ms)

كل حاجة هنا محفوظة في GitHub، الفرع `claude/instagram-profile-intro-3xh6k4`.

## 🎨 الهوية البصرية (2026-10-07)
- ألوان جداد (Palette C): بنفسجي غامق #140B34 · بنفسجي #2A1B5E · بنفسجي فاتح #8B5CF6 · أزرق نيون #38BDF8.
- خطوط: Readex Pro (عربي) + Sora (لاتيني)، كتيبة يد: Aref Ruqaa / Great Vibes.
- لوغو جديد K+M (`assets/brand/logo_*`) — القديم (كحل + برتقالي) محفوظ في `assets/brand/archive_palette_b/`.
- أيقونات نيون زجاج (كيما الصور اللي بعثت)، كوفرات الهايلايت، لوحة الهوية، قوالب البوستات.
- كانفا: تصميم "KABLI_MS — Identité visuelle C".
- قائمة الأسعار بالهوية تاعك + لوغو إنستغرام وفيسبوك بألوانهم + Meta Ads (`assets/brand/identity/price_list.png`).

## 🎬 الستايل تاع المونتاج (المحفوظ)
- الفيديو يعمّر الشاشة كاملة (بلا الخلفية البيضاء).
- بلا موسيقى، غير مؤثرات صوتية مدروسة (pop، sparkle، swoosh واحد، hit في الهوك، chime).
- رقم الواتساب تحت على اليسار، بلا end card في الآخر.
- قاعدة: ما كاش كتيبة فوق كتيبة — الكتيبة تبدا من بعد الهوك وتبقى بين اللوغو ورقم الواتساب، والأيقونة جنب الكلمة ماشي فوقها.
- الأمر: `tools/reel_mustafa.sh videos/reelN.mov subs/reelN.srt "الهوك"`

## ✨ ستايل "الريل اللي عجبك" (2026-10-09)
- عنوان أبيض كبير في الفوق، تليفون 3D + وجهك صغير في الركنة، كارت زجاج بعدّاد، شريط بحث يتكتب وحدو، أزرار WhatsApp · Instagram · Partage في الآخر.
- الأدوات: `--hook-style title` + `tools/ref_style.py` — المثال: `videos/reel4_v6.mp4`.
- التحليل تاع الريل: `content/scripts/ref_reel_1009_analysis.md`.

## 📹 الفيديوهات
- reel3: v10 → v13 (هوية جديدة، شاشة كاملة، بلا موسيقى، مؤثرات pro).
- reel4 (الـ ateliers): v1 → v6 — "80 commande"، فستان بلاصة الكرطونة، رقم الواتساب، بلا end card، الهوك "Les ateliers سرّاقين الموديلات"، v6 بستايل الريل اللي عجبك.
- reel_motion1: فيديو موشن بلا وجه.
- **E-COM TIP #01** (2026-10-09): "فيديو شباب وما جابليش" — كتيبة كثر (11 كلمة + أيقونة لكل وحدة)، "E-COM TIP • الحلقة 01" فوق على اليمين طول الفيديو، تليفون فيه سكرول (3 ثواني)، شريط بحث، وفي الآخر "Abonne-toi · TIP #02 قريب · WhatsApp" — `videos/tip01_v1.mp4`.
- غلاف الحلقة 01 (2026-10-09): `content/covers/tip01_cover.jpg` — E-COM TIP #01 + "الحلقة 01" + وجهك في كارت بإطار نيون + "فيديو شباب وما جابليش؟". الأداة: `python3 tools/make_cover.py frame.png out.jpg "E-COM TIP" "#02" "الحلقة 02" "سطر 1" "سطر 2"`.
- **reel5** (2026-10-13, السبّاط / "ما تجيكش ساهلة"): بالهوية بصح **موشن قليل** كيما طلبت — الهوك أبيض "ما تجيكش / ساهلة!"، 15 كلمة مهمة وأيقونات قلال، رقم الواتساب، بلا تليفون ولا كروت — `videos/reel5_v1.mp4`. غلاف: `content/covers/reel5_cover.jpg` ("ما تجيكش ساهلة!"، فمك مسكّر).

## 📚 المحتوى
- سلسلة E-COM TIP: 20 موضوع + سكريبتات #01–#10 (`profile/series_ecom_tip.md`) + جدول النشر Excel (`content/E-COM_TIP_planning.xlsx`, #01 = فيديو شباب) + عناوين الحلقات 01–20 (`content/E-COM_TIP_titles.md`).
- سكريبت "ماشي كل فيديو شباب يبيع" + جدول المونتاج + إرشادات الصوت والألوان + برومبتات الذكاء الاصطناعي (`content/scripts/creative_chaba_storyboard.md`).
- مخطط إعلان فستان 30 ثانية (`content/scripts/violet_vogue_dress_ad.md`).
- Ad copy لفيديو الـ ateliers (في الشات).

## 🛍️ ستور Shopify — VIOLET Vogue
- لوغو، بانيرات PC + تليفون، favicon، والنصوص كاملة بالفرنسية (`content/shopify/`).
- صفحة تجريبية: https://claude.ai/artifact/9nE4wmDheBcBEYqRpNNEF5
- باقي: تصلّح حساب Shopify (مشكل الخلاص) وتبعث صور وأسعار المنتوجات.

## 🧰 أدوات أخرى
- Prompteur (تقرا النص وإنت تصوّر): https://claude.ai/artifact/4Amrbquwp2dPzrw3vt7cLt

## 🚫 قواعد ما نبدلوهمش
- ما نذكروش نتائج الحملات، وما نخترعوش لا أسعار لا نتائج لا أرقام.
- الردود بالدارجة، قصيرة وبسيطة.
