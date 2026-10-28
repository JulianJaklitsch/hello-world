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
| **PDF in der App selbst benennen** | Namensfeld vor dem Export | ✅ einfach |
| **In „Dateien“ speichern** (iCloud Drive, „Auf meinem iPhone“, Google Drive …) | System-Ordnerauswahl (`UIDocumentPickerViewController`) | ✅ einfach |
| **Per Mail senden** | Mail-Fenster direkt in der App (`MFMailComposeViewController`) | ✅ einfach |
| Weitere Wege (AirDrop, WhatsApp, Drucken …) | Teilen-Menü (`ShareLink`) | ✅ einfach |
| **Eingebauter Kompressor** | ImageIO: Fotos verkleinern + JPEG-Qualität steuern | ✅ machbar |
| **Max. 20 MB pro PDF, sonst nach der Kompression in mehrere PDFs aufteilen** | Dateigröße messen, an Seitengrenzen aufteilen | ✅ machbar |

Etwas Sorgfalt brauchen nur zwei Bereiche: der **Speicherverbrauch bei vielen Fotos**
(z. B. 100+ Bilder in hoher Auflösung) und die **zuverlässige Einhaltung der
20-MB-Grenze**. Für beides gibt es bewährte Lösungen (siehe Abschnitte 2.4, 4.5 und 7).

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
| **Kompression** | Stark (150 dpi, JPEG 60 %) / Standard (220 dpi, JPEG 75 %) / Hoch für Druck (300 dpi, JPEG 85 %), siehe 2.4 | Standard |

Später denkbar: Hintergrundfarbe, Rahmenlinie um jedes Foto, Bildunterschrift
(Datum oder Dateiname), Seitenzahlen, Kopfzeile/Titel.

### 2.3 Vorschau
- Live-Vorschau: Jede Änderung an Raster/Rand wird sofort in einer Seitenvorschau
  angezeigt; man kann durch die Seiten wischen. Anzeige „12 Fotos → 3 Seiten“.
- Vor dem Export wird die geschätzte Größe angezeigt, z. B.
  „ca. 18 MB · 1 PDF“ oder „ca. 47 MB · wird in 3 PDFs à ca. 16 MB aufgeteilt“.
- Die letzten Einstellungen werden gespeichert und beim nächsten Start verwendet.

Benennen, Speichern und Mail sind in Abschnitt 2.5 beschrieben.

### 2.4 Kompressor & automatische Aufteilung (max. 20 MB pro PDF)

Ein Kompressor ist **immer aktiv**. Die Reihenfolge ist fest: **erst komprimieren,
dann prüfen, erst danach (falls nötig) aufteilen.**

```
 Fotos ──▶ 1. KOMPRIMIEREN ──▶ 2. PDF erzeugen ──▶ 3. Größe prüfen
                                                       │
                              ≤ 20 MB ◀────────────────┤
                                 │                     │ > 20 MB
                                 ▼                     ▼
                              1 PDF            4. AUFTEILEN in so viele PDFs
                                                  wie nötig (je ≤ 20 MB,
                                                  an Seitengrenzen)
```

**1. Komprimieren** – zwei Hebel, die zusammen die Datenmenge drastisch verringern:
- **Verkleinern auf die tatsächlich benötigte Auflösung.** Ein iPhone-Foto hat 12–48
  Megapixel; eine Zelle im 2×2-Raster braucht bei 220 dpi nur rund 1 Megapixel
  (ca. 800 × 1180 Pixel). Alles darüber ist im PDF unsichtbar, kostet aber Speicher.
  Die Zielauflösung wird pro Foto aus Zellgröße, Raster und Kompressionsstufe berechnet.
- **JPEG-Kompression** mit einstellbarer Qualität (60 / 75 / 85 %). HEIC-Fotos werden
  dabei in JPEG umgewandelt (PDF kann HEIC nicht direkt einbetten).

**2. PDF erzeugen** – aus den bereits komprimierten Bildern.

