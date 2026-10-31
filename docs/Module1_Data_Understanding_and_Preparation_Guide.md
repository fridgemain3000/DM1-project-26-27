# Modulo 1 — Teoria essenziale per Data Understanding & Preparation

Guida teorica **riassunta**, allineata alla scaletta [`Scaletta_Parte1_DU_DP.md`](Scaletta_Parte1_DU_DP.md) e al notebook `notebooks/01c_DU_DP_semplificato.ipynb` (versione semplificata di `01b_DU_DP_completo.ipynb`).

Ogni sezione ha:
- **Teoria**: definizioni e formule del corso (dispense DM1.01 e DM1.02, slide e libro di Tan);
- **Nel nostro dataset**: come la teoria si applica ai dati veri, con i numeri ottenuti nel notebook;
- **Da sapere all'orale**: le domande tipiche con la risposta breve.

I termini inglesi sono tra parentesi, utili se il report è scritto in inglese.

| Sezione | Scaletta | Notebook | Dispense |
|---|---|---|---|
| 1. Il dataset | §1 | §1 | — |
| 2. Data semantics | §2 | §2 | DM1.01 §2–3 |
| 3. Distribuzioni e statistiche | §3 | §4 | DM1.01 §5–12 |
| 4. Qualità dei dati | §4 | §3, §5 | DM1.01 §4 |
| 5. Valori mancanti | §5 | §6 | DM1.01 §14, DM1.02 §8 |
| 6. Outlier, trasformazioni, nuove feature | §6 | §7 | DM1.01 §13, DM1.02 §7, §9–12 |
| 7. Correlazioni ed eliminazione di variabili | §7 | §8 | DM1.01 §12, DM1.02 §4–6 |
| 8. Dalla preparazione ai moduli successivi | §8 | §9 | DM1.02 §1 |
| 9. Formulario · 10. Glossario IT–EN | — | — | — |

> **Il principio che guida tutta la parte 1.** Il *data understanding* **diagnostica** (mancanti, outlier, tipi, dipendenze), la *data preparation* **cura** (seleziona, riduce, imputa, trasforma). Nel report ogni passo segue lo schema *osservo → interpreto → decido → giustifico*: il prof valuta il **metodo**, non i numeri.

---

## 1. Il dataset in breve

- **Tipo di dataset**: *record data* in forma tabellare, 13.843 oggetti × 33 attributi.
- **Oggetto** (riga) = **un venditore**, non un'auto. I valori sono **già aggregati** sugli annunci del venditore:
  - `*_median` → statistiche di **secondo livello**: descrivono l'auto *tipica* dell'inventario;
  - `pct_*` → **proporzioni** in [0, 1];
  - `dominant_*` → **mode** dell'inventario (perdono la varietà: 51% SUV e 49% sedan diventa "suv").
- **Conseguenza da dire nel report**: l'aggregazione riduce il rumore dei singoli annunci, ma nasconde la variabilità interna (un venditore con metà auto da 5.000 $ e metà da 50.000 $ ha la stessa mediana di uno con tutte auto da 27.000 $).
- **Contesto temporale**: `year_median + vehicle_age_median ≈ 2020` → annunci raccolti intorno al 2020 (dataset USA: miglia, pollici, galloni, MPG).

---

## 2. Data semantics

### Teoria

**Oggetti e attributi.** Un *oggetto* (record, istanza) è descritto da *attributi* (feature, variabili). Il **tipo semantico** di un attributo decide quali operazioni e statistiche hanno senso. **Non coincide con il tipo informatico** di `df.dtypes`: un ID numerico è nominale, un `int` può essere ordinale.

**Tipi di attributo (Stevens).** Ogni tipo ha tutte le proprietà dei tipi alla sua sinistra.

| | **Nominale** | **Ordinale** | **Intervallo** (*interval*) | **Rapporto** (*ratio*) |
|---|---|---|---|---|
| Proprietà | distinzione (=, ≠) | + ordine (<, >) | + differenze (+, −) | + rapporti (×, /) |
| Statistiche | moda, frequenze, χ² | + mediana, percentili, Spearman | + media, dev. std, Pearson | + media geometrica, variazione % |
| Trasformazioni che non cambiano il significato | rinominazione 1-a-1 | funzione monotona crescente | $a\cdot x+b$ | $a\cdot x$ |
| Zero | — | — | **arbitrario** | **assoluto** (assenza della quantità) |
| Esempio | colore, ID | taglie S < M < L | data, °C | età, prezzo, conteggi |

