import CoreGraphics
import Foundation

enum PageOrientation: String, CaseIterable, Codable, Identifiable {
    case portrait, landscape

    var id: Self { self }
    var title: String { self == .portrait ? "Hochformat" : "Querformat" }
}

enum FitMode: String, CaseIterable, Codable, Identifiable {
    /// Ganzes Foto sichtbar, ggf. mit Leerraum in der Zelle.
    case fit
    /// Zelle komplett gefüllt, überstehende Ränder werden abgeschnitten.
    case fill

    var id: Self { self }
    var title: String { self == .fit ? "Einpassen" : "Füllen" }
}

enum CompressionLevel: String, CaseIterable, Codable, Identifiable {
    case strong, standard, print

    var id: Self { self }

    var title: String {
        switch self {
        case .strong: "Stark"
        case .standard: "Standard"
        case .print: "Druck"
        }
    }

    /// Auflösung, mit der Fotos ins PDF eingebettet werden.
    var dpi: CGFloat {
        switch self {
        case .strong: 150
        case .standard: 220
        case .print: 300
        }
    }

    var jpegQuality: CGFloat {
        switch self {
        case .strong: 0.60
        case .standard: 0.75
        case .print: 0.85
        }
    }

    /// Erfahrungswert für die Größenschätzung vor dem Erstellen (nur Anzeige).
    var estimatedBytesPerPixel: Double {
        switch self {
        case .strong: 0.12
        case .standard: 0.22
        case .print: 0.32
        }
    }
}

enum MarginPreset: CaseIterable, Identifiable {
    case noMargin, narrow, normal, wide, custom

    var id: Self { self }

    var title: String {
        switch self {
        case .noMargin: "Kein"
        case .narrow: "Schmal"
        case .normal: "Normal"
        case .wide: "Breit"
        case .custom: "Eigener"
        }
    }

    var millimeters: Double? {
        switch self {
        case .noMargin: 0
        case .narrow: 5
        case .normal: 10
        case .wide: 20
        case .custom: nil
        }
    }
}

struct GridPreset: Hashable, Identifiable {
    let columns: Int
    let rows: Int

    var id: String { title }
    var title: String { "\(columns)×\(rows)" }

    static let all: [GridPreset] = [
        GridPreset(columns: 1, rows: 1),
        GridPreset(columns: 1, rows: 2),
        GridPreset(columns: 2, rows: 2),
        GridPreset(columns: 2, rows: 3),
        GridPreset(columns: 3, rows: 3),
        GridPreset(columns: 3, rows: 4),
    ]
}

struct LayoutSettings: Codable, Equatable {
    /// A4 in Punkt (1 pt = 1/72 Zoll).
    static let a4Portrait = CGSize(width: 595.28, height: 841.89)
    static let pointsPerMillimeter: CGFloat = 72 / 25.4

    static let columnRange = 1...6
    static let rowRange = 1...8
    static let marginRange: ClosedRange<Double> = 0...30
    static let spacingRange: ClosedRange<Double> = 0...20

    var columns = 2
    var rows = 2
    var orientation = PageOrientation.portrait
    var marginMM: Double = 10
    var spacingMM: Double = 5
    var fitMode = FitMode.fit
    var autoRotate = false
    var compression = CompressionLevel.standard

    var pageSize: CGSize {
        let a4 = Self.a4Portrait
        return orientation == .portrait ? a4 : CGSize(width: a4.height, height: a4.width)
    }

    var margin: CGFloat { CGFloat(marginMM) * Self.pointsPerMillimeter }
    var spacing: CGFloat { CGFloat(spacingMM) * Self.pointsPerMillimeter }
    var photosPerPage: Int { columns * rows }

    func pageCount(forPhotoCount count: Int) -> Int {
        count == 0 ? 0 : (count + photosPerPage - 1) / photosPerPage
    }
}