**3. Größe prüfen** – die echte Dateigröße des fertigen PDFs wird gemessen. Die Grenze
gilt hart: **20 MB = 20.000.000 Byte** (dezimal, so wie iOS „Dateien“ und Mailprogramme
zählen; dadurch bleibt man auch bei binärer Zählweise sicher darunter).

**4. Aufteilen** – nur wenn das *komprimierte* PDF größer als 20 MB ist:
- Aufgeteilt wird **immer an Seitengrenzen**; eine Seite wird nie zerschnitten, die
  Seitenreihenfolge bleibt erhalten (Teil 1 = Seiten 1 bis k, Teil 2 = die nächsten usw.).
- Es werden **so viele Teile wie nötig** erzeugt (2, 3, 4, …), aber nie mehr als
  nötig. Beispiel: 47 MB → 3 Teile, 35 MB → 2 Teile.
- Die Teile werden **möglichst gleich groß** gemacht (z. B. 3 × 16 MB statt
  20 + 20 + 7 MB).
- Dateinamen: der selbst vergebene Name plus Teilnummer, z. B.
  `Urlaub Kroatien – Teil 1 von 3.pdf` … `Urlaub Kroatien – Teil 3 von 3.pdf` (siehe 2.5).
- Jeder Teil wird nach dem Schreiben nochmals gemessen. Würde ein Teil die 20 MB doch
  überschreiten, wird er erneut aufgeteilt; die Grenze gilt damit garantiert.
- Sonderfall „eine einzelne Seite > 20 MB“: praktisch ausgeschlossen (eine 3×4-Seite in
  Druckqualität hat ca. 5–8 MB). Falls doch, werden nur die Fotos dieser Seite stärker
  komprimiert.

**Orientierungswerte** (Schätzung, abhängig vom Motiv; wird im Prototyp verifiziert):

| Raster | Kompression | ca. Größe pro Seite | Seiten pro PDF (20 MB) | Fotos pro PDF (20 MB) |
|---|---|---|---|---|
| 1×1 (A4) | Standard | 0,8–1,5 MB | 13–25 | 13–25 |
| 2×2 | Standard | 0,6–1,2 MB | 16–33 | 65–130 |
| 2×2 | Stark | 0,3–0,6 MB | 33–66 | 130–260 |
| 2×2 | Hoch (Druck) | 1,2–2,4 MB | 8–16 | 33–66 |
| zum Vergleich: unkomprimiert | – | 3–6 MB pro Foto | – | nur ca. 3–6 |

Mehr Fotos sind kein Problem, es entstehen dann einfach entsprechend mehr Teile.

### 2.5 PDF benennen, in „Dateien“ speichern und per Mail senden

Der Export-Bildschirm hat drei klare Aktionen, die man einzeln **oder nacheinander**
nutzen kann (z. B. erst in „Dateien“ sichern, dann noch per Mail schicken):

```
┌──────────────────────────────────┐
│  Name des PDFs                   │
│  ┌────────────────────────┐      │
│  │ Urlaub Kroatien        │ .pdf │
│  └────────────────────────┘      │
│                                  │
│  ca. 47 MB → 3 PDFs à ca. 16 MB  │
│  Kompression: Standard  ▾        │
│                                  │
│  [   In „Dateien“ sichern    ]   │
│  [   Per Mail senden         ]   │
│  [   Weitere … (Teilen)      ]   │
└──────────────────────────────────┘
```

**1. PDF selbst benennen**
- Namensfeld ist vorausgefüllt mit einem Vorschlag (`Fotos 2026-10-28`) und beim
  Öffnen des Bildschirms schon markiert, sodass man direkt lostippen kann.
- Die Endung `.pdf` hängt die App automatisch an (grau daneben angezeigt).
- Umlaute, Leerzeichen und Sonderzeichen wie `&` oder `–` sind erlaubt. Zeichen, die
  in Dateinamen verboten sind (`/ \ : * ? " < > |`), werden automatisch durch `-`
  ersetzt; ein leeres Feld fällt auf den Vorschlag zurück.