- **Discreto** (insieme finito o numerabile: conteggi, codici) vs **continuo** (valori reali). È una classificazione indipendente dalla precedente: i conteggi sono discreti **e** ratio.
- **Binario**: *simmetrico* (i due valori contano uguale) o *asimmetrico* (conta la presenza, l'1; es. "ha auto incidentate").

### Nel nostro dataset

| Famiglia | Attributi | Tipo |
|---|---|---|
| Identificativo | `sp_id` | nominale (escluso dalle analisi) |
| Attività | `n_listings`, `n_listing_days`, `listing_span_days` | ratio, discreti |
| Prezzo e mercato | `price_median`, `savings_amount_median`, `daysonmarket_median` | ratio, continui |
| Età e uso | `year_median` → **intervallo**; `vehicle_age_median`, `mileage_median`, `owner_count_median` → ratio | |
| Motore, consumi, dimensioni | `horsepower`, `engine_displacement`, `*_fuel_economy`, legroom, serbatoio, altezza, lunghezza, larghezza | ratio, continui |
| Composizione inventario | `pct_isCab`, `pct_is_new`, `pct_salvage`, `pct_theft_title` | ratio, ∈ [0, 1] |
| Mode dell'inventario | `dominant_body_type`, `_fuel_type`, `_transmission`, `_wheel_system`, `_listing_color` | nominali |
| Profilo venditore | `franchise_status`, `new_used_profile` | nominali |
| **Target** | `seller_rating_class` | **ordinale** (low < medium < high) |

Punti da evidenziare:
- `year_median` è **intervallo** (dire "2010 è il doppio di 1005" non ha senso), `vehicle_age_median` è **ratio** (un'auto di 10 anni ha il doppio dell'età di una di 5).
- Il target è **ordinale**: ha senso la mediana e la correlazione di Spearman, non la media delle classi.
- **Discrepanze tra documentazione e dati**: `franchise_status` dichiara 4 valori ma ne ha 2; `new_used_profile` non ha mai "unknown".
- `new_used_profile` è una **discretizzazione deterministica** di `pct_is_new` (0 → used_only, 1 → new_only, altrimenti mixed): è ridondante.

### Da sapere all'orale
- *Perché l'anno è intervallo e l'età ratio?* L'anno 0 è una convenzione; un'età 0 è l'assenza di età.
- *Che statistica di centro uso per il target?* Moda o mediana (ordinale), mai la media dei codici.
- *Il tipo informatico basta?* No: `sp_id` è un `float64` ma è nominale.

---

## 3. Distribuzioni e statistiche

### Teoria

**Tendenza centrale.**
- **Media** $\bar x=\frac1m\sum_i x_i$: distributiva (si calcola a pezzi), ma **molto sensibile agli outlier**.
- **Mediana**: il valore centrale dei dati ordinati; **robusta**; vale anche per gli ordinali.
- **Moda**: il valore più frequente; l'unica valida per i nominali. Per i continui va letta sui bin dell'istogramma.
- **Media troncata** (*trimmed mean*): media dopo aver tolto una percentuale di valori estremi per lato.

**Forme delle distribuzioni.**

| Forma | Ordine delle misure | Esempio |
|---|---|---|
| Simmetrica (normale) | media = mediana = moda | altezza |
| Asimmetria **positiva** (coda a destra) | moda < mediana < **media** | redditi, prezzi, conteggi |
| Asimmetria **negativa** (coda a sinistra) | **media** < mediana < moda | — |
| **Bimodale** | due picchi = spesso **due popolazioni mescolate** | peso di uomini e donne |

L'indice di asimmetria (*skewness*) vale 0 per una distribuzione simmetrica; come regola pratica, sopra 1 in valore assoluto l'asimmetria è forte.

**Dispersione.**
- **Range** $=\max-\min$: dipende da due soli valori.
- **Varianza** $s^2=\frac{1}{m-1}\sum_i(x_i-\bar x)^2$ e **deviazione standard** $s=\sqrt{s^2}$ (stessa unità dei dati; si usa solo con la media come centro). Si divide per $m-1$ perché è una stima da un campione. In Python: `pandas.std()` usa $m-1$, `numpy.std()` di default usa $m$.
- **Misure robuste**: $\mathrm{IQR}=Q_3-Q_1$ (ampiezza del 50% centrale), AAD (media degli scarti assoluti), MAD (mediana degli scarti assoluti).

**Quantili e box plot.**
- Il $p$-esimo **percentile** lascia sotto di sé il $p\%$ dei dati. Q1 = 25°, Q2 = mediana, Q3 = 75°. *Five-number summary*: min, Q1, mediana, Q3, max.
- **Box plot**: la scatola va da Q1 a Q3, la linea interna è la mediana. I baffi arrivano all'ultimo dato entro i **recinti di Tukey** $[Q_1-1.5\,\mathrm{IQR},\ Q_3+1.5\,\mathrm{IQR}]$ (default di pandas, matplotlib e seaborn); i punti fuori sono candidati outlier. Con $3\cdot\mathrm{IQR}$ si individuano gli outlier "estremi".
- Gli **istogrammi dicono più dei box plot**: un box plot non mostra la bimodalità.

**Istogrammi e numero di bin.**
- Troppi pochi bin nascondono la forma (la bimodalità sparisce); troppi la trasformano in rumore.
- **Sturges**: $k=\lceil\log_2 n+1\rceil$. Per noi $\log_2 13.843=13{,}76$ → $k=\lceil14{,}76\rceil=\mathbf{15}$. È pensata per dati circa normali: con code lunghe conviene provare altri valori o trasformare prima.
- **Scott**: ampiezza del bin $h=\dfrac{3.5\,s}{\sqrt[3]{n}}$; per noi $\sqrt[3]{13.843}\approx24$.
- **Binning** (= discretizzazione):
  - *natural* (*equal width*): $\delta=\frac{x_{\max}-x_{\min}}{k}$; semplice ma molto sensibile agli outlier;
  - *equal frequency*: $\frac{N}{k}$ elementi per bin; istogramma piatto, quindi non mostra la forma.

**Due o più variabili.**
- **Scatter plot** e **scatter matrix** (pairplot): relazioni a coppie, outlier bivariati, gruppi.
- **Box plot / KDE condizionati** a una classe: confrontano la distribuzione $f(X\mid Y=c)$ tra le classi. Con classi sbilanciate le KDE vanno normalizzate per classe (`common_norm=False`).
- **Tabella di contingenza** tra due categoriche; normalizzata per riga dà le probabilità condizionate $P(Y=c\mid A=a)=\frac{O_{ac}}{\sum_c O_{ac}}$.
- **Coordinate parallele**: un asse verticale per attributo, una spezzata per oggetto. Servono attributi standardizzati e pochi oggetti, altrimenti il grafico è illeggibile.

### Nel nostro dataset
- **Asimmetria positiva forte**: `n_listings` (skew ≈ 5,3; mediana 70, max 4.959), `daysonmarket_median` (≈ 8,8), `price_median` (≈ 3,4), `savings_amount_median`, `listing_span_days`. → Candidati al logaritmo (§6).
- **Asimmetria negativa**: `year_median`, per 32 concessionari di auto d'epoca.
- **Molta massa in 0**: `pct_salvage` (~91% zeri), `pct_theft_title` (~85%), `savings_amount_median` (~37%), `pct_is_new` (~53%).
- **Bimodalità**: `mileage_median` e `vehicle_age_median` separano i venditori di usato da quelli misti.
- **Categoriche quasi costanti**: gasoline ~99%, cambio automatico ~94%.
- **Target sbilanciato**: medium 55%, high 27%, low 19%.
- **Relazioni con il target deboli**: la |ρ| di Spearman più alta è ≈ 0,26 (`n_listings`, negativa). Gli indipendenti hanno più rating *high* (33% contro 21%).

### Da sapere all'orale
- *Media o mediana per i prezzi?* Mediana: la distribuzione è asimmetrica e la media è tirata dalla coda.
- *Perché un box plot non basta?* Non mostra la bimodalità né la forma della distribuzione.
- *Come scelgo i bin?* Sturges come punto di partenza, poi verifico a occhio che la forma non cambi.

---

## 4. Qualità dei dati

### Teoria

**Dimensioni della qualità** (slide 19):

| Dimensione | Significato | Come si scopre |
|---|---|---|
| **Accuratezza sintattica** | il valore **non appartiene al dominio** (testo in un campo numerico, "fmale") | facile: controllo dei valori ammessi |
| **Accuratezza semantica** | il valore è nel dominio **ma è sbagliato** | difficile: servono regole di dominio o fonti esterne |
| **Completezza** | mancano dati che dovrebbero esserci (valori o interi gruppi di record) | confronto con ciò che ci si aspetta |
| **Sbilanciamento** (*unbalanced*) | dataset dominato da un tipo di record | frequenze delle classi |
| **Attualità** (*timeliness*) | i dati sono aggiornati? | data di raccolta |

Nota: nella slide 19 la definizione di completezza è copiata per errore da quella di accuratezza semantica. La completezza riguarda i dati **assenti**.

Altri concetti utili:
- **Duplicati**: record uguali o quasi uguali, tipici quando si uniscono fonti diverse (*deduplication*).
- **Valori incoerenti** (*inconsistent*): plausibili da soli, impossibili **insieme** agli altri valori dello stesso oggetto (es. età 6 anni e laurea). Si scoprono con regole che confrontano **più attributi**.
- **Rumore vs artefatto** (Tan):
  - *rumore*: errore **casuale**, diverso a ogni misura; fare la media lo riduce;
  - *artefatto*: errore **sistematico**, sempre uguale; fare la media non serve, ma una volta scoperto si può riconoscere e correggere.
- **Precisione, bias, accuratezza**: la precisione è quanto le misure sono vicine tra loro (dev. std); il bias è lo scostamento sistematico della media dal valore vero; l'accuratezza è la vicinanza al valore vero, e richiede entrambe.

### Nel nostro dataset
- **Accuratezza sintattica**: circa 1.580 celle in 7 colonne sono stringhe come `38.650.000.000.000.000` (= 38,65 con il punto letto come separatore delle migliaia). È un **artefatto**: un errore sistematico di esportazione. Proprio perché è sistematico si può **ricostruire**: si prova ogni posizione del punto decimale e si tiene l'unico candidato nel range plausibile della colonna. Recuperato il 99,7%; i casi ambigui diventano NaN.
- **Accuratezza semantica**: legroom 0 o 67 pollici, km nulli in inventari di usato, 72 MPG su "gasoline". Errori o casi dubbi diventano NaN. I valori **veri** si tengono: elettriche in MPGe (~120), van alti, auto d'epoca.
- **Coerenza tra attributi**: `listing_span_days ≥ n_listing_days − 1`, `n_listing_days ≤ n_listings`, profilo ↔ `pct_is_new`: tutti verificati. Attenzione: la condizione `n_listing_days ≤ listing_span_days` sarebbe **sbagliata**, perché un venditore attivo un solo giorno ha 1 giorno distinto e span 0.
- **Completezza**: `dominant_wheel_system` 76% NaN, `engine_displacement_median` 24,5%, colore "unknown" 11% (§5).
- **Sbilanciamento**: target 55/27/19%; gasoline ~99%.
- **Attualità**: annunci intorno al 2020.
- **Unicità**: 0 duplicati.

### Da sapere all'orale
- *Differenza tra errore sintattico e semantico?* Il primo si vede guardando un valore da solo (non è nel dominio); il secondo no.
- *Come si scopre un'incoerenza?* Con regole su più attributi dello stesso record.
- *Perché i numeri corrotti si possono riparare?* Perché l'errore è sistematico (un artefatto): la regola che lo ha prodotto si può invertire.

---

## 5. Valori mancanti

### Teoria

**Perché mancano** (slide 63): informazione **non raccolta**, attributo **non applicabile** (il reddito di un bambino), **guasto** di un sensore, **rifiuto** di rispondere.

**Tre tipi di valori anomali** (slide 28):
- **missing**: il valore non c'è (NaN, cella vuota);
- **unknown**: c'è un valore ma senza significato reale (−1, 9999, "unknown"); è un **mancante mascherato**;
- **not valid**: il valore c'è ma non è ammissibile (età 250 anni).

**Cosa fare** (Lezione 3 e slide 29):
1. **Eliminare la colonna** se ha moltissimi mancanti (es. ~80%): mancare è una caratteristica della variabile, che porta poca informazione.
2. **Eliminare la riga** se ha quasi tutti i valori mancanti.
3. Altrimenti **imputare**, cioè sostituire con valori plausibili **senza alterare la distribuzione**. Dalla strategia più semplice alla più raffinata:
   - media / mediana / moda globale;
   - **estrazione casuale** dalla distribuzione osservata;
   - media / mediana / moda **per segmento** (gruppi simili);
   - distribuzione dentro il segmento;
   - **modello** (regressione o classificazione) dalle altre variabili: "si usa già il data mining nella preparazione".

**Perché la media globale è la scelta peggiore**: mette tanti valori identici al centro, creando un **picco artificiale**, e **riduce la deviazione standard** (nel Titanic, `Age`: da 14,53 a 13,00). Inoltre ignora le relazioni con le altre variabili.

**Il mancante è informativo?** Prima di imputare si confrontano le righe con e senza mancante: mediane delle altre variabili e distribuzione del target.
- Nessuna differenza → mancante casuale: si può imputare o eliminare.
- Differenze nette → conviene tenerne traccia con un indicatore 0/1 o una categoria "unknown".
- Con molte righe anche differenze minime risultano "significative" nel test χ²: conta la dimensione dell'effetto (es. V di Cramér, §7), non solo il p-value.

> Fuori dalle slide, ma utile come lessico: nella letteratura si distingue tra mancanti *MCAR* (completamente casuali), *MAR* (dipendono da altre variabili osservate) e *MNAR* (dipendono dal valore mancante stesso).

**Data leakage.** Il target non si usa **mai** per imputare. In classificazione, imputazioni e scaling vanno stimati sul **solo training set** e poi applicati al test.

### Nel nostro dataset
- `dominant_wheel_system` (76% NaN) → **eliminata**.
- `engine_displacement_median` (24,5%):
  - il mancante **non è informativo**: V di Cramér con il target ≈ 0,01 e mediane uguali tra i due gruppi;
  - confronto di 4 strategie nascondendo il 20% dei valori noti:

    | Strategia | Errore medio (MAE) |
    |---|---|
    | mediana globale | ≈ 620 cc |
    | mediana per tipo di carrozzeria | ≈ 520 cc |
    | estrazione casuale | ≈ 840 cc |
    | **regressione** su potenza e serbatoio | **≈ 330 cc** |

  - scelta: la **regressione**, che è anche quella che conserva meglio la deviazione standard.
- **27 venditori con NaN in blocco** (`pct_isCab`, `pct_salvage`, `pct_theft_title`, `owner_count`): 26 sono venditori di solo nuovo. Sono mancanti **"non applicabili"**: un'auto nuova non ha proprietari precedenti e non è un ex taxi. → **posti a 0**, righe tenute (eliminarle avrebbe tolto l'84% della categoria `new_only`).
- NaN sparsi sotto l'1% → **mediana per tipo di carrozzeria** (le dimensioni dipendono dalla carrozzeria).
- Colore "unknown" (11%) → resta una **categoria**, perché non c'è modo sensato di ricostruirlo.

