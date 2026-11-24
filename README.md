# Color Splash – Pictures

Is repo me daali gayi pictures **Color Splash** app me apne aap aa jaati hain.
App update karne ki zarurat nahi hai.

## Nayi picture kaise daale

1. `pictures` folder kholo, phir category ka folder kholo (jaise `animals`).
2. Upar right me **Add file → Upload files** dabao.
3. PNG picture drag karke daalo.
4. Neeche **Commit changes** dabao.

Bas itna hi. 1–2 minute me GitHub picture ko khud chhota (WebP) kar deta hai.
Jab bachcha agli baar internet ke saath app kholega, picture app me aa jaayegi.

### Picture ka naam
File ka naam hi app me picture ka naam banta hai:
`happy_lion.png` app me **Happy Lion** dikhega.

- Sirf English letters aur numbers use karo.
- Jo picture pehle aani chahiye, uske naam ke aage number lagao: `01_happy_lion.png`
  (number app me nahi dikhta).

### Picture kaisi ho
- Har rang ek flat colour ho, aur saari shapes ke chaaron taraf **kaali (black) outline** ho.
- Background safed (white) ya transparent ho.
- Square picture sabse achhi lagti hai.
- **Upload se pehle picture dhyan se dekh lo.** Yeh seedha bachchon ke phone me jaati hai.

## Nayi category
`pictures` folder me jaake ek poora naya folder (jaise `dinosaurs`) apni pictures ke saath drag karke upload kar do.
Ya **Add file → Create new file** me naam likho `dinosaurs/.gitkeep`, phir us folder me pictures upload karo.

## Picture badalna
Same naam ki nayi PNG upload kar do. Purani picture apne aap badal jaayegi.

## Picture hatana
`pictures/<category>/` me us picture ki `.webp` file kholo, upar **⋯ → Delete file** dabao, phir **Commit changes**.
Woh picture app se bhi hat jaayegi.

## Kaise pata kare ki sab theek hua
Repo me upar **Actions** tab kholo.
- ✅ Green tick: picture taiyaar hai.
- ❌ Red cross: koi file chhod di gayi (jaise galat format). Us run ko kholkar wajah padho.

---

Technical: `tools/build_catalog.py` uploaded PNG/JPG ko 1024 px WebP banata hai,
asli file ko `originals/` me rakhta hai (app use download nahi karta), aur `catalog.json` likhta hai.
App `catalog.json` ko `raw.githubusercontent.com/xeeronline-ai/colorsplash-pictures/main/` se padhta hai.
Folder aur file ke naam badalne se picture ka id badal jaata hai, aur bachche ki us picture par ki hui painting gallery se chali jaati hai.