- Wird das PDF aufgeteilt (2.4), bekommen die Teile denselben Namen plus Teilnummer:
  `Urlaub Kroatien – Teil 1 von 3.pdf`, `… – Teil 2 von 3.pdf`, `… – Teil 3 von 3.pdf`.
- Der Name wird auch als Titel in die PDF-Metadaten geschrieben (wird z. B. in der
  Vorschau am Mac oder in Acrobat als Dokumenttitel angezeigt).

**2. In „Dateien“ speichern**
- Tippen auf „In ‚Dateien‘ sichern“ öffnet die iOS-Ordnerauswahl. Man wählt den
  Speicherort selbst: iCloud Drive, „Auf meinem iPhone“ oder angebundene Dienste wie
  Google Drive, OneDrive oder Dropbox; neue Ordner lassen sich dort direkt anlegen.
- Bei Aufteilung werden alle Teile in einem Schritt in denselben Ordner gesichert.
- Gibt es im Zielordner schon eine Datei mit demselben Namen, kümmert sich der
  System-Dialog darum (Ersetzen oder beide behalten); das wird im Prototyp geprüft.
- Keine zusätzliche Berechtigung nötig.
- Optional (Phase 2): Die App legt zusätzlich eine Kopie in ihrem eigenen Ordner ab,
  der in der „Dateien“-App unter „Auf meinem iPhone → FotoPDF“ erscheint. So gibt es
  eine Liste „Meine PDFs“, in der man frühere PDFs umbenennen, erneut senden oder
  löschen kann.

**3. Per Mail senden**
- Tippen auf „Per Mail senden“ öffnet ein Mail-Fenster **direkt in der App**:
  das PDF ist schon angehängt, der Betreff ist mit dem PDF-Namen vorausgefüllt,
  man trägt nur noch den Empfänger ein und sendet. Danach ist man wieder in der App.
- Das eingebaute Mail-Fenster nutzt die Apple-Mail-App. Ist dort kein Konto
  eingerichtet (wer z. B. nur die Gmail- oder Outlook-App nutzt), öffnet die App
  stattdessen automatisch das Teilen-Menü, in dem man die eigene Mail-App wählt;
  das PDF wird auch dort angehängt.
- **Aufgeteilte PDFs und Mail-Größenlimits:** Jeder Teil ist höchstens 20 MB groß,
  alle Teile zusammen aber mehr; so große Mails lehnen die meisten Anbieter ab
  (Gmail 25 MB, Outlook 20 MB, viele Firmen-Server 10–25 MB). Deshalb wird bei
  aufgeteilten PDFs angeboten:
  - **„Jeden Teil als eigene Mail“** (Standard): Es öffnen sich nacheinander so viele
    Mail-Fenster wie Teile, Betreff „Urlaub Kroatien – Teil 1 von 3“, „Teil 2 von 3“
    usw.; der Empfänger aus der ersten Mail wird in die folgenden übernommen.
  - **„Alle Teile in einer Mail“**: sinnvoll mit iCloud Mail Drop (Apple Mail bietet
    bei großen Anhängen an, sie über iCloud bis 5 GB zu versenden); ob Mail Drop auch
    im eingebauten Mail-Fenster angeboten wird, wird im Prototyp geprüft.
- **Hinweis zur Mail-Größe:** Anhänge werden beim Mail-Versand technisch umkodiert
  (Base64) und dadurch um etwa ein Drittel größer. Ein 20-MB-PDF ist unterwegs also
  ca. 27 MB groß. Je nach Anbieter (v. a. Outlook mit 20 MB, Gmail mit 25 MB) kann eine
  solche Mail trotzdem abgelehnt werden. Wenn die Teile garantiert per Mail durchgehen
  sollen, wären ca. **14 MB** pro Teil die sichere Grenze. Die Grenze ist im Code eine
  einzige Konstante und lässt sich jederzeit ändern.

**4. Weitere** – öffnet das normale iOS-Teilen-Menü (AirDrop, WhatsApp, Nachrichten,
Drucken, andere Apps).