### Da sapere all'orale
- *Quando elimino una colonna invece di imputarla?* Quando i mancanti sono così tanti che imputare vorrebbe dire inventare la variabile.
- *Perché non la media globale?* Picco artificiale e varianza ridotta.
- *Come verifico che l'imputazione non distorce?* Istogramma prima/dopo, media e deviazione standard prima/dopo, errore su valori noti nascosti.

---

## 6. Outlier, trasformazioni, nuove feature

### Teoria

**Outlier.** Oggetti con caratteristiche **considerevolmente diverse** dalla maggior parte degli altri.
- **Il dilemma** (Lezione 2): se è un **errore** (sensore guasto, battitura) va eliminato o reso NaN; se è un **valore vero** (redditi altissimi, mega-venditori) va **tenuto**, eventualmente riducendone l'effetto. Sono azioni opposte.
- **Rumore ≠ outlier**: il rumore è un errore casuale e non è mai interessante; un outlier può essere un dato legittimo e interessante (*anomaly detection*).
- **Rilevazione**:
  - univariata: recinti di Tukey (1,5·IQR, 3·IQR) per le numeriche; per le categoriche, valori con frequenza bassissima;
  - multivariata: scatter plot, PCA, clustering (punti che non appartengono a nessun cluster).
- **Limite della regola IQR**: se più del 75% dei valori è uguale (es. 0), allora IQR = 0 e **ogni valore diverso** risulta outlier. La regola non ha senso: meglio binarizzare.

