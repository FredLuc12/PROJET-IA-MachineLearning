-- ============================================================
--  HydroSmart — Script de création de la base de données
--  À exécuter dans pgAdmin4 : clic droit sur ta DB → Query Tool
-- ============================================================

-- 1. Parcelle
CREATE TABLE IF NOT EXISTS parcelle (
    id_parcelle  SERIAL PRIMARY KEY,
    nom          VARCHAR(100) NOT NULL,
    superficie   FLOAT,
    type_culture VARCHAR(50),
    localisation VARCHAR(150)
);

-- 2. Capteur
CREATE TABLE IF NOT EXISTS capteur (
    id_capteur      SERIAL PRIMARY KEY,
    id_parcelle     INT REFERENCES parcelle(id_parcelle),
    type_capteur    VARCHAR(50) NOT NULL,  -- 'humidite_sol', 'temperature', 'humidite_air'
    date_install    TIMESTAMP DEFAULT NOW(),
    statut          VARCHAR(20) DEFAULT 'actif',
    profondeur      FLOAT
);

-- 3. Mesure
CREATE TABLE IF NOT EXISTS mesure (
    id_mesure      SERIAL PRIMARY KEY,
    id_capteur     INT REFERENCES capteur(id_capteur),
    timestamp      TIMESTAMP DEFAULT NOW(),
    humidite_sol   FLOAT,
    temperature    FLOAT,
    humidite_air   FLOAT
);

-- 4. Irrigation
CREATE TABLE IF NOT EXISTS irrigation (
    id_irrigation  SERIAL PRIMARY KEY,
    id_parcelle    INT REFERENCES parcelle(id_parcelle),
    date_debut     TIMESTAMP DEFAULT NOW(),
    date_fin       TIMESTAMP,
    volume_eau     FLOAT,
    mode           VARCHAR(20) DEFAULT 'automatique'
);

-- 5. Recommandation ML
CREATE TABLE IF NOT EXISTS recommandation_ml (
    id_recommandation  SERIAL PRIMARY KEY,
    id_mesure          INT REFERENCES mesure(id_mesure),
    id_irrigation      INT REFERENCES irrigation(id_irrigation),
    timestamp          TIMESTAMP DEFAULT NOW(),
    besoin_eau         BOOLEAN,
    niveau_humidite_prevu FLOAT,
    modele_utilise     VARCHAR(100)
);

-- ── Données de départ ─────────────────────────────────────────
INSERT INTO parcelle (nom, superficie, type_culture, localisation)
VALUES ('Parcelle A', 500.0, 'maïs', 'Zone Nord');

INSERT INTO capteur (id_parcelle, type_capteur, profondeur)
VALUES (1, 'humidite_sol+temperature+humidite_air', 10.0);

-- Vérification
SELECT 'parcelle'        AS table_name, COUNT(*) FROM parcelle
UNION ALL
SELECT 'capteur',          COUNT(*) FROM capteur
UNION ALL
SELECT 'mesure',           COUNT(*) FROM mesure
UNION ALL
SELECT 'irrigation',       COUNT(*) FROM irrigation
UNION ALL
SELECT 'recommandation_ml',COUNT(*) FROM recommandation_ml;