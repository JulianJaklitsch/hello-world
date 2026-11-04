import Foundation

/// Temporäre Arbeitsordner der App (importierte Fotos, Zwischenstände beim Erstellen).
enum WorkDirectory {
    private static var root: URL {
        FileManager.default.temporaryDirectory.appendingPathComponent("FotoPDF", isDirectory: true)
    }

    static var photos: URL { directory("Photos") }

    /// Löscht Reste früherer Sitzungen.
    static func reset() {
        try? FileManager.default.removeItem(at: root)
    }

    static func newPhotoURL(pathExtension: String) -> URL {
        photos.appendingPathComponent(UUID().uuidString)
            .appendingPathExtension(pathExtension.isEmpty ? "jpg" : pathExtension)
    }

    static func newJobDirectory() throws -> URL {
        let url = root.appendingPathComponent("Job-\(UUID().uuidString)", isDirectory: true)
        try FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
        return url
    }

    private static func directory(_ name: String) -> URL {
        let url = root.appendingPathComponent(name, isDirectory: true)
        try? FileManager.default.createDirectory(at: url, withIntermediateDirectories: true)
        return url
    }
}
