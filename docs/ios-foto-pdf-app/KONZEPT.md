# Konzept: iOS-App „Foto → A4-PDF“

Arbeitstitel: **FotoPDF**

## 1. Kurzfassung & Machbarkeit

**Ja, die App ist vollständig machbar** – und zwar ausschließlich mit Apple-eigenen
Frameworks, ohne Drittanbieter-Bibliotheken, ohne Server und komplett offline.

| Anforderung | Umsetzung mit Apple-Bordmitteln | Machbarkeit |
|---|---|---|
| Fotos aus der Galerie auswählen (auch mehrere) | `PhotosPicker` (PhotosUI) | ✅ einfach |
| Ein Foto als A4-PDF-Seite, mit/ohne Rand | `UIGraphicsPDFRenderer` (UIKit) | ✅ einfach |
| Mehrere Fotos in ein gemeinsames PDF | `UIGraphicsPDFRenderer`, mehrere Seiten | ✅ einfach |
| Mehrere Fotos pro Seite im Raster (Standard 2×2) | eigene Layout-Berechnung (wenige Zeilen Code) | ✅ einfach |
| Raster frei wählbar | Einstellungen für Spalten × Zeilen | ✅ einfach |
| Vorschau vor dem Export | `PDFKit` (`PDFView`) | ✅ einfach |
| PDF speichern / teilen / drucken | `ShareLink` / Teilen-Menü (Dateien, Mail, AirDrop, Drucken) | ✅ einfach |

Der einzige Bereich, der etwas Sorgfalt braucht, ist der **Speicherverbrauch bei vielen
Fotos** (z. B. 100+ Bilder in hoher Auflösung). Dafür gibt es bewährte Lösungen (siehe
Abschnitt 7).

**Wichtige Erkenntnis für das Design:** „Ein Foto pro A4-Seite“ ist technisch einfach
ein Raster von **1×1**. Beide Wünsche (Einzelfoto als A4 und mehrere Fotos pro Seite)
lassen sich deshalb mit *einer* gemeinsamen Layout-Engine abdecken. Das hält die App
schlank und die Bedienung einheitlich.

## 2. Funktionsumfang

### 2.1 Fotoauswahl
- Mehrfachauswahl aus der Galerie über den System-Picker.
- Auswahl-Reihenfolge bleibt erhalten (das zuerst angetippte Foto kommt zuerst).
- **Keine Fotomediathek-Berechtigung nötig:** Der System-Picker läuft außerhalb der App,
  die App sieht nur die ausgewählten Fotos. Das ist datenschutzfreundlich und erspart
  den Berechtigungsdialog.
- Nach der Auswahl: Fotos per Drag & Drop umsortieren, einzelne entfernen, weitere
  hinzufügen.

### 2.2 Layout-Einstellungen

| Einstellung | Optionen | Standard |
|---|---|---|
| **Raster** | Vorlagen: 1×1, 1×2, 2×2, 2×3, 3×3, 3×4 + „Eigenes“ (Spalten 1–6 × Zeilen 1–8) | **2×2** |
| Seitenformat | A4 (später optional A5, A3, US Letter) | A4 |
| Ausrichtung | Hochformat / Querformat | Hochformat |
| **Seitenrand** | Kein Rand (0 mm), Schmal (5 mm), Normal (10 mm), Breit (20 mm), Eigener Wert | Normal (10 mm) |
| Abstand zwischen Fotos | 0–20 mm | 5 mm |
| Bildanpassung | **Einpassen** (ganzes Foto sichtbar, ggf. Leerraum) / **Füllen** (Zelle voll, Foto wird beschnitten) | Einpassen |
| Fotos automatisch drehen | Querformat-Fotos in Hochformat-Zellen drehen, damit sie größer erscheinen | aus |
| Ausgabe | Alle Fotos in **ein** PDF / **ein PDF pro Foto** (nur bei 1×1 sinnvoll) | ein PDF |
| Qualität | Klein (150 dpi) / Standard (220 dpi) / Druck (300 dpi) | Standard |