**Trasformazioni.** Una funzione che manda ogni valore di un attributo in un nuovo valore. È buona se (slide 39):
1. **conserva l'informazione** rilevante;
2. **elimina almeno un problema** dell'attributo;
3. è **più utile** dell'originale.

Gli obiettivi principali sono stabilizzare la varianza, rendere le distribuzioni più simili alla normale e rendere lineari le relazioni.

**Famiglia di potenze** (slide 43): $T_p(x)=a\,x^p+b$, con il logaritmo al posto di $p=0$. Conservano l'ordine dei valori.

| Trasformazione | Quando |
|---|---|
| lineare $ax+b$ | cambio di unità; non cambia la forma |
| **logaritmo** ($\log(1+x)$ se ci sono zeri) | asimmetria positiva forte, valori su più ordini di grandezza (prezzi, conteggi) |
| radice quadrata | conteggi; correzione più "morbida" del log |
| reciproco $1/x$ | quando la varianza cresce troppo con la media |

**Perché il logaritmo funziona**: misura l'**ordine di grandezza**, quindi valori enormemente diversi diventano vicini; non perde informazione (si torna indietro con l'esponenziale).

**Normalizzazione.** Serve perché gli algoritmi basati su **distanze** (K-means, DBSCAN, gerarchico, KNN) sono dominati dagli attributi con valori grandi.
- **Min-max**: $v'=\frac{v-\min}{\max-\min}\in[0,1]$. Range fisso, ma **molto sensibile agli outlier**.
- **Z-score**: $v'=\frac{v-\bar x}{s}$, con media 0 e dev. std 1. È il default per PCA e clustering.
- Esiste una variante robusta: mediana al posto della media, deviazione assoluta al posto della dev. std.
- **Ordine giusto**: prima il log, poi lo z-score.

