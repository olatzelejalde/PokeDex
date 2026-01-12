# PokeDex

Web aplikazio bat Pokémonen **Pokédex** moduan: Pokémonak ikusi/iragazi, **taldeak** sortu eta kudeatu, **lagunak** gehitu, eta **Telegram** bidez taldeak partekatu. Gainera, ekintzen arabera **intsigniak** (badges) lortzen dira.

## Ezaugarriak

- Pokémonen zerrenda + bilaketa + motaren araberako filtroa
- "Nire taldeak": taldeak sortu/ezabatu eta Pokémonak gehitu
- "Nire lagunak": erabiltzaileak bilatu eta lagun bihurtu
- "Nire intsigniak": lortutako intsigniak (berdea) eta blokeatuak (grisa)
- Telegram integrazioa: talde bat lagun bati bidali (irudia ahal bada; bestela testua)

## Teknologia

- Backend: **Python + Flask**
- DB: **SQLite** (fitxategia: `library.sqlite`)
- Frontend: HTML + CSS + JavaScript (vanilla)
- Telegram: Bot API (`requests`) + (aukerakoa) `Pillow` irudiak sortzeko

## Baldintzak

- Python 3.10+ (gomendatua: 3.11)

## Instalazioa

### 1) (Gomendatua) Virtualenv

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

### 2) Paketeak instalatu

Proiektu honek gutxienez hauek behar ditu:

```bash
pip install flask flask-cors requests
```

Telegram-en irudia bidali nahi baduzu (aukerakoa baina polita):

```bash
pip install pillow
```

## Martxan jartzea

```bash
python run.py
```

Nabigatzailean:

- http://localhost:5000

Lehenengo exekuzioan, DBa automatikoki sortzen da `library.sqlite`-en eta `app/database/schema.sql` aplikatzen da.

## Saioa / erabiltzaileak

`schema.sql`-ek demo erabiltzaile batzuk sartzen ditu. Adibidez:

- erabiltzailea: `admin` / pasahitza: `adminpass`

(
Oharrak: datuak aldatu/handitu daitezke proiektua eboluzionatzen doan heinean.
)

## Telegram konfigurazioa (aukerakoa)

Telegram bidez partekatzeko:

1. Sortu bot bat `@BotFather`-en eta hartu token-a
2. Ezarri ingurune aldagaia:

```powershell
$env:TELEGRAM_BOT_TOKEN="<zure_token_a>"
```

3. (Local) polling bidez aktibatzeko:

```powershell
$env:TELEGRAM_USE_POLLING="1"
```

Oharra: webhooka eta polling-a ezin dira batera erabili. Localerako polling-a da errazena.

## Intsigniak (Badges)

- Intsigniak `intsignia` taulan definituta daude.
- Erabiltzailearen aurrerapena/egoera `erabiltzaileak_intsigniak` taulan gordetzen da.
- UI-an: lortutakoak **berde** agertzen dira (`app/static/sprites/berdea.png`), bestela **grisa**.

## Ohiko arazoak (Troubleshooting)

### 1) 500 errorea `/api/.../intsigniak` edo antzekoetan

Normalean `library.sqlite` zaharrarekin gertatzen da (schema berria ez dago aplikatua).

Irtenbide azkarra (garapen/klase proiektua bada):

1. Itxi aplikazioa
2. Ezabatu `library.sqlite`
3. Berriro exekutatu `python run.py`

### 2) `ModuleNotFoundError` (flask / flask_cors / requests)

Instalatu dependentziak virtualenv-ean:

```bash
pip install flask flask-cors requests
```

## Proiektuaren egitura (labur)

```
app/
	__init__.py              # Flask app + DB init
	controller/
		ui/bistaKontroladorea.py     # API routes
		model/                       # controller logic
	domain/                        # katalogoak / domain models
	database/
		schema.sql                   # SQLite schema + seed
	static/
		js/                          # frontend logic
		styles/                      # CSS
		sprites/                     # images
	templates/                     # HTML templates
run.py                           # entrypoint
config.py                        # DB path, secret key
```
