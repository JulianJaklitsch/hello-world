import Foundation

enum FileNaming {
    /// Vorschlag, z. B. „Fotos 2026-10-28“.
    static func defaultBaseName(date: Date = .now) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.dateFormat = "yyyy-MM-dd"
        return "Fotos \(formatter.string(from: date))"
    }

    /// Macht aus der Eingabe einen gültigen Dateinamen (ohne Endung).
    static func sanitized(_ input: String, fallback: String) -> String {
        let forbidden = CharacterSet(charactersIn: "/\\:*?\"<>|").union(.controlCharacters)
        var name = input.components(separatedBy: forbidden).joined(separator: "-")
            .trimmingCharacters(in: .whitespacesAndNewlines)
        if name.lowercased().hasSuffix(".pdf") {
            name = String(name.dropLast(4)).trimmingCharacters(in: .whitespaces)
        }
        while name.hasPrefix(".") {
            name.removeFirst() // keine versteckten Dateien
        }
        name = String(name.prefix(100))
        return name.isEmpty ? fallback : name
    }

    /// „Urlaub.pdf“ bzw. „Urlaub – Teil 1 von 2.pdf“, „Urlaub – Teil 2 von 2.pdf“.
    static func partFileNames(base: String, partCount: Int) -> [String] {
        guard partCount > 1 else { return ["\(base).pdf"] }
        return (1...partCount).map { "\(base) – Teil \($0) von \(partCount).pdf" }
    }
}
