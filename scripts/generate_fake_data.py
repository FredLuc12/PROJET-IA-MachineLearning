"""
generate_fake_data.py
---------------------
Génère des données de mesures simulées réalistes pour l'entraînement ML.
Simule des cycles jour/nuit, des événements d'irrigation, et des variations météo.

Usage :
    python scripts/generate_fake_data.py --days 30 --interval 300 --output data/raw/fake_mesures.json
"""

import argparse
import json
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

SEED = 42
random.seed(SEED)

# Seuils sol (en %)
SOIL_DRY_THRESHOLD    = 30.0   # En dessous → état sec → irrigation recommandée
SOIL_NORMAL_THRESHOLD = 60.0   # Entre 30-60 → normal / Au-dessus → humide

# Paramètres température
BASE_TEMP_DAY   = 28.0
BASE_TEMP_NIGHT = 16.0
BASE_AIR_HUM    = 55.0

# Irrigation
IRRIGATION_TRIGGER    = 25.0   # déclenche l'irrigation à 25% (avant le seuil sec)
IRRIGATION_BOOST      = 40.0   # +40% humidité sol
IRRIGATION_COOLDOWN   = 12     # mesures de cooldown après irrigation

# Évapotranspiration — plus agressive pour créer des états "sec"
EVAPOTRANSPIRATION_BASE        = 0.8   # % perdu par mesure (était 0.3)
EVAPOTRANSPIRATION_HEAT_FACTOR = 0.05  # facteur chaleur (était 0.02)


def simulate_temperature(hour: float) -> float:
    angle = 2 * math.pi * (hour - 4) / 24
    amplitude = (BASE_TEMP_DAY - BASE_TEMP_NIGHT) / 2
    base = (BASE_TEMP_DAY + BASE_TEMP_NIGHT) / 2
    return round(base + amplitude * math.sin(angle) + random.gauss(0, 0.5), 1)


def simulate_air_humidity(temp: float) -> float:
    deviation = (temp - BASE_TEMP_DAY) * -1.5
    value = BASE_AIR_HUM + deviation + random.gauss(0, 2)
    return round(max(20.0, min(95.0, value)), 1)


def compute_evapotranspiration(temp: float) -> float:
    extra = max(0, temp - 25) * EVAPOTRANSPIRATION_HEAT_FACTOR
    return EVAPOTRANSPIRATION_BASE + extra


def label_soil_state(h: float) -> str:
    if h < SOIL_DRY_THRESHOLD:
        return "sec"
    elif h < SOIL_NORMAL_THRESHOLD:
        return "normal"
    return "humide"


def should_irrigate(h: float) -> bool:
    return h < SOIL_DRY_THRESHOLD


def generate_dataset(days: int, interval_seconds: int) -> list[dict]:
    records = []
    start = datetime.now() - timedelta(days=days)
    current_time = start

    # Démarre dans un état variable pour avoir de la diversité dès le début
    soil_humidity = random.uniform(15.0, 75.0)
    irrigation_cooldown = 0
    mesure_id = 1
    capteur_id = 1

    total_steps = int(days * 86400 / interval_seconds)

    for step in range(total_steps):
        hour = current_time.hour + current_time.minute / 60
        temperature  = simulate_temperature(hour)
        humidite_air = simulate_air_humidity(temperature)

        # Évapotranspiration
        evap = compute_evapotranspiration(temperature)
        soil_humidity = max(0.0, soil_humidity - evap + random.gauss(0, 0.2))

        # Irrigation auto (déclenche avant le seuil sec pour avoir du sec + normal)
        irrigated_now = False
        if soil_humidity < IRRIGATION_TRIGGER and irrigation_cooldown <= 0:
            boost = IRRIGATION_BOOST + random.gauss(0, 5)
            soil_humidity = min(100.0, soil_humidity + boost)
            irrigation_cooldown = IRRIGATION_COOLDOWN
            irrigated_now = True
        else:
            irrigation_cooldown = max(0, irrigation_cooldown - 1)

        humidite_sol = round(max(0.0, min(100.0, soil_humidity)), 1)

        etat_sol   = label_soil_state(humidite_sol)
        besoin_eau = should_irrigate(humidite_sol)

        humidite_prevue = round(
            max(0.0, humidite_sol - evap * (1800 / interval_seconds)), 1
        )

        records.append({
            "id_mesure":       mesure_id,
            "id_capteur":      capteur_id,
            "timestamp":       current_time.isoformat(),
            "humidite_sol":    humidite_sol,
            "temperature":     temperature,
            "humidite_air":    humidite_air,
            "hour":            round(hour, 2),
            "etat_sol":        etat_sol,
            "besoin_eau":      besoin_eau,
            "humidite_prevue": humidite_prevue,
            "irrigated":       irrigated_now,
        })

        current_time += timedelta(seconds=interval_seconds)
        mesure_id += 1

    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days",     type=int, default=30)
    parser.add_argument("--interval", type=int, default=300)
    parser.add_argument("--output",   type=str, default="data/raw/fake_mesures.json")
    args = parser.parse_args()

    print(f"⚙️  Génération de {args.days} jours de données (intervalle {args.interval}s)...")
    records = generate_dataset(days=args.days, interval_seconds=args.interval)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    total  = len(records)
    dry    = sum(1 for r in records if r["etat_sol"] == "sec")
    normal = sum(1 for r in records if r["etat_sol"] == "normal")
    humid  = sum(1 for r in records if r["etat_sol"] == "humide")
    irrig  = sum(1 for r in records if r["irrigated"])

    print(f"✅ {total} mesures générées → {output_path}")
    print(f"   🟤 Sec    : {dry}    ({dry/total*100:.1f}%)")
    print(f"   🟢 Normal : {normal} ({normal/total*100:.1f}%)")
    print(f"   🔵 Humide : {humid}  ({humid/total*100:.1f}%)")
    print(f"   💧 Irrigations déclenchées : {irrig}")


if __name__ == "__main__":
    main()