Später denkbar: Hintergrundfarbe, Rahmenlinie um jedes Foto, Bildunterschrift
(Datum oder Dateiname), Seitenzahlen, Kopfzeile/Titel.

### 2.3 Vorschau & Export
- Live-Vorschau: Jede Änderung an Raster/Rand wird sofort in einer Seitenvorschau
  angezeigt; man kann durch die Seiten wischen. Anzeige „12 Fotos → 3 Seiten“.
- Export über das iOS-Teilen-Menü: In „Dateien“ sichern, per Mail/Messenger senden,
  AirDrop, direkt drucken.
- Dateiname vorschlagen (z. B. `Fotos_2026-10-28.pdf`), editierbar.
- Die letzten Einstellungen werden gespeichert und beim nächsten Start verwendet.

## 3. Bedienablauf (Screens)

```
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ 1. Start         │   │ 2. Auswahl       │   │ 3. Layout        │   │ 4. Export        │
│                  │   │                  │   │                  │   │                  │
│  [ Fotos         │──▶│  ▢ ▢ ▢ ▢         │──▶│  ┌────────────┐  │──▶│  Dateiname       │
│    auswählen ]   │   │  ▢ ▢ ▢ ▢         │   │  │ ▢ ▢        │  │   │  Qualität        │
│                  │   │  (sortieren,     │   │  │ ▢ ▢        │  │   │                  │
│  Zuletzt:        │   │   entfernen, +)  │   │  └────────────┘  │   │  [ Teilen /      │
│  Raster 2×2      │   │                  │   │  Raster: 1×1 2×2 │   │    Sichern ]     │
│  Rand 10 mm      │   │  12 Fotos        │   │  Rand ─●──       │   │                  │
└──────────────────┘   └──────────────────┘   │  3 Seiten        │   └──────────────────┘
                                              └──────────────────┘
```

In der Praxis lassen sich Schritt 2 und 3 auf einem Bildschirm zusammenfassen
(oben Vorschau, unten Einstellungen, Fotoleiste zum Sortieren), sodass der typische
Fall „Fotos auswählen → Teilen“ nur **zwei Taps plus Auswahl** braucht, weil 2×2 schon
voreingestellt ist.

## 4. Technisches Konzept

### 4.1 Plattform & Technik
- **Sprache/UI:** Swift, SwiftUI
- **Mindestversion:** iOS 17 (wegen geordneter Mehrfachauswahl im `PhotosPicker`
  und moderner SwiftUI-APIs; deckt praktisch alle aktiven iPhones ab)
- **Geräte:** iPhone, iPad läuft automatisch mit
- **Frameworks:** SwiftUI, PhotosUI, UIKit (`UIGraphicsPDFRenderer`), PDFKit, ImageIO
- **Keine** Drittbibliotheken, **kein** Backend, **keine** Netzwerkverbindung

### 4.2 Architektur (MVVM, überschaubar)

```
FotoPDF/
├── App/FotoPDFApp.swift            App-Einstieg
├── Model/
│   ├── LayoutSettings.swift        Raster, Rand, Abstand, Ausrichtung, Modus …
│   └── SelectedPhoto.swift         Referenz auf ein ausgewähltes Foto
├── Services/
│   ├── PhotoLoader.swift           lädt & verkleinert Fotos speicherschonend (ImageIO)
│   ├── GridLayout.swift            berechnet die Zellen-Rechtecke einer Seite
│   └── PDFComposer.swift           erzeugt das PDF Seite für Seite
├── ViewModel/ProjectViewModel.swift
└── Views/
    ├── StartView.swift
    ├── EditorView.swift            Fotoleiste + Vorschau + Einstellungen
    ├── LayoutControls.swift
    └── PDFPreview.swift            PDFKit-Vorschau
```

### 4.3 Maße & Layout-Berechnung

PDF-Koordinaten werden in Punkt (pt) angegeben, 1 pt = 1/72 Zoll.

- A4 = 210 × 297 mm = **595,28 × 841,89 pt**
- 1 mm = 2,8346 pt

Beispiel Standard (A4 hoch, Rand 10 mm, Abstand 5 mm, Raster 2×2):