## 3. Bedienablauf (Screens)

```
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ 1. Start         │   │ 2. Auswahl       │   │ 3. Layout        │   │ 4. Export        │
│                  │   │                  │   │                  │   │                  │
│  [ Fotos         │──▶│  ▢ ▢ ▢ ▢         │──▶│  ┌────────────┐  │──▶│  Name: [Urlaub]  │
│    auswählen ]   │   │  ▢ ▢ ▢ ▢         │   │  │ ▢ ▢        │  │   │  Kompression     │
│                  │   │  (sortieren,     │   │  │ ▢ ▢        │  │   │                  │
│  Zuletzt:        │   │   entfernen, +)  │   │  └────────────┘  │   │  [In Dateien]    │
│  Raster 2×2      │   │                  │   │  Raster: 1×1 2×2 │   │  [Per Mail]      │
│  Rand 10 mm      │   │  12 Fotos        │   │  Rand ─●──       │   │  [Weitere …]     │
└──────────────────┘   └──────────────────┘   │  3 Seiten        │   └──────────────────┘
                                              └──────────────────┘
```

In der Praxis lassen sich Schritt 2 und 3 auf einem Bildschirm zusammenfassen
(oben Vorschau, unten Einstellungen, Fotoleiste zum Sortieren), sodass der typische
Fall „Fotos auswählen → Namen tippen → In Dateien sichern / Per Mail senden“ mit sehr
wenigen Taps auskommt, weil 2×2 schon voreingestellt ist.

## 4. Technisches Konzept

### 4.1 Plattform & Technik
- **Sprache/UI:** Swift, SwiftUI
- **Mindestversion:** iOS 17 (wegen geordneter Mehrfachauswahl im `PhotosPicker`
  und moderner SwiftUI-APIs; deckt praktisch alle aktiven iPhones ab)
- **Geräte:** iPhone, iPad läuft automatisch mit
- **Frameworks:** SwiftUI, PhotosUI, UIKit (`UIGraphicsPDFRenderer`,
  `UIDocumentPickerViewController`), PDFKit, ImageIO, MessageUI (Mail)
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
│   ├── ImageCompressor.swift       verkleinert + JPEG-komprimiert jedes Foto
│   ├── PDFComposer.swift           erzeugt das PDF Seite für Seite
│   ├── PDFSplitter.swift           prüft die 20-MB-Grenze und teilt bei Bedarf auf
│   └── FileNaming.swift            bereinigt den eingegebenen Namen, Teil-Namen
├── ViewModel/ProjectViewModel.swift
└── Views/
    ├── StartView.swift
    ├── EditorView.swift            Fotoleiste + Vorschau + Einstellungen
    ├── LayoutControls.swift
    ├── PDFPreview.swift            PDFKit-Vorschau
    ├── ExportView.swift            Namensfeld, Größe, Sichern / Mail / Weitere
    ├── SaveToFilesView.swift       Ordnerauswahl für „Dateien“
    └── MailView.swift              Mail-Fenster mit PDF-Anhang
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

### 4.5 Kompressor & Aufteilung (Skizze)

**Komprimieren:** Jedes Foto wird mit ImageIO direkt in der Zielauflösung geladen
(ohne das volle 48-MP-Bild in den Speicher zu holen) und als JPEG kodiert. Die
JPEG-Daten landen in einem temporären Ordner, nicht im Arbeitsspeicher.

