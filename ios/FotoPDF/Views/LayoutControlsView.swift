import SwiftUI

/// Einstellungen für Raster, Seite, Fotos und Kompression (Abschnitte eines Formulars).
struct LayoutControlsView: View {
    @Binding var settings: LayoutSettings
    @State private var customMargin = false

    var body: some View {
        Section("Raster (Spalten × Zeilen)") {
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(GridPreset.all) { preset in
                        let selected = preset.columns == settings.columns && preset.rows == settings.rows
                        Button(preset.title) {
                            settings.columns = preset.columns
                            settings.rows = preset.rows
                        }
                        .buttonStyle(.bordered)
                        .tint(selected ? Color.accentColor : Color.secondary)
                        .fontWeight(selected ? .bold : .regular)
                    }
                }
                .padding(.vertical, 2)
            }
            Stepper("Spalten: \(settings.columns)", value: $settings.columns, in: LayoutSettings.columnRange)
            Stepper("Zeilen: \(settings.rows)", value: $settings.rows, in: LayoutSettings.rowRange)
        }

        Section("Seite (A4)") {
            Picker("Ausrichtung", selection: $settings.orientation) {
                ForEach(PageOrientation.allCases) { Text($0.title).tag($0) }
            }
            .pickerStyle(.segmented)

            VStack(alignment: .leading, spacing: 8) {
                Text("Seitenrand: \(Int(settings.marginMM)) mm")
                Picker("Seitenrand", selection: marginPreset) {
                    ForEach(MarginPreset.allCases) { Text($0.title).tag($0) }
                }
                .pickerStyle(.segmented)
                .labelsHidden()
                if marginPreset.wrappedValue == .custom {
                    Slider(value: $settings.marginMM, in: LayoutSettings.marginRange, step: 1)
                }
            }

            VStack(alignment: .leading, spacing: 8) {
                Text("Abstand zwischen Fotos: \(Int(settings.spacingMM)) mm")
                Slider(value: $settings.spacingMM, in: LayoutSettings.spacingRange, step: 1)
            }
        }

        Section {
            Picker("Bildanpassung", selection: $settings.fitMode) {
                ForEach(FitMode.allCases) { Text($0.title).tag($0) }
            }
            .pickerStyle(.segmented)
            Toggle("Fotos automatisch drehen", isOn: $settings.autoRotate)
        } header: {
            Text("Fotos")
        } footer: {
            Text("Einpassen zeigt das ganze Foto, Füllen nutzt die ganze Zelle und schneidet Ränder ab. Automatisch drehen dreht Querformat-Fotos in Hochformat-Zellen (und umgekehrt), damit sie größer erscheinen.")
        }

        Section {
            Picker("Kompression", selection: $settings.compression) {
                ForEach(CompressionLevel.allCases) { Text($0.title).tag($0) }
            }
            .pickerStyle(.segmented)
        } header: {
            Text("Kompression")
        } footer: {
            Text("Stark: kleinste Dateien (150 dpi). Standard: guter Kompromiss (220 dpi). Druck: beste Qualität (300 dpi). PDFs über 20 MB werden nach der Kompression automatisch in mehrere Teile aufgeteilt.")
        }
    }

    private var marginPreset: Binding<MarginPreset> {
        Binding {
            if customMargin { return .custom }
            return MarginPreset.allCases.first { $0.millimeters == settings.marginMM } ?? .custom
        } set: { preset in
            customMargin = preset == .custom
            if let millimeters = preset.millimeters {
                settings.marginMM = millimeters
            }
        }
    }
}