```
Nutzbreite  = 595,28 − 2 × 28,35 = 538,58 pt
Nutzhöhe    = 841,89 − 2 × 28,35 = 785,19 pt
Zellbreite  = (538,58 − 1 × 14,17) / 2 = 262,2 pt  ≈ 92,5 mm
Zellhöhe    = (785,19 − 1 × 14,17) / 2 = 385,5 pt  ≈ 136 mm
```

Fotos pro Seite = Spalten × Zeilen; Seitenzahl = ⌈Anzahl Fotos / Fotos pro Seite⌉.
Die letzte Seite wird nur teilweise befüllt (Restzellen bleiben leer).

### 4.4 Kern-Code (Skizze)

So kompakt ist der eigentliche PDF-Teil:

```swift
import UIKit

enum FitMode { case fit, fill }

struct LayoutSettings {
    var pageSize = CGSize(width: 595.28, height: 841.89) // A4 hoch
    var margin: CGFloat = 28.35   // 10 mm
    var spacing: CGFloat = 14.17  // 5 mm
    var columns = 2
    var rows = 2
    var fitMode: FitMode = .fit
}

/// Rechtecke aller Zellen einer Seite, zeilenweise von links oben.
func cellRects(for s: LayoutSettings) -> [CGRect] {
    let content = CGRect(origin: .zero, size: s.pageSize).insetBy(dx: s.margin, dy: s.margin)
    let w = (content.width  - CGFloat(s.columns - 1) * s.spacing) / CGFloat(s.columns)
    let h = (content.height - CGFloat(s.rows - 1) * s.spacing) / CGFloat(s.rows)
    return (0..<s.rows).flatMap { r in
        (0..<s.columns).map { c in
            CGRect(x: content.minX + CGFloat(c) * (w + s.spacing),
                   y: content.minY + CGFloat(r) * (h + s.spacing),
                   width: w, height: h)
        }
    }
}

/// Foto proportional in die Zelle einpassen oder sie damit füllen.
func imageRect(for size: CGSize, in cell: CGRect, mode: FitMode) -> CGRect {
    let sx = cell.width / size.width, sy = cell.height / size.height
    let scale = mode == .fit ? min(sx, sy) : max(sx, sy)
    let w = size.width * scale, h = size.height * scale
    return CGRect(x: cell.midX - w / 2, y: cell.midY - h / 2, width: w, height: h)
}

/// Schreibt das PDF direkt in eine Datei; Fotos werden seitenweise geladen.
func writePDF(photoCount: Int,
              loadImage: (Int) -> UIImage?,
              settings s: LayoutSettings,
              to url: URL) throws {
    let cells = cellRects(for: s)
    let renderer = UIGraphicsPDFRenderer(bounds: CGRect(origin: .zero, size: s.pageSize))
    try renderer.writePDF(to: url) { ctx in
        for pageStart in stride(from: 0, to: photoCount, by: cells.count) {
            ctx.beginPage()
            for (offset, cell) in cells.enumerated() where pageStart + offset < photoCount {
                autoreleasepool {
                    guard let image = loadImage(pageStart + offset) else { return }
                    ctx.cgContext.saveGState()
                    ctx.cgContext.clip(to: cell) // nötig für „Füllen“
                    image.draw(in: imageRect(for: image.size, in: cell, mode: s.fitMode))
                    ctx.cgContext.restoreGState()
                }
            }
        }
    }
}
```

## 5. Datenschutz

- Alles passiert lokal auf dem Gerät, keine Daten verlassen das iPhone (außer der
  Nutzer teilt das PDF aktiv).
- Durch den System-Picker ist **keine** Berechtigung für die Fotomediathek nötig.
- Kein Tracking, keine Accounts → App-Store-Datenschutzangabe: „Keine Daten erfasst“.

## 6. Abgrenzung zu vorhandenen iOS-Funktionen

