# ⛽ Degaliniu Kainu Palyginimo Sistema

Degaliniu kainu palyginimo aplikacija su **lokacijos filtravimu** ir **interaktyviu žemėlapiu**.

## 🎯 Funkcionalumas

- ✅ **Lokacijos pagrindinis paieška** - Raskite degalines šalia jūsų
- ✅ **GPS koordinates** - Automatinis skaičiavimas atstumo (Haversine formulė)
- ✅ **Interaktyvus žemėlapis** - Vizualinė degalinių lokacija (Leaflet.js)
- ✅ **Kuro tipai** - Benzinas 95/98, Dyzelis, LPG
- ✅ **Pasirinktinas spindulys** - Paieška 5-200 km spindulyje
- ✅ **REST API** - Lengvas integravimas
- ✅ **Kelių miestų palaikymas** - Vilnius, Kaunas, Klaipėda, Šiauliai, Panevėžys

## 🚀 Pradžia

### Reikalavimai
- Python 3.9+
- pip

### Diegimas

```bash
# Klonuoti repozitoriją
git clone https://github.com/juozasaugutis-glitch/Fuel-api.git
cd Fuel-api

# Sukurti virtualią aplinką
python -m venv venv
source venv/bin/activate  # Linux/Mac
# arba
venv\Scripts\activate  # Windows

# Įdiegti priklausomybes
pip install -r requirements.txt
```

### Paleidimas

```bash
python server.py
```

Tada atidarykite naršyklę: **http://localhost:8000**

## 📱 Naudojimas

### Interaktyvus puslapis (UI)

1. Pasirinkite miestą iš dropdown arba įveskite savo koordinates
2. Pasirinkite kuro tipą (Benzinas 95, Dyzelis, etc.)
3. Nustatykite paieškos spindulio dydį (km)
4. Spustelėkite "🔍 Ieškoti" arba "📍 Mano lokacija"
5. Rezultatai rodo:
   - **Žemėlapis** su degalinių lokacija
   - **Geriausia pasiūlyma** (pigiausias degalai)
   - **Visas degalines** arčiau jūsų

### REST API

#### Gauti degalines pagal lokacija

```bash
curl "http://localhost:8000/api/prices?latitude=54.6872&longitude=25.2797&fuel_type=D&radius_km=30"
```

**Atsakymas:**
```json
{
  "user_location": {
    "latitude": 54.6872,
    "longitude": 25.2797,
    "name": "Vilnius"
  },
  "fuel_type": "D",
  "radius_km": 30,
  "stations_found": 5,
  "stations": [
    {
      "degaline": "Statoil",
      "vieta": "Vilnius",
      "kaina": 1.32,
      "atstumas_km": 2.5,
      "latitude": 54.68,
      "longitude": 25.27,
      "address": "Geležinio Vilko g. 10"
    }
  ]
}
```

#### Rasti pigiausią degalinę

```bash
curl "http://localhost:8000/api/best-price?latitude=54.6872&longitude=25.2797&fuel_type=D&radius_km=50"
```

**Atsakymas:**
```json
{
  "degaline": "Shell",
  "vieta": "Vilnius",
  "address": "Konstitucijos pr. 7",
  "kaina": 1.29,
  "atstumas_km": 3.2,
  "kuras": "Dyzelis",
  "sutaupymas": {
    "santaupa_eurais": 0.08,
    "santaupa_procentais": 5.8
  }
}
```

#### Gauti visų tipų kurus

```bash
curl "http://localhost:8000/api/all-fuels?latitude=54.6872&longitude=25.2797&radius_km=30"
```

#### Gauti pavyzdines lokacijas

```bash
curl "http://localhost:8000/api/locations"
```

## 🗂️ Failų Struktūra

```
Fuel-api/
├── app.py                 # Pagrindinė logika (FuelPriceComparator klasė)
├── server.py              # FastAPI serveris ir HTML puslapis
├── requirements.txt       # Python priklausomybes
├── README.md             # Šis failas
└── .gitignore
```

## 📊 Algoritmai

### Atstumo Skaičiavimas (Haversine)

Naudojame Haversine formulę GPS koordinatėms apskaičiuoti:

```python
distance = 2 * R * arcsin(sqrt(sin²((Δlat)/2) + cos(lat1) * cos(lat2) * sin²((Δlon)/2)))
```

Kur:
- `R = 6371 km` (Žemės spindulys)
- `Δlat`, `Δlon` - koordinačių skirtumai

### Santupos Skaičiavimas

```python
santaupa = ((brangiausias - pigiausias) / brangiausias) * 100%
```

## 🗺️ Žemėlapis

- **Biblioteka**: Leaflet.js
- **Žemėlapis**: OpenStreetMap
- **Žymės**: 
  - 🔵 Jūsų lokacija (mėlyna)
  - 🔴 Degalines (raudona)

## 🔄 Integracija su Fuel.api

Sukonfigūruokite `fuel.api` URL `app.py` faile:

```python
self.api_base_url = "https://api.fuel.api"
```

API turi grąžinti tokią struktūrą:
```json
{
  "station_name": "Shell Vilnius",
  "latitude": 54.6872,
  "longitude": 25.2797,
  "price_95": 1.45,
  "price_98": 1.55,
  "price_D": 1.32,
  "price_LPG": 0.65,
  "location": "Vilnius",
  "city": "Vilnius",
  "address": "Konstitucijos pr. 7"
}
```

## 💡 Galimos Išplėtimos

- [ ] Duomenų bazė (PostgreSQL) - saugoti degalinių istoriją
- [ ] Kainų trendo grafikas - pamatyti kainu pokytius
- [ ] Savaitės ataskaita per e-pašta
- [ ] Mobilinė aplikacija (React Native)
- [ ] Skambučiai degalinėms
- [ ] Kuponu integravimas
- [ ] Lankstuminko režimas - kelias tarp degalinių

## 📝 Licenzija

MIT License

## 👨‍💻 Kontaktai

GitHub: [@juozasaugutis-glitch](https://github.com/juozasaugutis-glitch)

## 🤝 Prisidėti

Pageidaujiame pagalbos! Sukūrykite Pull Request arba Report Issue.

---

**Sėkmės ieškant pigiausių degalų! ⛽💰**
