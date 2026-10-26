
Perfetto — partiamo proprio da zero. Segui l'ordine: prima metti in piedi l'ambiente (Parte A), poi esegui la scaletta fase per fase (Parte B). Ti do i comandi esatti da digitare, ma **non** le risposte analitiche: le decisioni (cosa eliminare, come imputare, quali feature creare) restano tue.

---

# PARTE A — Setup da zero

## A1. Cosa installare (una volta sola)

| Software | A cosa serve | Dove prenderlo |
|---|---|---|
| **Python 3.x** | Il linguaggio | Ce l'hai già (3.14) — verificabile con `python --version` |
| **VS Code** | Scrivere ed eseguire il codice (consigliato) | code.visualstudio.com |
| **GitHub Desktop** | Gestire la repo senza terminale | desktop.github.com |
| Estensioni VS Code | Dopo aver aperto VS Code: cerca e installa **Python** e **Jupyter** (di Microsoft) | Pannello estensioni (icona cubi a sinistra) |

## A2. Collegare la repo al computer (una volta sola)

1. Apri **GitHub Desktop** → File → **Clone repository** → scegli `DM1-project-26-27` → cartella comoda (es. `Documenti\uni\DM1-project-26-27`)
2. Clicca **Open in Visual Studio Code** (o da VS Code: File → Open Folder → scegli la cartella della repo)



## A3. Struttura della cartella (creala subito, ordine = salute mentale)

Dentro la cartella della repo crea queste cartelle (tasto destro → New Folder in VS Code):

```
DM1-project-26-27/
├── data/                  ← il dataset originale (mai modificato!)
│   └── seller_info_dm1_2627.csv
├── notebooks/             ← i tuoi notebook (01_, 02_, ...)
├── src/                   ← funzioni riutilizzabili (per dopo)
├── report/                ← figure finali per il report
└── README.md              ← c'è già (descrizione progetto)
```

