# Fortress Vault 2.0 - Zero-Knowledge Password Manager

Benvenuti su "Fortress Vault", un password manager locale basato su crittografia forte (AES-GCM a 256 bit) sviluppato in Python con interfaccia grafica PyQt6.

---

- Chi Sono & Filosofia del Progetto
Sono un appassionato di informatica e sto studiando programmazione in modo teorico sui libri. Tuttavia, credo fermamente che l'esercizio pratico sul campo sia infinitamente più utile della sola teoria per comprendere davvero come si costruisce il software.

Per questo motivo, nel mio tempo libero, ho deciso di mettermi alla prova creando progetti reali. Per colmare il divario tra la teoria dei libri e la complessità pratica del codice, mi faccio affiancare dall'Intelligenza Artificiale, utilizzandola come un tutor interattivo e un "co-pilota" per lo sviluppo. 

Questo repository è il risultato di questo esperimento: unire lo studio tradizionale, l'approccio pratico "learning by doing" e la potenza dell'IA.

---

Lo Stato del Progetto (Work in Progress)
Il software è attualmente in una fase iniziale (Alpha). Il motore crittografico e la struttura di base sono solidi e funzionanti, ma c'è ancora moltissimo lavoro da fare, specialmente su due fronti:

1. UI/UX (Grafica): L'interfaccia grafica attuale è molto minimale e spartana. Vorrei renderla decisamente più moderna, fluida e accattivante.
2. Funzionalità Mancanti:Al momento l'applicazione permette di creare nuove categorie, ma mancano funzioni essenziali come l'eliminazione delle stesse, la modifica dei record esistenti e una gestione più dinamica del database.

---

Ho Bisogno della Tua Mano! 
Uno dei motivi principali per cui ho reso questo progetto pubblico è la possibilità di creare contatti, chiedere aiuto e imparare da altre persone più capaci di me.

Se hai suggerimenti, se vuoi criticare costruttivamente il codice, o se ti va di aiutarmi a migliorare la grafica o a implementare le funzioni mancanti:
Apri una Issue per discutere di nuove idee.
Fai una Pull Request se vuoi mettere direttamente mano al codice.
Lascia un commento o mettiti in contatto con me, grazie. 

Ogni aiuto, consiglio o review del codice è una preziosa opportunità di crescita per me.

---

Stack Tecnico Utilizzato
- Language: Python 3.13+
- GUI Framework:** PyQt6
- Cryptography: `cryptography` library (AES-256-GCM authenticated encryption)
- Storage: JSON criptato locale
