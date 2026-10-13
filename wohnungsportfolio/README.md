# Wohnungsportfolio – Lea Rager

Liebevoll gestaltete, halb-professionelle Wohnungsbewerbung (A4, 2 Seiten) zum Bearbeiten in InDesign.

| Datei | Wofür |
|---|---|
| `Wohnungsportfolio_Lea_Rager.idml` | **In InDesign öffnen** (Datei › Öffnen) und als `.indd` speichern |
| `Wohnungsportfolio_Lea_Rager_Vorschau.pdf` | Vorschau, wie das Layout aussieht |
| `Unterlagen_Deckblatt_Vorschau.pdf` | Nur Seite 2 als eigenes PDF (Deckblatt für die Unterlagen) |
| `Wohnungsportfolio_Lea_Rager_Apple.idml` | **Variante im Apple-Stil, warm** (siehe unten, mit Platzhaltern) |
| `Wohnungsportfolio_Lea_Rager_Apple_Vorschau.pdf` | Vorschau der Apple-Variante |
| `build_portfolio.py` | Generator (warmes Design) und gemeinsame Engine für IDML und PDF |
| `build_portfolio_apple.py` | Generator der Apple-Variante |

## Aufbau

1. **Seite 1 – Steckbrief:** rundes Foto, „Hallo, ich bin Lea Rager“, kurzer Text über mich,
   Karten „Auf einen Blick“ (Pädagogin · 2,5 Jahre im Beruf · Wien · Nichtraucherin · keine Haustiere · Einzug ab)
   und ein Kontaktfeld.
2. **Seite 2 – Meine Unterlagen:** Deckblatt mit Checkliste (Gehaltszettel, Arbeitsbestätigung,
   Ausweis, Meldezettel, KSV-Auskunft). Nicht benötigte Zeilen einfach löschen.

## In InDesign fertigstellen

1. **Foto:** den runden Rahmen auf Seite 1 anklicken › *Datei › Platzieren…* (Cmd/Strg + D).
   Das Bild füllt den Kreis automatisch aus.
2. **Platzhalter** in Rosé ersetzen: `[Datum]`, `[+43 …]`, `[E-Mail-Adresse]` (Seite 1 und Fußzeile Seite 2).
3. **Text „Ein paar Worte über mich“** ist ein Entwurf – einfach durch Leas eigenen Text ersetzen.
4. Schriften: **Georgia** und **Arial** (auf Mac und Windows vorinstalliert).
   Farben und Absatzformate (Name, Fließtext, Karten …) sind als Farbfelder bzw. Formate angelegt.

## Variante im Apple-Stil (warm)

Folgt Apples Designprinzipien (Klarheit, viel Weißraum, klare Hierarchie, Foto als Hauptdarsteller),
wirkt aber bewusst warm: cremefarbener Hintergrund, große abgerundete Ecken, Pastell-Kacheln
(„Bento“), Merkmale als Pillen, Kontaktfeld in Terrakotta.

- Schrift: **Inter** (kostenlos, sehr nah an Apples SF Pro). Vorher installieren:
  [rsms.me/inter](https://rsms.me/inter/) oder Google Fonts. Ohne Inter: in InDesign
  *Schrift › Schriftart suchen/ersetzen* › „Inter“ durch „Helvetica Neue“ ersetzen.
- Foto: den abgerundeten Rahmen links oben anklicken › *Datei › Platzieren…* – füllt sich automatisch.
- Platzhalter in Terrakotta: `[€ / Monat]`, `[Alter]`, `[folgt]` (und in der Repo-Version Telefon/E-Mail).

### Persönliche Daten

Das Repo ist öffentlich – Foto, Telefonnummer und E-Mail liegen deshalb nur lokal in `privat/`
(per `.gitignore` ausgeschlossen). `privat/daten.json` enthält z. B.:

```json
{ "telefon": "…", "email": "…", "foto": "Lea_Foto.jpg", "alter": "…", "netto": "…", "arbeitgeber": "…" }
```

`python3 build_portfolio_apple.py --fonts <ordner> --privat` erzeugt daraus IDML und fertiges PDF in `privat/`.

## Gehaltszettel anhängen

*Datei › Exportieren › Adobe PDF (Druck)*, dann in Acrobat (*Dateien kombinieren*) oder in der
macOS-Vorschau (PDF-Seiten in die Seitenleiste ziehen) die Gehaltszettel **hinter Seite 2** einfügen.
Alternativ Seite 1 alleine exportieren und die Unterlagen samt Deckblatt als zweites PDF mitschicken.

## Neu erzeugen

```bash
python3 build_portfolio.py                     # nur IDML
python3 build_portfolio.py --fonts <ordner>    # + PDF-Vorschau (braucht Gelasio-*.ttf, metrisch = Georgia)
python3 build_portfolio_apple.py --fonts <ordner>   # Apple-Variante (braucht Inter-400/500/600/700.ttf)
```
