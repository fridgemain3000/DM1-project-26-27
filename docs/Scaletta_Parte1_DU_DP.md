# Scaletta Parte 1 — Data Understanding & Preparation (30 pt)

Progetto DM1 2026/27 · Dataset `seller_info_dm1_2627.csv` (13.843 venditori × 33 colonne) · target `seller_rating_class`

---

## 0. Cosa chiede il prof e come viene valutato

Dalle guideline ufficiali (slide 5 e 7):

| Blocco richiesto (slide 7)                                                                                   | Sezione di questa scaletta |
| ------------------------------------------------------------------------------------------------------------ | -------------------------- |
| **Data Semantics** — variabili, significato, caratteristiche                                                 | §2                         |
| **Distribution of the variables and statistics** — singole e coppie                                          | §3                         |
| **Data quality & variable transformation** — errori, outlier, mancanti, incoerenze semantiche, log-transform | §4, §5, §6                 |
| **Pairwise correlations & elimination of variables** — matrice di correlazione                               | §7                         |

Regole del report che pesano sul voto (slide 5):
- **Ogni scelta va giustificata** (perché elimino, perché imputo così, perché log).
- **Ogni grafico/tabella va commentato** (altrimenti "useless").
- **Discutere i limiti**, anche quando il risultato non convince.
- Grafici **leggibili** (titoli, assi con unità, font grandi, palette coerente).
- Solo PDF, max **20 pagine totali** per tutti e 4 i moduli (copertina e indice esclusi). Per la parte 1 conviene stare su **circa 4–5 pagine**, a due colonne se serve.
- Scadenza mid-draft **15/11/2026** (DU&DP + Clustering) → +0.5 punti.