**Discretizzazione e binarizzazione** (servono soprattutto per il pattern mining, Modulo 4):
- discretizzare = numerico → **ordinale** (natural, equal frequency, statistical binning);
- binarizzare = una colonna 0/1 per valore (**one-hot**).
- Codificare categorie nominali con interi (0, 1, 2) **inventa un ordine e delle distanze**: per algoritmi che fanno calcoli serve il one-hot.

**Feature creation** (slide 23):
- *construction*: nuove variabili da conoscenza del dominio (densità = massa/volume, BMI);
- *extraction*: da dati grezzi non strutturati (pixel → "ci sono gli occhi");
- *projection*: in uno spazio con meno dimensioni (PCA).

Una buona feature cattura l'informazione **in modo più efficiente** e spesso **sostituisce** due variabili correlate.

### Nel nostro dataset
- **Outlier veri, tenuti**: mega-venditori (fino a 4.959 annunci), auto d'epoca, elettriche, van alti. Da ricordare per il Modulo 2: K-means è sensibile agli outlier, DBSCAN li può etichettare come rumore.
- **log1p** su `n_listings`, `listing_span_days`, `daysonmarket_median`, `price_median`, `savings_amount_median`:
  - `n_listings`: skew da 5,25 a −0,13, outlier IQR da 4,6% a 0,01%;
  - limite: per `listing_span_days` il log corregge troppo (skew −1,22); la radice quadrata dà 0,53.