Poi **copia** `seller_info_dm1_2627.csv` (sta in `Parte 1 - DATA MINING_ FUNDAMENTALS\Project\`) dentro `data/`. Il file originale resta dov'è: lavorerai solo su questa copia.

## A4. Ambiente Python e librerie (una volta sola)

Apri il **terminale in VS Code** (Terminal → New Terminal) e digita:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pandas numpy matplotlib seaborn scikit-learn jupyter ipykernel
```

Note da principiante:
- `.venv` è un "recinto" con le librerie di questo progetto solo (vedrai la scritta `(.venv)` nel terminale)
- Se `Activate.ps1` da errore di permessi, digita prima: `Set-ExecutionPolicy -Scope Process RemoteSigned`
- Il `.gitignore` scelto su GitHub (Python) già esclude `.venv` e `__pycache__` dal versionamento — controlla che ci sia il file `.gitignore` nella cartella

## A5. Primo notebook (il "ciao mondo")

1. VS Code: dentro `notebooks/` → tasto destro → New File → `01_data_understanding_preparation.ipynb`
2. In alto a destra seleziona l'interprete Python (quello dentro `.venv`) se chiesto
3. Prima cella — esegui con **Shift+Invio**:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("../data/seller_info_dm1_2627.csv")
print(df.shape)
df.head()
```

Se vedi `(13843, 33)` e una tabella: **ambiente funzionante**. Da qui in poi tutto il lavoro è "aggiungere celle al notebook".

## A6. Abitudini Git (tutti i giorni)

Con **GitHub Desktop** (il più semplice):
1. Prima di iniziare a lavorare: **Fetch/Pull** (prendi i cambi dei compagni)
2. Lavori normalmente e salvi (Ctrl+S)
3. A fine sessione: scrivi un messaggio breve ("aggiunto audit missing values") → **Commit to main** → **Push origin**

Regole: commit frequenti e piccoli; mai committare il file `.venv` o i checkpoint dei notebook (il `.gitignore` ci pensa); il dataset sì (repo privata).

---

# PARTE B — La scaletta operativa, approfondita

Premessa: nel notebook usa **commenti markdown** (# titoli di sezione) come quelli qui sotto, così il notebook è già l'indice del report.

## Fase 1 — Data Semantics (il "chi è chi" del dataset)

**Obiettivo**: capire e documentare cosa rappresenta ogni colonna.

Passi concreti:
1. `df.shape`, `df.dtypes`, `df.head(3)`, `df.tail(3)` — annota tipi informatici (float64, object...)
2. Crea una **tabella-semantica** (foglio Excel o markdown): per ogni colonna scrivi *significato* (dal file `seller_level_vehicle_dataset_description.txt`), *tipo* (nominale / ordinale / intervallo / ratio — vedi DM1.01 §3), *ruolo* (id / predittore / target)
3. Controlli di dominio: per ogni colonna categorica `df[col].value_counts()` — i valori trovati coincidono con quelli dichiarati nel TXT?
4. Controlli di coerenza (costruisci maschere booleane, es. `df[condizione_sbagliata]`):
   - `sp_id` univoco? `df["sp_id"].nunique()` vs `df.shape[0]` — righe duplicate? `df.duplicated().sum()`
   - le `pct_*` stanno nell'intervallo [0, 1]?
   - `n_listing_days <= listing_span_days` sempre vero?
   - `vehicle_age_median` coerente con `year_median`? (quale "anno di listing" implicito ottieni sommandoli?)
5. Nota: `sp_id` è un identificatore → **non è un predittore**, ma ricordati di dichiararlo nel report

**Output report**: la tabella semantica + un paragrafo sulle incoerenze/incoerenze trovate.
**Decisioni aperte (tue)**: come rendere leggibili i codici opachi (es. `a`, `cvt`, `m`); se qualche colonna è ambigua nel significato.

## Fase 2 — Distribuzioni e statistiche univariate

**Obiettivo**: descrivere ogni variabile da sola: forma, centro, dispersione, valori strani.

Per ogni **numerica** (24 colonne):
1. `df.describe()` — guarda **media vs mediana**: se differiscono molto, la distribuzione è asimmetrica
2. Istogramma: `sns.histplot(df[col], bins=...)` — i bin: usa Sturges (`k = ceil(log2(n)) + 1` ≈ 15 per n=13843) e prova anche un natural binning per confrontare
3. Boxplot: `sns.boxplot(x=df[col])` — annota i punti oltre i baffi (1.5·IQR)
4. Commenta per ogni variabile: simmetrica / coda destra / coda sinistra / picchi / valori impossibili

Per ogni **categorica** (8 colonne):
1. Bar chart: `df[col].value_counts().plot.bar()` — annota le **classi rare** (categorie con poche unità) senza decidere ancora cosa farne
2. Cerca "mancanti travestiti": categorie tipo `unknown`, stringhe vuote, e zeri sospetti nelle numeriche (un `0` può significare "vero zero" oppure "non raccolto" — DM1.01 §14)

**Suggerimento organizzativo**: non fare 32 figure separate; raggruppa in griglie tematiche (motore / consumi / dimensioni / attività / proporzioni / inventario) con `plt.subplots(...)` come nel lab Titanic.

**Output report**: tabella riepilogativa (colonna → min/Q1/mediana/media/Q3/max → forma → anomalie) + figure commentate.
**Decisioni aperte**: quali variabili meritano un'analisi più approfondita in Fase 3.

## Fase 3 — Esplorazione bivariata (relazioni e target)

**Obiettivo**: capire cosa "si muove insieme" e cosa distingue le classi del target.

1. **Contro il target** `seller_rating_class`:
   - numeriche: `sns.boxplot(x="seller_rating_class", y=col, data=df)` e `sns.kdeplot(..., hue="seller_rating_class")` — confronta medie/median per classe
   - categoriche: `pd.crosstab(df[col], df["seller_rating_class"], normalize="index")` + grafico a barre impilate → leggi le **probabilità condizionate**
2. **Tra predittori**: `sns.pairplot(df[poche_colonne], hue="seller_rating_class")` sulle coppie tematiche più promettenti (es. prezzo–età–chilometri)
3. Extra (facoltativo, "Innovation"): un grafico multivariato tipo coordinate parallele su 4-6 variabili

**Output report**: boxplot/KDE condizionati + heatmap della crosstab, **ognuno commentato in termini di differenze tra classi** (non "si vede la distribuzione" ma "la classe high tende a... perciò...").
**Decisioni aperte**: quali relazioni sembrano più utili per i moduli successivi.

## Fase 4 — Data quality assessment (il checklistone)

**Obiettivo**: rispondere esplicitamente alle 5 dimensioni della qualità (DM1.01 §4.2), una sezione per ciascuna.

1. **Accuratezza sintattica**: per ogni colonna, i valori appartengono al dominio? (`pct_*` in [0,1]? prezzi/chilometri/età non negativi? unità di misura coerenti?)
2. **Accuratezza semantica**: valori "nel dominio ma impossibili" — es. consumi estremi, dimensioni fuori scala, altezze/lunghezze di veicoli plausibili? Per ognuno: **errore o valore reale?** (il dilemma di DM1.01 §13) e annota la motivazione
3. **Completezza**: audit dei mancanti (vedi Fase 5) + mancanti travestiti (zeri di default)
4. **Unbalanced**: frequenza del target (medium ≈ 55%) e delle categorie dominanti → segnala, non risolvere
5. **Timeliness**: anno di listing implicito → in che periodo sono raccolti i dati? record fuori epoca?

**Output report**: tabella "dimensione → riscontro → azione". È una delle tabelle che il docente cerca.

## Fase 5 — Valori mancanti (il pezzo che fa la differenza)

**Obiettivo**: quantificare, capire *perché* mancano, confrontare strategie, scegliere e motivare.

1. Quantifica: `df.isnull().sum()` e `df.isnull().mean() * 100` — tabella colonna → n° → %
2. **Pattern**: le righe con mancante in una colonna sono "diverse" dalle altre? Confronta la distribuzione delle altre variabili (e del target) tra righe con/senza mancante. Se sono diverse → il mancante è **informativo**, e la strategia cambia
3. Per le variabili con pochi mancanti e per quelle con molti, **confronta almeno 3 strategie** (schema del lab Titanic §11):
   - media/mediana/moda globali: `df[col].fillna(df[col].median())`
   - per segmento: `df.groupby([altra_variabile])[col].transform(lambda x: x.fillna(x.median()))`
   - estrazione casuale dalla distribuzione osservata: `df[col].dropna().sample(n_mancanti, replace=True)`
4. Per ogni strategia: grafico "distribuzione originale + valori imputati in evidenza" e confronto di media/std **prima e dopo** (la media globale crea un picco artificiale e abbassa la std — è l'effetto da verificare)
5. Per le variabili con moltissimi mancanti: considera l'**eliminazione della colonna** (DM1.01 §14.2) vs mantenerla come categoria `unknown` vs usarla come indicatore binario "era mancante" — è una decisione da motivare nel report

**Output report**: tabella dei mancanti + grafici pre/post a confronto + paragrafo "perché ho scelto X".
**Decisioni aperte**: strategia per ciascuna colonna (questa è la tua scelta più importante del modulo 1).

## Fase 6 — Outlier

**Obiettivo**: trovarli, classificarli, decidere il trattamento.

1. Rilevamento univariato: per ogni numerica calcola Q1, Q3, IQR e i recinti `Q1-1.5*IQR`, `Q3+1.5*IQR` (e il 3·IQR per gli estremi, come nel lab) — quanti per colonna?
2. Rilevamento multivariato: outlier visibili solo in scatter (punti isolati su coppie di variabili correlate)
3. Classifica ogni gruppo di outlier in **errore / reale / dubbio** (DM1.02 §8: missing vs unknown vs not-valid):
   - errore → correggi o trattali come mancanti (rientrano nella Fase 5)
   - reale → tienili, ma valuta di ridurne l'effetto (Fase 7) o di usare statistiche robuste (mediana)
4. Annota **quante righe** elimini/correggi e perché — mai rimozioni silenziose

**Output report**: tabelle/barre "n° outlier per colonna" + discussione dei casi più eclatanti.
**Decisioni aperte**: soglie, chi eliminare, chi tenere.

## Fase 7 — Trasformazioni

**Obiettivo**: decidere se e come trasformare le variabili per i moduli successivi.

1. Dalla Fase 2 prendi le distribuzioni fortemente asimmetriche → prova `np.log1p(col)` (log(1+x), sicuro con gli zeri), `np.sqrt(col)`, e confronta istogrammi **prima/dopo**
2. Ragiona sul trade-off: variabile originale (interpretabile) vs trasformata (meglio per distanze/clustering/PCA)
3. Normalizzazione: confronta min-max (`(x - min) / (max - min)`) vs z-score (`(x - media) / std`) — sapendo che media/std sono sensibili agli outlier. Decidi **quale scaler** userai nei moduli 2-3 e scrivilo nel report (non applicarlo necessariamente subito)
4. Se applichi una trasformazione, salva sia la versione originale sia quella trasformata (due colonne o due dataframe)

**Output report**: figure "prima/dopo" affiancate con motivazione della scelta.
**Decisioni aperte**: quali variabili trasformare, quale scaler.

## Fase 8 — Correlazioni e eliminazione variabili (bullet 4)

**Obiettivo**: trovare ridondanze e decidere cosa tenere.

1. Matrice di correlazione: `df.corr(numeric_only=True)` (Pearson) e `df.corr(numeric_only=True, method="spearman")` — heatmap `sns.heatmap(..., annot=False)` e versione con `annot=True` su un sottoinsieme
2. Individua le coppie con |r| alta (soglia tipica del corso: >0.9 per l'eliminazione, >0.7 per l'attenzione) — nel dataset ci sono coppie quasi duplicate e "ciuffi" correlati
3. Per ogni coppia ridondante scegli **una** strada e motivala (DM1.02 §6):
   - eliminane uno (quale? in base a interpretabilità / mancanti / correlazione col target)
   - combinane due in una nuova feature (es. rapporto o media)
   - PCA sul gruppo (e quante componenti tenere, dalla varianza spiegata)
4. Distingui **ridondanti** (stessa info) da **irrilevanti** (poca info sul task): per i secondi puoi citare filter/wrapper/embedded (DM1.02 §6.1) e magari provare un metodo semplice di feature selection
5. Facoltativo: correlazione delle numeriche con il target codificato (low=0, medium=1, high=2) — utile come esplorazione, sapendo che è un indicatore debole

**Output report**: heatmap commentata + tabella "coppia → |r| → decisione → motivazione" (risponde direttamente al bullet "eventual elimination of variables").
**Decisioni aperte**: chi eliminare, chi combinare, soglie.

## Fase 9 — Feature creation, encoding e dataset prepared

**Obiettivo**: costruire il dataset "pulito" che userai per clustering, classification e pattern mining.

1. **Feature creation di dominio** (DM1.02 §7): crea 2-3 variabili nuove che catturano informazione più efficiente degli originali (pattern del corso: densità = massa/volume, BMI, efficienza, prezzo-per-persona). Nel vostro dominio: rapporti prezzo/età, attività/tempo, efficienza consumi, composizione inventario... sono **idee tue**, da motivare
2. **Encoding**: `pd.get_dummies(df, columns=[...])` per i nominali (one-hot); codifica numerica solo dove esiste un ordine reale
3. **Classi rare**: decidere se raggrupparle in `other` o tenerle (in base a numerosità e significato) — motivazione obbligatoria
4. Scrivi il "contratto" del dataset prepared: quali variabili dentro/fuori, quali imputate e come, quali scalate/trasformate → salvalo: `df.to_csv("../data/prepared/seller_prepared.csv", index=False)` (cartella `data/prepared/`)
5. Controllo finale: `df.isnull().sum().sum()` (zero NaN residui?), tipi coerenti, shape documentata

**Output report**: sezione "feature engineering" con la tabella delle nuove feature e il "contratto" del dataset finale.
**Decisioni aperte**: quali feature creare (qui più che altrove la creatività conta come Innovation).

## Fase 10 — Struttura del report (5-6 pagine per questo capitolo)

Ordine consigliato (specchio delle guidelines):

| Sottosezione | Contenuto | Pagine |
|---|---|---|
| 1.1 Data semantics | Tabella variabili + coerenze verificate | ~1 |
| 1.2 Distributions & statistics | Tabelle + figure univariate e vs target | ~2 |
| 1.3 Quality + transformations | Tabella qualità + missing/outlier + prima/dopo | ~1,5-2 |
| 1.4 Correlations + elimination | Heatmap + tabella decisioni | ~1-1,5 |

Regole di scrittura (dalle guidelines): **ogni figura commentata, ogni scelta motivata**, niente tabelle nude; salvare le figure da `report/` con `plt.savefig("../report/fig01_distribuzione_prezzo.png", dpi=150, bbox_inches="tight")`; scrivere in LaTeX su Overleaf (consigliato) o Word; font > 9pt.

---

# Il "primo giorno" in sintesi

1. Installa VS Code + GitHub Desktop + estensioni
2. Clona la repo, crea le cartelle, copia il CSV in `data/`
3. Crea `.venv`, installa le librerie, apri il primo notebook e carica il df
4. Commit + push del primo stato funzionante
5. Inizia la **Fase 1** (tabella semantica) — è tutta manuale/di ragionamento, il modo migliore per entrare nei dati

Quando l'ambiente funziona e hai la tabella semantica bozza, dimmelo: possiamo passare alla Fase 2 oppure costruire insieme lo scheletro di celle del notebook (senza risolvere le analisi).