Bonus trasversali (slide 11) a cui la parte 1 può contribuire: *Innovation* (es. riparazione dei numeri corrotti, imputazione con regressione, Cramér's V), *Experimentation* (confronto di più strategie di imputazione/trasformazione), *Appearance/Organization* (figure pulite, tabelle riassuntive).

> **Principio guida:** il prof valuta il **metodo**, non i numeri. Ogni passo segue lo schema *osservo → interpreto → decido → giustifico*.

---

## 1. Setup del notebook e caricamento

**Codice**
- Struttura consigliata: `notebooks/01_data_understanding_preparation.ipynb`, funzioni riusabili in `src/` (es. `src/cleaning.py`), figure salvate in `report/figures/` con `plt.savefig(..., dpi=300, bbox_inches="tight")`.
- `pd.read_csv(path, sep=";")` → **attenzione: il separatore è `;`**, non la virgola (con il default si ottiene una sola colonna).
- `df.shape`, `df.head()`, `df.dtypes`, `df.info()`.
- Fissare `RANDOM_STATE = 42` e lo stile grafico (`sns.set_theme(...)`) una volta sola.

**Da notare subito (già verificato sul file)**
- `sp_id` è letto come `float64` → convertirlo in intero/stringa: è un identificativo.
- 7 colonne numeriche sono lette come **stringa**: `price_median`, `back_legroom_median`, `front_legroom_median`, `fuel_tank_volume_median`, `height_median`, `length_median`, `width_median`. Il motivo è in §4.1.

**Nel report**: 2–3 righe: n. record, n. attributi, unità di analisi (un record = un venditore, valori già **aggregati** per mediana/proporzione sugli annunci).

---
## 2. Data Semantics

### 2.1 Teoria da richiamare (DM1.01 §2–3)
- Oggetti/attributi; tipo di dataset (record data, tabella).
- **Tipi di attributo** secondo Stevens: **nominale**, **ordinale**, **intervallo**, **rapporto**; proprietà e operazioni ammesse (=, <, +, ×).
- Discreto vs continuo; binario/asimmetrico.
- **Concetto chiave del dataset**: sono dati **aggregati per venditore**. Una "mediana del prezzo" è una statistica di secondo livello: descrive l'inventario tipico, non un'auto. Le `pct_*` sono **proporzioni in [0,1]**; le `dominant_*` sono **mode** dell'inventario (perdono la varietà: un venditore 51% SUV / 49% sedan risulta "suv").

### 2.2 Tabella semantica (da mettere nel report, compatta)
Una tabella con colonne: *Variabile · Significato · Tipo (Stevens) · Discreto/Continuo · Dominio/Unità · Note*. Raggruppare per famiglie per risparmiare spazio:

| Famiglia                | Variabili                                                                                         | Tipo                                                               | Note                                               |
| ----------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------------------- |
| Identificativo          | `sp_id`                                                                                           | nominale                                                           | da escludere dalle analisi                         |
| Attività del venditore  | `n_listings`, `n_listing_days`, `listing_span_days`                                               | rapporto, discreti                                                 | conteggi/durate, molto asimmetrici                 |
| Prezzo e mercato        | `price_median`, `savings_amount_median`, `daysonmarket_median`                                    | rapporto, continui                                                 | USD, giorni                                        |
| Età/uso                 | `year_median` (intervallo!), `vehicle_age_median`, `mileage_median`, `owner_count_median`         | `year` è **intervallo** (lo zero è arbitrario), gli altri rapporto | `owner_count` quasi-ordinale (1–6)                 |
| Motore/consumi          | `horsepower_median`, `engine_displacement_median` (cc), `city_/highway_fuel_economy_median` (MPG) | rapporto                                                           |                                                    |
| Dimensioni              | `back_/front_legroom`, `fuel_tank_volume`, `height`, `length`, `width`                            | rapporto                                                           | pollici / galloni (dataset USA)                    |
| Composizione inventario | `pct_isCab`, `pct_is_new`, `pct_salvage`, `pct_theft_title`                                       | rapporto, ∈[0,1]                                                   | `salvage`/`theft` quasi sempre 0                   |
| Modali inventario       | `dominant_body_type`, `_fuel_type`, `_transmission`, `_wheel_system`, `_listing_color`            | nominali                                                           |                                                    |
| Profilo venditore       | `franchise_status`, `new_used_profile`                                                            | nominali (il secondo è una discretizzazione di `pct_is_new`)       |                                                    |
| **Target**              | `seller_rating_class`                                                                             | **ordinale** (low < medium < high)                                 | discretizzazione di un rating continuo non fornito |

### 2.3 Discrepanze tra documentazione e dati (punto che fa bella figura)
- La descrizione dice `franchise_status ∈ {franchise, independent, mixed, unknown}` → nei dati ci sono **solo 2 valori** (franchise 6999, independent 6844).
- `new_used_profile ∈ {new_only, used_only, mixed, unknown}` → **nessun "unknown"**; `new_only` solo 31 venditori.
- `vehicle_age_median = anno di annuncio − year_median`: verificato che `year + age ≈ 2020` (std 0.4) → gli annunci sono raccolti intorno al 2020. Utile per interpretare tutto il resto.
- `new_used_profile` è **deterministicamente** ricavabile da `pct_is_new` (0 → used_only, 1 → new_only, altrimenti mixed): verificato con crosstab, zero eccezioni.
- Codici poco leggibili: `dominant_transmission ∈ {a, cvt, m, unknown}` → rinominare in `automatic`, `cvt`, `manual`, `unknown` (anche per avere grafici e tabelle leggibili). Stessa cura per `4x2` in `dominant_wheel_system`, che si sovrappone a `fwd`/`rwd`.

### 2.4 Codice
- Dizionario `semantics = {col: (tipo, descrizione, unità, ruolo)}`, con ruolo = id / predittore / target → `pd.DataFrame` → esportato in LaTeX con `df.to_latex()`.
- `df.nunique()` accanto al tipo per evidenziare variabili quasi-costanti.
- Controllo dei domini dichiarati: per ogni categorica, `set(df[col].unique())` confrontato con i valori elencati nel file `.txt`.
- `df["dominant_transmission"].replace({"a": "automatic", "m": "manual"})`.

---

## 3. Distribuzioni e statistiche (Data Understanding)

### 3.1 Teoria da richiamare (DM1.01 §5–12)
- Tendenza centrale: media, mediana, moda, media troncata; **media vs mediana → asimmetria**.
- Dispersione: range, varianza, deviazione standard, **IQR**; skewness.
- Istogrammi (scelta dei bin: Sturges/Freedman-Diaconis, natural binning vs equal frequency), box plot, bar chart per categoriche.
- Bivariata: scatter plot, scatter matrix, box plot condizionali, **tabelle di contingenza**.

### 3.2 Analisi univariata — numeriche
**Codice**
- `df.describe(percentiles=[.01,.25,.5,.75,.99]).T` + colonne aggiuntive `skew`, `kurt`, `n_zeros`, `n_unique`, `%NaN`. Una tabella sola, pulita, nel report (o in appendice compatta).
- Griglia di istogrammi (`plt.subplots(nrows, ncols)` + `sns.histplot(kde=True)`), e box plot affiancati.

**Cosa commentare (fatti già emersi)**
- **Asimmetria positiva forte**: `n_listings` (skew 5.3, max 4959 vs mediana 70), `daysonmarket_median` (8.8, max 1987), `listing_span_days` (2.2), `price_median` (3.4, max ~236k), `savings_amount_median` (2.4).
- **Asimmetria negativa**: `year_median` (−2.25) per la coda di auto d'epoca (1960–1988, 32 venditori).
- **Distribuzioni con massa a 0** (zero-inflated): `pct_salvage` (91% zeri), `pct_theft_title` (85%), `savings_amount_median` (37%), `pct_is_new` (53% zeri = venditori solo usato), `mileage_median` (621 zeri = venditori di nuovo).
- **Bimodalità** attesa: `mileage_median`/`vehicle_age_median` separano venditori di nuovo e di usato → mostrarlo con istogramma colorato per `new_used_profile`.
- Variabili con poca variabilità (`front_legroom`, std 0.8) → candidate a poca informatività.

### 3.3 Analisi univariata — categoriche
**Codice**: `value_counts(normalize=True)` + countplot orizzontali ordinati.

**Cosa commentare**
- Forte **sbilanciamento**: `dominant_fuel_type` gasoline 98.7%, `dominant_transmission` automatica 93.7% → quasi costanti, poco informative.
- `dominant_body_type`: suv 64%, sedan 22%, pickup 10%, il resto <2% → categorie rare da raggruppare (§6.3).
- `dominant_listing_color`: "unknown" 1510 (11%) = **mancante travestito**.
- **Target**: medium 54.7%, high 26.6%, low 18.6% → classi sbilanciate (anticipare: stratificazione nello split, metriche macro-F1 in classificazione).

### 3.4 Analisi bivariata e rispetto al target
**Codice**
- Box plot / violin delle numeriche **per classe di rating** (`sns.boxplot(x=target, y=col, order=['low','medium','high'])`).
- **KDE per classe** (`sns.kdeplot(data=df, x=col, hue=target, common_norm=False)`): mostra meglio dei box plot se le tre distribuzioni si sovrappongono (con classi sbilanciate serve `common_norm=False`).
- `pd.crosstab(cat, target, normalize="index")` + barre impilate al 100% (lettura come **probabilità condizionate** P(rating | categoria)).
- Pairplot di un sottoinsieme (5–6 variabili scelte, non tutte!) con `hue=target`.
- Scatter mirati: `price` vs `mileage`, `year` vs `mileage`, `n_listings` vs `n_listing_days` (scala log).
- **Coordinate parallele** (DM1.01 §11, `pd.plotting.parallel_coordinates`) su 4–6 variabili **già standardizzate** e su un campione stratificato (~300 righe, altrimenti è illeggibile), colorate per classe. È una visualizzazione multivariata vista a lezione e poco usata: utile per il bonus *Innovation*.

**Come commentare**: non "si vede la distribuzione", ma "la classe *high* tende a …, quindi …".

**Cosa commentare**
- Le relazioni con il target sono **deboli** (Spearman con il target ordinale: massimo |ρ| ≈ 0.26 per `n_listings` e `n_listing_days`, negativo: venditori più grandi → rating più basso). Coerente con la slide 4 ("hard classification task") → dirlo esplicitamente.
- `franchise_status`: gli **independent** hanno più "high" (32.8% vs 20.6%) e meno "low" → insight interpretabile.
- `used_only` ha profilo di rating simile agli independent; `mixed` simile ai franchise (le due variabili sono quasi la stessa informazione, vedi §7.3).

---

## 4. Data Quality (errori, incoerenze, duplicati)

### 4.0 Quadro per dimensioni della qualità (DM1.01 §4.2)
Aprire la sezione con questa tabella: segue la struttura vista a lezione e il valutatore la riconosce subito. Le righe rimandano ai paragrafi che seguono.

| Dimensione | Domanda | Riscontro nel dataset | Azione |
|---|---|---|---|
| **Accuratezza sintattica** | i valori appartengono al dominio/formato? | ~1.580 numeri corrotti in 7 colonne; `sp_id` letto come float; `pct_*` tutte in [0,1] ✓ | riparazione (§4.1), cast dei tipi |
| **Accuratezza semantica** | valori nel formato giusto ma impossibili? | legroom 0 o 67, `mileage = 0` su venditori di usato, consumi 72 MPG su "gasoline" | caso per caso: errore → NaN, vero → si tiene (§4.2) |
| **Completezza** | quanto manca, anche in forma mascherata? | `wheel_system` 76%, `engine_displacement` 24.5%, colore "unknown" 11% | §5 |
| **Coerenza** | gli attributi sono coerenti tra loro? | `year + age ≈ 2020`, profilo ↔ `pct_is_new` ✓; valori di categoria diversi da quelli documentati | §2.3, §4.3 |
| **Sbilanciamento** | classi e categorie equilibrate? | target 55/27/19%; gasoline 98.7%, automatico 93.7% | segnalare qui; si gestisce in classificazione (stratificazione) e con il raggruppamento delle categorie rare (§6.3) |
| **Attualità** (*timeliness*) | a quando risalgono i dati? | annunci intorno al 2020 (da `year + age`); 32 venditori con auto 1960–1988 | dichiarare il periodo; le auto d'epoca sono una nicchia reale, non dati vecchi |
| **Unicità** | duplicati? | 0 righe duplicate, 0 `sp_id` ripetuti | nessuna (§4.4) |

### 4.1 Errori sintattici: numeri corrotti (problema principale del dataset)
**Osservazione**: 7 colonne numeriche contengono stringhe come `38.650.000.000.000.000` (legroom), `6.619.999.999.999.990` (altezza), `26.037.495.000.000.000` (prezzo). Sono numeri decimali **rovinati da un'esportazione con separatore delle migliaia** (es. 38.65 → `38.650.000.000.000.000`).

Conteggio: price 4, back_legroom 272, front_legroom 247, fuel_tank 115, height 426, length 28, width 490 (totale ~1.580 celle).

**Tre opzioni da discutere nel report** (questa discussione vale punti di "justify every choice"):
1. `pd.to_numeric(errors="coerce")` → diventano NaN e poi si imputano. Semplice, ma perde informazione vera.
2. **Ricostruzione**: tolgo i punti, ottengo le cifre e provo tutte le posizioni del decimale; tengo il candidato che cade nel range plausibile della colonna (es. tra lo 0.1° e il 99.9° percentile dei valori puliti). Testato: ricostruzione **univoca nel 99.7% dei casi**; restano 2 prezzi ambigui e 3 valori senza candidato → NaN.
3. Ibrida: ricostruzione dove univoca, NaN altrove. **← consigliata** (spunto per il bonus *Innovation*).

Verifica obbligatoria dopo la riparazione: confrontare istogramma dei valori ricostruiti vs valori puliti (devono sovrapporsi).

### 4.2 Valori impossibili o sospetti (controlli di dominio)
| Controllo | Risultato | Decisione da discutere |
|---|---|---|
| `back_legroom = 0` | 2 venditori, pickup | probabilmente pickup a cabina singola (nessun sedile posteriore): **valore vero ma semanticamente "non applicabile"**; oppure mancante travestito → scegliere e motivare |
| `front_legroom` 54–67 | 2 SUV | fuori scala fisica → errore → NaN |
| `height` > 90 | 4 van | plausibile (van alti) → tenere |
| `city_fuel_economy` > 60 | 10 venditori; 8 elettrici (MPGe ~120) | **outlier veri** (unità MPGe), 2 "gasoline" a ~72 → sospetti, probabilmente ibridi mal etichettati |
| `highway < city` | 18 (ibridi/elettrici) | fisicamente coerente per ibridi/EV → tenere, ma spiegare |
| `year_median` 1960–1988 | 32 venditori, prezzi alti | concessionari di **auto d'epoca**: outlier veri, non errori |
| `daysonmarket_median` max 1987, `listing_span_days` max 3553 | 65 > 1 anno | plausibili ma estremi → coda lunga, trattare con log |
| `mileage = 0` con `pct_is_new < 0.5` | 4 | incoerenza → segnalare / NaN |

### 4.3 Coerenza tra variabili (controlli già fatti, tutti da citare)
- `year_median + vehicle_age_median ≈ 2020` → coerenti.
- `listing_span_days ≥ n_listing_days − 1` → sempre vero ✓. Attenzione a non usare `n_listing_days ≤ listing_span_days`: fallisce su 20 venditori corretti (es. annunci in un solo giorno: 1 giorno, span 0) e produrrebbe falsi errori.
- `n_listing_days ≤ n_listings` → sempre vero ✓.
- `new_used_profile` ↔ `pct_is_new` → perfettamente coerenti ✓.
- `used_only` con `mileage = 0` → 0 casi ✓.

> Anche i controlli "passati" vanno scritti in una riga: mostrano rigore metodologico.

### 4.4 Duplicati
- Righe duplicate: 0; `sp_id` duplicati: 0; duplicati ignorando `sp_id`: 0. Una riga nel report.

---

## 5. Valori mancanti

### 5.1 Teoria (DM1.01 §14, DM1.02 §8)
- Cause (non raccolto, non applicabile, guasto, rifiuto); **mancanti travestiti** (0, "unknown").
- Strategie: eliminare attributo / eliminare record / imputare (media, mediana, moda, **per gruppo**, da distribuzione, **con modello/regressione**).
- Imputare **non deve alterare la distribuzione** (es. media globale → picco artificiale e varianza ridotta).

### 5.2 Mappa dei mancanti
**Codice**: tabella `isna().sum()` e `%`; heatmap/matrice dei mancanti (`sns.heatmap(df.isna())` su campione) per vedere se sono **in blocco**.

| Variabile | NaN | % | Strategia proposta |
|---|---|---|---|
| `dominant_wheel_system` | 10.518 | **76.0%** | **eliminare la colonna** (troppo vuota); in alternativa categoria "unknown" — motivare |
| `engine_displacement_median` | 3.393 | **24.5%** | non sono elettrici (98.7% gasoline) → mancante "casuale" di raccolta. Imputare **con regressione** da `horsepower` + `fuel_tank_volume` (corr. 0.71–0.83) o mediana per `body_type`; in alternativa eliminare (è ridondante con hp/fuel tank, §7) |
| `pct_isCab`, `pct_salvage`, `pct_theft_title`, `owner_count_median` | 27 (39 owner) | 0.2% | **gli stessi 27 record** hanno NaN in blocco, e 26 di loro sono venditori `new_only` (su 31 in tutto): sono mancanti **"non applicabili"** (un'auto nuova non ha proprietari precedenti, non è ex taxi né incidentata) → porre a **0**, **non** eliminare le righe (si perderebbe l'84% della categoria `new_only`) |
| colonne riparate (§4.1) + piccoli NaN (`horsepower`, dimensioni, fuel economy) | <0.2% ciascuna (fino a ~3% dopo la coercizione se non si ripara) | | mediana per gruppo (`dominant_body_type`), perché dimensioni/consumi dipendono dal tipo di carrozzeria |
| `dominant_listing_color = "unknown"` | 1.510 | 10.9% | mancante travestito: tenere "unknown" come categoria (non imputabile in modo sensato) |
| `dominant_fuel_type`/`transmission = "unknown"` | 1 e 6 | ~0% | moda |

### 5.3 Il fatto di mancare porta informazione?
Prima di scegliere la strategia, per le variabili con molti mancanti (`engine_displacement_median`, `dominant_wheel_system`) controllare se le righe **con** mancante sono diverse da quelle **senza**:
- `df.groupby(df[col].isna())[altre_numeriche].median()` → confronto delle mediane tra i due gruppi;
- `pd.crosstab(df[col].isna(), df[target], normalize="index")` → la distribuzione del rating cambia?
- `pd.crosstab(df[col].isna(), df["franchise_status"])` → già visto: il 76% di NaN di `wheel_system` è distribuito allo stesso modo tra franchise e independent.

Interpretazione:
- **nessuna differenza** → mancanti "casuali": imputazione o eliminazione senza problemi;
- **differenze nette** → il mancante è **informativo**: conviene aggiungere un indicatore binario (`engine_displacement_missing = 1/0`) oppure, per le categoriche, tenere `unknown` come categoria vera.

Usare il target **solo per descrivere** questo confronto, mai per imputare.

### 5.4 Esperimento di imputazione (punto "Experimentation")
Per `engine_displacement_median` confrontare 4 strategie, come nel lab Titanic con `Age`:
1. mediana globale: `fillna(df[col].median())`;
2. mediana per `dominant_body_type`: `groupby(...)[col].transform(lambda x: x.fillna(x.median()))`;
3. estrazione casuale dalla distribuzione osservata (DM1.02 §8): `df[col].dropna().sample(n_mancanti, replace=True, random_state=42)`;
4. regressione lineare da `horsepower_median` (+ `fuel_tank_volume_median`).

Per ognuna: istogramma "originale + imputati in evidenza" e tabella media/std **prima e dopo**. Effetti attesi: la mediana globale crea un picco artificiale e abbassa la std; l'estrazione casuale preserva la forma ma ignora le altre variabili; la regressione sfrutta la correlazione con la potenza. Scegliere e motivare.

> **Attenzione al data leakage**: non usare **mai** il target per imputare. E segnalare nel report che, per la classificazione, imputazioni e scaling andranno "fittati" solo sul training set.

---

## 6. Outlier e trasformazioni

### 6.1 Teoria (DM1.01 §13, DM1.02 §11–12)
- Outlier: **errore** (rimuovere/correggere) vs **valore vero** (tenere e ridurne l'effetto). Il dilemma del prof: capire in quale caso siamo.
- Rilevazione univariata: regola **1.5·IQR** (e 3·IQR per estremi); multivariata: scatter plot (e più avanti DBSCAN/clustering).
- Trasformazioni: **log** (asimmetria positiva, valori su più ordini di grandezza), radice (conteggi), normalizzazione min-max / z-score.

### 6.2 Outlier
**Codice**
- Funzione `iqr_outliers(s, k=1.5)` → tabella per variabile: n. outlier a 1.5·IQR e a 3·IQR, % sul totale.
- Box plot prima/dopo.

**Cosa scrivere**
- Con variabili molto asimmetriche la regola IQR segnala **migliaia** di "outlier" (es. `n_listings`): non sono errori, è la coda di una distribuzione log-normale → **non vanno eliminati**, si risolve con il log (dopo il log quasi spariscono: mostrarlo con un numero).
- Errori veri (da §4.2) → NaN/correzione.
- Outlier veri e interessanti (auto d'epoca, EV, mega-dealer) → **tenuti**, segnalati come possibili problemi per K-means (sensibile agli outlier) e come rumore per DBSCAN.

### 6.3 Trasformazioni delle variabili (con giustificazione per ognuna)
| Trasformazione | Variabili | Perché |
|---|---|---|
| `log1p` | `n_listings`, `n_listing_days`, `listing_span_days`, `daysonmarket_median`, `price_median`, `savings_amount_median`, `mileage_median` | skew forte, più ordini di grandezza; `log1p` gestisce gli zeri. Mostrare **istogramma prima/dopo** + skew prima/dopo in tabella |
| nessuna (già in [0,1]) | `pct_*` | proporzioni; `pct_salvage` e `pct_theft_title` quasi costanti → valutare **binarizzazione** (`has_salvage = pct > 0`) |
| raggruppamento categorie rare | `dominant_body_type` (coupe, hatchback, van, convertible, minivan, wagon → "other" o raggruppamenti semantici: van+minivan), `dominant_listing_color` (brown, green, gold, teal → "other") | categorie con < 1% di supporto creano rumore e problemi nel one-hot |
| encoding | target ordinale → {low:0, medium:1, high:2}; nominali → one-hot | servirà per correlazione e classificazione |
| **normalizzazione** z-score (o min-max) | tutte le numeriche, **dopo** il log | il clustering usa distanze: senza scaling `mileage` (decine di migliaia) domina `pct_*` |

### 6.4 Feature engineering (spunto per il bonus, solo se c'è spazio)
Idee semplici e motivabili:
- `listings_per_day = n_listings / n_listing_days` (intensità di attività: separa la dimensione dall'attività).
- `combined_fuel_economy` = media pesata city/highway (EPA usa 55/45) → sostituisce due variabili correlate 0.94.
- `discount_ratio = savings_amount / price` (sconto relativo, più confrontabile tra fasce di prezzo).
- `has_salvage`, `has_theft` binarie (§6.3).

Ogni feature nuova va giustificata e, idealmente, mostrata con un box plot per classe di rating.

---

## 7. Correlazioni ed eliminazione di variabili

### 7.1 Teoria (DM1.01 §12, DM1.02 §6)
- **Pearson** (relazioni lineari, sensibile agli outlier) vs **Spearman** (monotone, robusta, adatta a variabili asimmetriche). Calcolarle entrambe e commentare dove differiscono.
- Correlazione ≠ causalità.
- Feature subset selection: attributi **ridondanti** (alta correlazione tra loro) e **irrilevanti**; approccio **filter**.
- Categoriche: tabelle di contingenza (e, come extra, **Cramér's V** da χ²).

### 7.2 Matrice di correlazione
**Codice**: `df[num].corr(method="spearman")` → heatmap triangolare (`mask = np.triu(...)`), `vmin=-1, vmax=1`, cmap divergente, annotazioni solo se leggibili. Mettere nel report **una** heatmap ben fatta + una tabella delle coppie con |ρ| > 0.7.

### 7.3 Coppie fortemente correlate (già trovate) e decisione
| Coppia | Pearson | Spearman | Decisione proposta |
|---|---|---|---|
| `year_median` – `vehicle_age_median` | −0.996 | −0.984 | **ridondanti per costruzione** (age = 2020 − year) → tenere **solo `vehicle_age_median`** (rapporto, più interpretabile) |
| `n_listings` – `n_listing_days` | 0.84 | 0.96 | tenerne una (o creare `listings_per_day`) |
| `city_fuel_economy` – `highway_fuel_economy` | 0.94 | 0.94 | fondere in `combined_fuel_economy` o tenerne una |
| `mileage` – `vehicle_age` / `year` | ±0.82 | ±0.93 | correlazione attesa (auto più vecchie → più km); tenere entrambe o solo una a seconda del modulo |
| `pct_is_new` – `year`/`mileage`/`age` | ~0.7 | ~0.87 | blocco "nuovo vs usato" → valutare |
| `engine_displacement` – `fuel_tank_volume` / `horsepower` | 0.83 / 0.71 | 0.81 / 0.73 | se `engine_displacement` ha 24.5% NaN, è la candidata naturale all'eliminazione |
| `fuel_tank_volume` – `length` | 0.84 | 0.76 | blocco "dimensione del veicolo" |
| `pct_is_new` – `new_used_profile` | deterministica | | eliminare `new_used_profile` (o tenerla solo per pattern mining) |
| `franchise_status` – `new_used_profile` | crosstab: franchise→mixed 91%, independent→used_only 99% | | quasi la stessa informazione → Cramér's V per quantificare |

**Regola di decisione da dichiarare** (es.): se |ρ_Spearman| ≥ 0.9 elimino una delle due, tenendo quella più interpretabile / con meno NaN / più correlata al target; tra 0.7 e 0.9 discuto caso per caso. Dichiararla prima, applicarla poi.

**Tre strade per ogni coppia o gruppo ridondante** (DM1.02 §6), da scegliere e motivare:
1. **eliminare** una variabile (la scelta più interpretabile);
2. **combinare** le variabili in una nuova feature (es. `combined_fuel_economy`, `listings_per_day`, §6.4);
3. **PCA sul gruppo** (DM1.02 §5): per il blocco "dimensioni del veicolo" (`length`, `width`, `height`, `fuel_tank_volume`, `horsepower`, `engine_displacement`) una PCA sulle variabili standardizzate può riassumere tutto in 1–2 componenti ("taglia del veicolo"). Mostrare la varianza spiegata e scegliere quante componenti tenere. Svantaggio da dire: le componenti sono meno interpretabili, quindi meglio usarle per il clustering che per gli alberi di decisione.

### 7.4 Variabili poco informative
- `sp_id` (identificativo), `dominant_fuel_type` (98.7% gasoline), `dominant_transmission` (93.7% automatico), `dominant_wheel_system` (76% NaN), `pct_salvage`/`pct_theft_title` (quasi tutti 0) → eliminare o binarizzare, motivando.

---

## 8. Output finale della parte 1 (ponte verso gli altri moduli)

Salvare in `data/processed/`:
1. `df_clean.csv` — dataset ripulito (errori corretti, mancanti gestiti, variabili ridondanti rimosse), **non scalato**, con target. Base per classificazione/regressione.
2. `df_clustering.csv` — solo numeriche selezionate, log-trasformate + z-score, **senza target** (il target si usa solo dopo, per interpretare i cluster).
3. (più avanti) versione discretizzata per il pattern mining (binning equal-frequency delle numeriche).

Nel report chiudere la sezione con una **tabella riassuntiva delle decisioni**: *variabile → problema → azione → motivazione*. È la cosa che il valutatore legge più volentieri e vale per il bonus *Organization*.

**"Contratto" del dataset finale** (da scrivere nel notebook e, in breve, nel report):
- variabili tenute / eliminate / create, con il motivo;
- per ogni variabile imputata: metodo usato e numero di valori imputati;
- trasformazioni applicate (log, encoding, scaling) e su quale versione del dataset;
- shape finale di ciascun file salvato.

**Controlli automatici prima di salvare**:
- `assert df_clean.isna().sum().sum() == 0` (oppure elenco esplicito dei NaN lasciati di proposito);
- tipi coerenti (`df_clean.dtypes`), nessuna colonna testo rimasta tra le numeriche;
- stesse righe in tutti i file (stessi `sp_id`), così i risultati dei moduli successivi restano confrontabili.

---

## 9. Budget del report per la parte 1 (~4–5 pagine)

| Sezione | Spazio | Contenuto minimo |
|---|---|---|
| Intro dataset + semantica | ~0.75 pag | tabella semantica compatta, discrepanze con la documentazione |
| Distribuzioni e statistiche | ~1.25 pag | 1 griglia di istogrammi, 1 figura categoriche, 1 figura vs target, tabella statistiche ridotta |
| Qualità, mancanti, outlier | ~1.5 pag | tabella per dimensioni della qualità, riparazione numeri corrotti, tabella mancanti + strategie (confronto imputazioni in 1 figura), tabella controlli di dominio |
| Trasformazioni | ~0.5 pag | log prima/dopo (1 figura), scaling |
| Correlazioni ed eliminazione | ~0.75 pag | heatmap Spearman, tabella coppie, regola di decisione, variabili eliminate |
| Tabella riassuntiva decisioni | ~0.25 pag | |

Ogni figura: numerata, con didascalia e **richiamata e commentata nel testo**.

---

## 10. Checklist finale prima della consegna

- [ ] Separatore `;` gestito, tipi corretti (`sp_id` non numerico, 7 colonne stringa convertite).
- [ ] Tabella semantica con tipo di Stevens per ogni variabile; `year` = intervallo, target = ordinale.
- [ ] Discrepanze documentazione vs dati citate; codici di `dominant_transmission` rinominati.
- [ ] Statistiche descrittive + skew; commento media vs mediana.
- [ ] Distribuzioni di tutte le variabili esaminate (nel report solo le più significative, il resto riassunto in una frase).
- [ ] Bivariata e vs target (box plot, KDE, crosstab, coordinate parallele), con commento sulla debolezza delle relazioni.
- [ ] Tabella della qualità per dimensioni (§4.0).
- [ ] Riparazione dei numeri corrotti spiegata e verificata.
- [ ] Controlli di dominio e di coerenza (anche quelli superati).
- [ ] Mancanti: tabella, pattern in blocco, verifica del mancante informativo, confronto di 4 strategie, scelta motivata, nessun uso del target per imputare.
- [ ] Outlier: errori vs veri, decisione motivata, effetto del log.
- [ ] Trasformazioni con prima/dopo.
- [ ] Heatmap Spearman (+ confronto con Pearson), regola di eliminazione dichiarata e applicata, alternativa PCA discussa.
- [ ] Dataset processati salvati con "contratto" e controlli automatici; tabella riassuntiva delle decisioni.
- [ ] Nessun grafico senza commento; assi e unità leggibili; font ≥ 9pt.
