# FotoPDF – iOS-App

Fotos aus der Galerie zu A4-PDFs zusammenstellen: ein oder mehrere Fotos pro Seite
(Standard 2×2), mit Rand, eingebautem Kompressor und automatischer Aufteilung in
mehrere PDFs zu je höchstens 20 MB. PDFs lassen sich benennen, in „Dateien“ sichern,
per Mail (Outlook oder Apple Mail) senden und unter „Meine PDFs“ verwalten.

Konzept: [`../docs/ios-foto-pdf-app/KONZEPT.md`](../docs/ios-foto-pdf-app/KONZEPT.md)

## Auf dem Mac starten

Voraussetzungen: Mac mit **Xcode 16 oder neuer** (kostenlos im Mac App Store), iPhone mit
**iOS 17 oder neuer**.

1. Repository auf den Mac holen:
   ```sh
   git clone https://github.com/JulianJaklitsch/hello-world.git
   cd hello-world
   git checkout claude/ios-photo-pdf-converter-loq5am
   open ios/FotoPDF.xcodeproj
   ```
2. In Xcode links das Projekt **FotoPDF** anklicken → Target **FotoPDF** →
   Reiter **Signing & Capabilities** → bei **Team** deine Apple-ID auswählen
   (ggf. über „Add an Account…“ anmelden; eine kostenlose Apple-ID reicht).
3. Falls Xcode meldet, dass die **Bundle Identifier** schon vergeben ist: dort einen
   eigenen Wert eintragen, z. B. `de.deinname.FotoPDF`.
4. Zum Ausprobieren ohne iPhone: oben einen Simulator wählen (z. B. „iPhone 16“) und
   **▶︎** drücken. Fotos lassen sich per Drag & Drop in den Simulator ziehen.
5. Auf dem eigenen iPhone: iPhone per Kabel verbinden, oben als Ziel auswählen, **▶︎**.
   Beim ersten Mal auf dem iPhone unter
   *Einstellungen › Allgemein › VPN & Geräteverwaltung* dem Entwickler vertrauen und
   unter *Einstellungen › Datenschutz & Sicherheit* den **Entwicklermodus** aktivieren.

Hinweis: Mit einer kostenlosen Apple-ID läuft die installierte App 7 Tage; danach in
Xcode einfach erneut auf **▶︎** drücken. Mit dem Apple Developer Program (99 €/Jahr)
entfällt das, und die App kann über TestFlight oder den App Store verteilt werden.

## Aufbau

```
FotoPDF/
├── App/FotoPDFApp.swift          App-Einstieg
├── Model/                        Einstellungen, ausgewählte Fotos, Mail-Weg
├── Services/
│   ├── GridLayout.swift          Zellen und Foto-Platzierung (für PDF und Vorschau)
│   ├── ImageCompressor.swift     verkleinern + JPEG-Kompression (ImageIO)
│   ├── PDFComposer.swift         komprimieren → PDF schreiben → messen → aufteilen
│   ├── PDFSplitter.swift         20-MB-Grenze, gleich große Teile
│   ├── FileNaming.swift          Dateinamen bereinigen, „Teil 1 von 3“
│   ├── PDFLibrary.swift          „Meine PDFs“ (Dokumente-Ordner der App)
│   ├── PhotoImporter.swift       Fotos aus der Galerie als Dateien übernehmen
│   └── WorkDirectory.swift       temporäre Arbeitsordner
├── ViewModel/ProjectViewModel.swift
└── Views/                        Editor, Vorschau, Export, Meine PDFs, Mail/Teilen
```

Die 20-MB-Grenze steht in `Services/PDFSplitter.swift` (`maxFileSize`).

## Was als Erstes zu testen ist

Der Code wurde ohne Mac geschrieben und ist noch **nicht kompiliert**. Beim ersten
Öffnen in Xcode bitte bauen (⌘B) und eventuelle Fehlermeldungen zurückmelden. Danach:

- 1 Foto, Raster 1×1 → eine A4-Seite, Rand prüfen
- 10 Fotos, Raster 2×2 → 3 Seiten, Vorschau und PDF stimmen überein
- Viele Fotos (z. B. 150) mit Kompression „Druck“ → mehrere Teile, jeder ≤ 20 MB
- Name vergeben → Dateiname und „Teil x von n“ korrekt
- „In ‚Dateien‘ sichern“, „Per Mail senden“ mit Outlook, „Meine PDFs“ (umbenennen, löschen)