```swift
import ImageIO
import UniformTypeIdentifiers

enum Compression {
    case strong, standard, print
    var dpi: CGFloat { switch self { case .strong: 150; case .standard: 220; case .print: 300 } }
    var jpegQuality: CGFloat { switch self { case .strong: 0.60; case .standard: 0.75; case .print: 0.85 } }
}

/// `drawSize` = Größe, in der das Foto auf der Seite gezeichnet wird (in pt, aus `imageRect`).
func compressedJPEG(from source: URL, drawSize: CGSize, compression: Compression) -> Data? {
    let maxPixels = max(drawSize.width, drawSize.height) / 72 * compression.dpi
    guard let src = CGImageSourceCreateWithURL(source as CFURL, nil),
          let image = CGImageSourceCreateThumbnailAtIndex(src, 0, [
              kCGImageSourceCreateThumbnailFromImageAlways: true,
              kCGImageSourceCreateThumbnailWithTransform: true,   // EXIF-Drehung übernehmen
              kCGImageSourceThumbnailMaxPixelSize: maxPixels
          ] as CFDictionary) else { return nil }

    let output = NSMutableData()
    guard let dest = CGImageDestinationCreateWithData(output, UTType.jpeg.identifier as CFString, 1, nil)
    else { return nil }
    CGImageDestinationAddImage(dest, image,
        [kCGImageDestinationLossyCompressionQuality: compression.jpegQuality] as CFDictionary)
    return CGImageDestinationFinalize(dest) ? output as Data : nil
}
```

Beim Zeichnen ins PDF wird das Bild aus den JPEG-Daten erzeugt
(`CGImage(jpegDataProviderSource:…)`); Quartz bettet solche Bilder in der Regel
unverändert als JPEG ins PDF ein, sodass die PDF-Größe ≈ Summe der JPEG-Größen ist.
Das wird im Prototyp geprüft. Die 20-MB-Garantie hängt aber nicht davon ab, weil am
Ende immer die **echte Dateigröße** gemessen wird.

**Aufteilen:** Da die Größe jedes komprimierten Fotos bekannt ist, kennt man auch die
ungefähre Größe jeder Seite. Daraus wird berechnet, wie viele Teile mindestens nötig
sind, und dann so aufgeteilt, dass die Teile möglichst gleich groß werden:

```swift
let maxFileSize    = 20_000_000   // harte Obergrenze pro PDF (20 MB)
let targetPartSize = 18_500_000   // Sicherheitsabstand für PDF-Verwaltungsdaten

/// Zusammenhängende Seitenbereiche, keiner größer als `cap` Byte.
func greedyParts(_ pageSizes: [Int], cap: Int) -> [Range<Int>] {
    var parts: [Range<Int>] = []
    var start = 0, sum = 0
    for (i, size) in pageSizes.enumerated() {
        if sum + size > cap && i > start {
            parts.append(start..<i)
            start = i
            sum = 0
        }
        sum += size
    }
    if start < pageSizes.count { parts.append(start..<pageSizes.count) }
    return parts
}

/// So wenige Teile wie nötig, dabei möglichst gleich groß.
func balancedParts(_ pageSizes: [Int], limit: Int = targetPartSize) -> [Range<Int>] {
    let count = greedyParts(pageSizes, cap: limit).count
    var lo = pageSizes.max() ?? 0, hi = limit
    while lo < hi {   // kleinste Obergrenze suchen, die mit `count` Teilen auskommt
        let mid = (lo + hi) / 2
        if greedyParts(pageSizes, cap: mid).count <= count { hi = mid } else { lo = mid + 1 }
    }
    return greedyParts(pageSizes, cap: lo)
}
```

Ablauf im `PDFSplitter`:
1. Summe aller Seitengrößen ≤ 18,5 MB → ein PDF schreiben.
2. Sonst `balancedParts` → für jeden Bereich ein eigenes PDF schreiben.
3. Jede geschriebene Datei messen; liegt eine über `maxFileSize`, wird nur dieser Teil
   erneut aufgeteilt.

### 4.6 Benennen, Speichern, Mail (Skizze)

**Dateiname:** Die PDFs werden im temporären Ordner gleich unter dem gewünschten Namen
geschrieben. So tragen sie diesen Namen automatisch in „Dateien“, im Mail-Anhang und im
Teilen-Menü.

