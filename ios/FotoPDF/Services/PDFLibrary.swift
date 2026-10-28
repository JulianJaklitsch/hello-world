import Foundation
import Observation

struct LibraryFile: Identifiable, Hashable {
    let url: URL
    let byteCount: Int
    let modified: Date

    var id: URL { url }
    var name: String { url.deletingPathExtension().lastPathComponent }
}

enum PDFLibraryError: LocalizedError {
    case nameTaken(String)

    var errorDescription: String? {
        switch self {
        case .nameTaken(let name): "Es gibt schon ein PDF mit dem Namen „\(name)“."
        }
    }
}

/// „Meine PDFs“: der Dokumente-Ordner der App. Er erscheint in der Dateien-App
/// unter „Auf meinem iPhone › FotoPDF“.
@Observable
final class PDFLibrary {
    private(set) var files: [LibraryFile] = []

    static var directory: URL { URL.documentsDirectory }

    init() {
        reload()
    }

    func reload() {
        let keys: [URLResourceKey] = [.fileSizeKey, .contentModificationDateKey]
        let urls = (try? FileManager.default.contentsOfDirectory(
            at: Self.directory, includingPropertiesForKeys: keys, options: [.skipsHiddenFiles]
        )) ?? []
        files = urls
            .filter { $0.pathExtension.lowercased() == "pdf" }
            .map { url in
                let values = try? url.resourceValues(forKeys: Set(keys))
                return LibraryFile(url: url,
                                   byteCount: values?.fileSize ?? 0,
                                   modified: values?.contentModificationDate ?? .distantPast)
            }
            .sorted { $0.modified > $1.modified }
    }

    /// Übernimmt frisch erstellte Teile unter dem gewünschten Namen.
    /// Ist der Name schon vergeben, wird „(2)“, „(3)“ … angehängt.
    func store(parts: [URL], baseName: String) throws -> [URL] {
        let base = availableBaseName(for: baseName, partCount: parts.count)
        let names = FileNaming.partFileNames(base: base, partCount: parts.count)
        let stored = try zip(parts, names).map { source, name in
            let destination = Self.directory.appendingPathComponent(name)
            try FileManager.default.moveItem(at: source, to: destination)
            return destination
        }
        reload()
        return stored
    }

    func rename(_ file: LibraryFile, to newName: String) throws {
        let base = FileNaming.sanitized(newName, fallback: file.name)
        let destination = Self.directory.appendingPathComponent("\(base).pdf")
        guard destination != file.url else { return }
        let onlyCaseChanged = destination.path.lowercased() == file.url.path.lowercased()
        if !onlyCaseChanged && FileManager.default.fileExists(atPath: destination.path) {
            throw PDFLibraryError.nameTaken(base)
        }
        try FileManager.default.moveItem(at: file.url, to: destination)
        reload()
    }

    func delete(_ file: LibraryFile) {
        try? FileManager.default.removeItem(at: file.url)
        reload()
    }

    private func availableBaseName(for base: String, partCount: Int) -> String {
        var candidate = base
        var counter = 2
        while FileNaming.partFileNames(base: candidate, partCount: partCount).contains(where: exists(_:)) {
            candidate = "\(base) (\(counter))"
            counter += 1
        }
        return candidate
    }

    private func exists(_ name: String) -> Bool {
        FileManager.default.fileExists(atPath: Self.directory.appendingPathComponent(name).path)
    }
}