- **Binarizzazione**: `has_salvage`, `has_theft_title`.
- **Categorie rare raggruppate**: carrozzeria → `coupe_convertible`, `other`; colori rari → `other`.
- **Nuove feature**:
  - `listings_per_day = n_listings / n_listing_days` (intensità dell'attività);
  - `combined_fuel_economy = 0,55·city + 0,45·highway` (pesi EPA; sostituisce due variabili con ρ = 0,94);
  - `discount_ratio = savings / price` (sconto relativo).

### Da sapere all'orale
- *Un outlier va sempre eliminato?* No: solo se è un errore. Se è vero, lo tengo e ne riduco l'effetto (log, binning).
- *Perché il log e non lo z-score per la coda lunga?* Lo z-score è lineare: non cambia la forma della distribuzione, sposta e riscala soltanto.
- *Min-max o z-score?* Con outlier lo z-score è meno schiacciato; il prof li considera intercambiabili, ma la scelta va motivata.

---

## 7. Correlazioni ed eliminazione di variabili

### Teoria

**Pearson** (relazione **lineare**):
$$r_{xy}=\frac{\sum_i(x_i-\bar x)(y_i-\bar y)}{\sqrt{\sum_i(x_i-\bar x)^2}\,\sqrt{\sum_i(y_i-\bar y)^2}}\in[-1,1]$$
Il numeratore è (a meno di $n-1$) la **covarianza**; il denominatore la normalizza. $|r|=1$ significa punti esattamente su una retta.

**Tre trabocchetti**:
1. Pearson misura solo relazioni **lineari**: con $y=x^2$ su valori simmetrici si ottiene $r=0$ anche se la relazione è perfetta.
2. **Correlazione non è causalità** (spesso c'è una terza variabile).
3. Pearson richiede attributi **numerici**.

**Spearman** = Pearson calcolato sui **ranghi**:
$$\rho=1-\frac{6\sum_i d_i^2}{n(n^2-1)}$$
(senza pareggi; $d_i$ = differenza tra i ranghi). Misura relazioni **monotone**, è **robusta agli outlier** e va bene per gli ordinali. Se Spearman è molto più alto di Pearson, la relazione è monotona ma non lineare, oppure Pearson è disturbato dalla coda.

**Due categoriche**: tabella di contingenza e test χ². Come misura di intensità si può usare la **V di Cramér** (extra rispetto alle slide):
$$V=\sqrt{\frac{\chi^2/n}{\min(r-1,\ k-1)}}\in[0,1]$$
dove $r$ e $k$ sono il numero di righe e colonne della tabella. Nel notebook si usa proprio questa formula (funzione `cramers_v`, §6.2). Poiché è uno strumento non visto a lezione, nel report va presentato con la formula (le guideline suggeriscono di avvisare il docente per i metodi nuovi).

**Riduzione della dimensionalità.**
- **Curse of dimensionality**: con molte dimensioni i punti diventano quasi equidistanti, e densità e distanze perdono significato. Per questo si vuole essere "parsimoniosi" con le variabili.
- Attributi **irrilevanti** (nessuna informazione per il compito) vs **ridondanti** (duplicano informazione di altri).
- **Feature subset selection**:
  - *filter*: prima e indipendentemente dall'algoritmo (es. correlazione); è quello richiesto nella parte 1;
  - *wrapper*: prova sottoinsiemi usando l'algoritmo (forward selection, backward elimination);
  - *embedded*: la selezione avviene dentro l'algoritmo (albero di decisione).
- **PCA**: nuove dimensioni ortogonali, la prima con la massima varianza. Passi:
  1. standardizzare;
  2. matrice di covarianza (= di correlazione);
  3. autovalori e autovettori;
  4. ordinare e tenere i primi $k$;
  5. proiettare.

  Si tengono componenti finché la varianza spiegata cumulata è alta (90–95%) o fino al "gomito". Con due variabili standardizzate e correlazione $r$, la PC1 spiega $\frac{1+r}{2}$ della varianza. Costo: le componenti sono **meno interpretabili**.

**Tre strade per una coppia o un gruppo ridondante**: **eliminare** una variabile, **combinarle** in una nuova feature, oppure **PCA** sul gruppo.

### Nel nostro dataset
- **Regola dichiarata**:
  - |ρ| ≥ 0,9 → si tiene una variabile o si fondono;
  - 0,7–0,9 → si decide caso per caso;
  - variabili quasi costanti o derivate → si escludono.
- **Coppie ridondanti**:
  - `year`–`vehicle_age`: ρ = −0,98, ridondanti per costruzione → si tiene l'età;
  - `n_listings`–`n_listing_days`: ρ = 0,96 → si tiene `n_listings` più `listings_per_day`;
  - `city`–`highway`: ρ = 0,94 → fuse in `combined_fuel_economy`;
  - `savings`–`discount_ratio`: ρ = 0,91 → nel clustering solo `discount_ratio`.
- **Pearson ≪ Spearman**: `price`–`year` 0,55 contro 0,82 → relazione monotona non lineare, un altro motivo per il log.
- **Blocchi di variabili correlate**: età/uso/nuovo; dimensione del veicolo; attività del venditore.
- **PCA sul blocco dimensioni/motore**: PC1 spiega il **71%** della varianza ("taglia del veicolo").
- **Categoriche**: `franchise_status`–`new_used_profile` V ≈ 0,90 (quasi la stessa informazione). Con il target la V più alta è ≈ 0,14: associazione debole.

### Da sapere all'orale
- *Perché togliere variabili correlate se l'informazione è la stessa?* Raddoppiano il peso di quell'aspetto nelle distanze, aumentano la dimensionalità e rendono i modelli meno interpretabili.
- *Filter, wrapper o embedded: quale hai usato?* Filter, con la matrice di correlazione e una regola dichiarata in anticipo.
- *Quando preferisci la PCA all'eliminazione?* Quando un intero gruppo è correlato e l'interpretabilità conta meno (clustering più che alberi).

---

## 8. Dalla preparazione ai moduli successivi

Ogni algoritmo ha esigenze diverse: per questo si salvano versioni diverse dello **stesso** dataset (stesse righe, stesso `sp_id`).

| Modulo | Versione dei dati | Perché |
|---|---|---|
| **Clustering** (K-means, DBSCAN, gerarchico) | numeriche non ridondanti, **log + z-score**, **senza target** | le distanze richiedono la stessa scala; il target serve solo dopo, per interpretare i cluster |
| **Classificazione** (alberi, KNN, Naive Bayes) | dataset pulito **non scalato**, con target; one-hot per i nominali | gli alberi non richiedono scaling; KNN sì, ma **dentro** il training (niente leakage); split **stratificato** per lo sbilanciamento |
| **Regressione** | dataset pulito | scegliere un target numerico e controllare la linearità |
| **Pattern mining** | numeriche **discretizzate** (equal frequency) e **binarizzate** | le regole di associazione accettano solo attributi categorici/binari |

Nel notebook: `data/processed/seller_clean.csv` (13.843 × 30, con target) e `seller_clustering_base.csv` (13.843 × 19, z-score, senza target).

---

## 9. Formulario

| Concetto | Formula |
|---|---|
| Media | $\bar x=\frac1m\sum_i x_i$ |
| Varianza campionaria | $s^2=\frac{1}{m-1}\sum_i(x_i-\bar x)^2$ |
| Deviazione standard | $s=\sqrt{s^2}$ |
| Scarto interquartile | $\mathrm{IQR}=Q_3-Q_1$ |
| Recinti di Tukey | $[Q_1-1.5\,\mathrm{IQR},\ Q_3+1.5\,\mathrm{IQR}]$ (estremi: $3\,\mathrm{IQR}$) |
| AAD / MAD | $\frac1m\sum_i\lvert x_i-\bar x\rvert$ / $\operatorname{median}_i\lvert x_i-\bar x\rvert$ |
| Sturges | $k=\lceil\log_2 n+1\rceil$ (per noi 15) |
| Scott | $h=3.5\,s/\sqrt[3]{n}$ |
| Natural binning | $\delta=(x_{\max}-x_{\min})/k$ |
| Equal frequency | $N/k$ elementi per bin |
| Pearson | $r=\dfrac{\sum(x_i-\bar x)(y_i-\bar y)}{\sqrt{\sum(x_i-\bar x)^2}\sqrt{\sum(y_i-\bar y)^2}}$ |
| Spearman | $\rho=1-\dfrac{6\sum d_i^2}{n(n^2-1)}$ |
| V di Cramér | $V=\sqrt{\dfrac{\chi^2/n}{\min(r-1,k-1)}}$ |
| Min-max | $v'=\dfrac{v-\min}{\max-\min}$ |
| Z-score | $v'=\dfrac{v-\bar x}{s}$ |
| Log con zeri | $\log(1+x)$ |
| PCA, 2 variabili standardizzate | varianza spiegata da PC1 $=\frac{1+r}{2}$ |

---

## 10. Glossario italiano–inglese

| Italiano | Inglese |
|---|---|
| attributo, variabile | attribute, feature, variable |
| nominale / ordinale / a intervallo / a rapporto | nominal / ordinal / interval-scaled / ratio-scaled |
| tendenza centrale, dispersione | central tendency, dispersion |
| asimmetria, curtosi | skewness, kurtosis |
| scarto interquartile | interquartile range (IQR) |
| recinti, baffi | fences, whiskers |
| tabella di contingenza | contingency table, cross-tabulation |
| accuratezza sintattica / semantica | syntactic / semantic accuracy |
| completezza, attualità | completeness, timeliness |
| valore mancante (mascherato) | missing value (disguised) |
| imputazione | imputation |
| valore anomalo, rumore, artefatto | outlier, noise, artifact |
| trasformazione logaritmica | log transformation |
| normalizzazione, standardizzazione | min-max normalization, z-score standardization |
| discretizzazione, binarizzazione | discretization (binning), binarization (one-hot encoding) |
| creazione di attributi | feature creation / construction |
| selezione di attributi | feature (subset) selection — filter / wrapper / embedded |
| maledizione della dimensionalità | curse of dimensionality |
| componenti principali | principal components (PCA) |
| fuga di informazione | data leakage |