```swift
/// Macht aus der Eingabe einen gültigen Dateinamen (ohne Endung).
func sanitizedFileName(_ input: String, fallback: String) -> String {
    let forbidden = CharacterSet(charactersIn: "/\\:*?\"<>|").union(.controlCharacters)
    var name = input.components(separatedBy: forbidden).joined(separator: "-")
        .trimmingCharacters(in: .whitespacesAndNewlines)
    if name.lowercased().hasSuffix(".pdf") { name = String(name.dropLast(4)) }
    while name.hasPrefix(".") { name.removeFirst() }   // keine versteckten Dateien
    name = String(name.prefix(100))
    return name.isEmpty ? fallback : name
}

/// "Urlaub.pdf" bzw. "Urlaub – Teil 1 von 2.pdf", "Urlaub – Teil 2 von 2.pdf"
func partFileNames(base: String, partCount: Int) -> [String] {
    guard partCount > 1 else { return ["\(base).pdf"] }
    return (1...partCount).map { "\(base) – Teil \($0) von \(partCount).pdf" }
}
```

**In „Dateien“ sichern:** Die System-Ordnerauswahl kopiert eine oder mehrere Dateien in
den gewählten Ordner.

```swift
struct SaveToFilesView: UIViewControllerRepresentable {
    let files: [URL]   // ein PDF oder alle Teile

    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        UIDocumentPickerViewController(forExporting: files, asCopy: true)
    }
    func updateUIViewController(_ vc: UIDocumentPickerViewController, context: Context) {}
}
```

**Per Mail senden:**

```swift
import MessageUI

struct MailView: UIViewControllerRepresentable {
    let subject: String
    let attachments: [URL]
    var recipients: [String] = []
    let onFinish: (MFMailComposeResult) -> Void

    static var canSend: Bool { MFMailComposeViewController.canSendMail() }

    func makeUIViewController(context: Context) -> MFMailComposeViewController {
        let mail = MFMailComposeViewController()
        mail.mailComposeDelegate = context.coordinator
        mail.setSubject(subject)
        mail.setToRecipients(recipients)
        for url in attachments {
            if let data = try? Data(contentsOf: url) {
                mail.addAttachmentData(data, mimeType: "application/pdf",
                                       fileName: url.lastPathComponent)
            }
        }
        return mail
    }
    func updateUIViewController(_ vc: MFMailComposeViewController, context: Context) {}
    func makeCoordinator() -> Coordinator { Coordinator(onFinish: onFinish) }

    final class Coordinator: NSObject, MFMailComposeViewControllerDelegate {
        let onFinish: (MFMailComposeResult) -> Void
        init(onFinish: @escaping (MFMailComposeResult) -> Void) { self.onFinish = onFinish }

        func mailComposeController(_ controller: MFMailComposeViewController,
                                   didFinishWith result: MFMailComposeResult, error: Error?) {
            onFinish(result)   // z. B. nächsten Teil öffnen oder Fenster schließen
        }
    }
}
```

Ist `MailView.canSend` falsch (kein Konto in Apple Mail), zeigt die App stattdessen das
Teilen-Menü mit denselben Dateien. Bei „Jeden Teil als eigene Mail“ öffnet `onFinish`
nach dem Senden eines Teils automatisch das Fenster für den nächsten Teil.

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
| Große PDF-Dateien | Eingebauter Kompressor (2.4): Fotos auf Zielauflösung herunterrechnen + JPEG-Kompression; danach harte 20-MB-Grenze mit automatischer Aufteilung |
| Geschätzte Größe weicht von echter ab | Schätzung nur für Vorschau und Aufteilungsplan; entscheidend ist die gemessene Dateigröße, zu große Teile werden nachträglich weiter aufgeteilt |
| Empfänger bekommt mehrere Dateien | klare Namen „Teil 1 von 2“, alle Teile werden in einem Rutsch gesichert bzw. geteilt |
| Mail wird wegen Größe abgelehnt | aufgeteilte PDFs standardmäßig als eine Mail pro Teil senden; optional Mail Drop; bei Bedarf Grenze senken (ca. 14 MB ist für alle gängigen Anbieter sicher) |
| Kein Konto in Apple Mail eingerichtet | automatisch auf das Teilen-Menü ausweichen (Gmail, Outlook usw.) |
| Ungültige Zeichen im eingegebenen Namen | werden automatisch ersetzt, leerer Name fällt auf den Vorschlag zurück |
| Fotos liegen nur in iCloud | Der Picker lädt sie nach; Fortschrittsanzeige einbauen |
| Falsche Drehung (EXIF-Ausrichtung) | ImageIO-Option `kCGImageSourceCreateThumbnailWithTransform` berücksichtigt sie automatisch |
| HEIC-, Live- und RAW-Fotos | HEIC/Live: problemlos (Standbild wird verwendet); RAW: als JPEG-Vorschau laden |
| Lange Erstellungszeit | Erzeugung im Hintergrund mit Fortschrittsbalken; Vorschau mit kleinen Vorschaubildern |