iOS kann bereits Fotos als PDF ausgeben (Fotos-App → Drucken → Vorschau aufziehen, oder
Kurzbefehl „PDF erstellen“). Dabei gibt es aber **kein frei wählbares Raster, keine
Rand-Einstellungen und keine verlässliche A4-Seitengröße**. Genau diese Lücke schließt
die App.

## 7. Risiken & Lösungen

| Risiko | Lösung |
|---|---|
| Speicher läuft voll bei vielen großen Fotos (ein 48-MP-Foto belegt dekodiert ~190 MB) | Fotos nie alle gleichzeitig laden; mit ImageIO (`CGImageSourceCreateThumbnailAtIndex`) direkt auf die benötigte Auflösung verkleinert laden; PDF seitenweise direkt in eine Datei schreiben (siehe Code) |
| Große PDF-Dateien | Fotos auf Zielauflösung herunterrechnen (bei 2×2 und 220 dpi reichen ca. 800 × 1180 px pro Foto); Qualitätsstufe wählbar |
| Fotos liegen nur in iCloud | Der Picker lädt sie nach; Fortschrittsanzeige einbauen |
| Falsche Drehung (EXIF-Ausrichtung) | ImageIO-Option `kCGImageSourceCreateThumbnailWithTransform` berücksichtigt sie automatisch |
| HEIC-, Live- und RAW-Fotos | HEIC/Live: problemlos (Standbild wird verwendet); RAW: als JPEG-Vorschau laden |
| Lange Erstellungszeit | Erzeugung im Hintergrund mit Fortschrittsbalken; Vorschau mit kleinen Vorschaubildern |

## 8. Umsetzungsplan & Aufwand

Schätzung für eine Person mit iOS-Erfahrung:

| Phase | Inhalt | Aufwand |
|---|---|---|
| **1 – MVP** | Fotoauswahl, Raster (Vorlagen + eigenes, Standard 2×2), Rand, Abstand, Einpassen/Füllen, Hoch/Quer, ein gemeinsames PDF, Teilen-Menü | ca. 5–8 Personentage |
| **2 – Komfort** | Live-Vorschau mit PDFKit, Umsortieren per Drag & Drop, „ein PDF pro Foto“, Qualitätsstufen, Einstellungen merken, Auto-Drehen | ca. 4–6 Personentage |
| **3 – Feinschliff** | App-Icon, Dark Mode, iPad-Layout, Lokalisierung DE/EN, Barrierefreiheit, Tests, App-Store-Einreichung | ca. 4–6 Personentage |
| Optional | Rahmen, Bildunterschriften, Seitenzahlen, weitere Papierformate | je 0,5–2 Tage |

**Gesamt bis zur App-Store-reifen Version: etwa 3–4 Wochen.**

## 9. Was du zum Starten brauchst

- **Mac mit Xcode** (kostenlos im Mac App Store) – iOS-Apps lassen sich nur auf einem
  Mac bauen.
- **Nur für dich selbst:** Mit einer normalen Apple-ID kostenlos aufs eigene iPhone
  installierbar (die Installation muss dann alle 7 Tage über Xcode erneuert werden).
- **Dauerhaft, TestFlight oder App Store:** Apple Developer Program, 99 €/Jahr.
- Die App-Store-Prüfung ist bei dieser Art App unkritisch (klarer Nutzen, keine
  Berechtigungen, keine Nutzerdaten).

## 10. Empfehlung

Umsetzen. Die Anforderungen passen sehr gut zu dem, was iOS von Haus aus kann; das
technische Risiko ist gering. Empfohlener Einstieg ist das **MVP aus Phase 1** mit einem
einzigen Editor-Bildschirm und 2×2 als Standard. Damit ist der Hauptnutzen sofort da,
der Rest kann schrittweise ergänzt werden.

### Offene Fragen an dich
1. Nur für dich privat oder im App Store veröffentlichen?
2. Reicht A4, oder werden weitere Formate (z. B. A5, US Letter) gebraucht?
3. Sollen Fotos im Raster auch beschriftet werden können (z. B. Datum oder eigener Text)?
4. Soll beim Raster 1×1 standardmäßig *ein* PDF mit allen Seiten entstehen oder *ein
   PDF je Foto*?
