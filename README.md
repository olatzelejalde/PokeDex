# PokeDex

Web aplikazio bat Pokémonen **Pokédex** moduan: Pokémonak ikusi, **taldeak** sortu eta kudeatu, **lagunak** gehitu, **changeLog** ikusi eta **Telegram** bidez taldeak partekatu. Gainera, ekintzen arabera **intsigniak** (badges) lortzen dira.

## Ezaugarriak

- Pokémonen zerrenda + bilaketa + motaren araberako filtroa
- "Nire taldeak": taldeak sortu/ezabatu eta Pokémonak gehitu
- "Nire lagunak": erabiltzaileak bilatu eta lagun bihurtu
- "Nire intsigniak": lortutako intsigniak (berdea) eta blokeatuak (grisa)
- "Nire profila": Erabiltzailea bere datuak editatzeko aukera izango du eta saioa bertatik ixteko.
- "Changelog": Erabiltzaileek sortutako taldeen eta bertan sartutako pokemonen erregistroa eukiko du.
- Telegram integrazioa: talde bat lagun bati bidali (irudia ahal bada; bestela testua)

## Teknologia

- Backend: **Python + Flask**
- DB: **SQLite** 
- Frontend: HTML + CSS + JavaScript
- Telegram: Bot API  + (aukerakoa) `Pillow` irudiak sortzeko

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

Lehenengo exekuzioan, DBa automatikoki sortzen da `library.sqlite`-en eta `app/database/schema.sql` aplikatzen da. Pixkat itxaron beharko da.

## Saioa / erabiltzaileak

Saio bat irekitzeko:
1. Erregistratu botoia sakatu
2. datuak sartu (telegram aukerakoa)
3. erregistratu sakatu

Ondoren kontua gordeta egongo da eta saioa hasteko prest izango duzu.

## Telegram konfigurazioa

Nola bidali/jaso taldeak:
1. "Nire profila" atalean sartu
2. datuak editatu eta bertan zure telegram kontua sartu (aurretik telegramen definituta)
3. Telegram zabaldu eta PokemonParteBot botari /start komandoa bidali

Pausuak jarraitu ondoren zure lagunek taldeak bidali ahalko dizkizute.

## Intsigniak 

Intsigna bat lortzeko, intsignaren deskripzioa ikusi dezakezu, eta bete ostean intsigna emango zaizu.

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