## 8. Umsetzungsplan & Aufwand

Schätzung für eine Person mit iOS-Erfahrung:

| Phase | Inhalt | Aufwand |
|---|---|---|
| **1 – MVP** | Fotoauswahl, Raster (Vorlagen + eigenes, Standard 2×2), Rand, Abstand, Einpassen/Füllen, Hoch/Quer, ein gemeinsames PDF, **Kompressor, 20-MB-Grenze mit automatischer Aufteilung in beliebig viele Teile, PDF selbst benennen, in „Dateien“ sichern, per Mail senden (inkl. eine Mail pro Teil)**, Teilen-Menü | ca. 10–13 Personentage |
| **2 – Komfort** | Live-Vorschau mit PDFKit, Umsortieren per Drag & Drop, „ein PDF pro Foto“, Größenanzeige vor dem Export, Einstellungen merken, Auto-Drehen, Liste „Meine PDFs“ (umbenennen, erneut senden) | ca. 5–8 Personentage |
| **3 – Feinschliff** | App-Icon, Dark Mode, iPad-Layout, Lokalisierung DE/EN, Barrierefreiheit, Tests, App-Store-Einreichung | ca. 4–6 Personentage |
| Optional | Rahmen, Bildunterschriften, Seitenzahlen, weitere Papierformate | je 0,5–2 Tage |

**Gesamt bis zur App-Store-reifen Version: etwa 4–5 Wochen.**

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
einzigen Editor-Bildschirm, 2×2 als Standard, dem Kompressor samt 20-MB-Grenze sowie
Benennen, Sichern in „Dateien“ und Mail-Versand von Anfang an. Damit ist der Hauptnutzen sofort da,
der Rest kann schrittweise ergänzt werden.

### Bereits entschieden
- Grenze pro PDF: **20 MB** (nach der Kompression gemessen).
- Reicht ein PDF nicht, werden **beliebig viele Teile** erzeugt (2, 3, 4, …).

### Offene Fragen an dich
1. Nur für dich privat oder im App Store veröffentlichen?
2. Reicht A4, oder werden weitere Formate (z. B. A5, US Letter) gebraucht?
3. Sollen Fotos im Raster auch beschriftet werden können (z. B. Datum oder eigener Text)?
4. Soll beim Raster 1×1 standardmäßig *ein* PDF mit allen Seiten entstehen oder *ein
   PDF je Foto*?
5. Bleibt es bei 20 MB pro Teil, oder lieber ca. 14 MB, damit jede Mail sicher bei
   allen Anbietern durchgeht (siehe Hinweis in 2.5)?
6. Welche Mail-App nutzt du (Apple Mail, Gmail, Outlook …)? Davon hängt ab, ob das
   eingebaute Mail-Fenster oder das Teilen-Menü der Hauptweg wird.
7. Gibt es feste Empfänger (z. B. immer dieselbe Adresse), die vorausgefüllt sein
   sollen, oder einen Standard-Betreff / Standard-Text für die Mail?
8. Soll die App eine eigene Liste „Meine PDFs“ führen, um frühere PDFs später
   umzubenennen oder erneut zu senden (Phase 2)?
