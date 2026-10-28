import Observation
import PhotosUI
import SwiftUI

/// Die aktuelle Auswahl an Fotos und die Layout-Einstellungen.
@Observable
final class ProjectViewModel {
    var photos: [SelectedPhoto] = []
    var settings: LayoutSettings
    var importMessage: String?
    private(set) var isImporting = false
    private(set) var importedCount = 0
    private(set) var importTotal = 0

    private static let settingsKey = "layoutSettings"

    init() {
        WorkDirectory.reset()
        if let data = UserDefaults.standard.data(forKey: Self.settingsKey),
           let saved = try? JSONDecoder().decode(LayoutSettings.self, from: data) {
            settings = saved
        } else {
            settings = LayoutSettings()
        }
    }

    var pageCount: Int { settings.pageCount(forPhotoCount: photos.count) }

    /// Grobe Schätzung der PDF-Größe nach der Kompression (nur zur Anzeige).
    var estimatedBytes: Int {
        let cells = GridLayout.cellRects(for: settings)
        let compression = settings.compression
        let pixels = photos.enumerated().reduce(0.0) { sum, entry in
            let size = entry.element.pixelSize
            let placement = GridLayout.placement(for: size, in: cells[entry.offset % cells.count], settings: settings)
            let longSide = ImageCompressor.targetLongSide(pixelSize: size, placement: placement, dpi: compression.dpi)
            let ratio = longSide / max(size.width, size.height, 1)
            return sum + Double(size.width * size.height * ratio * ratio)
        }
        return Int(pixels * compression.estimatedBytesPerPixel) + pageCount * 3_000
    }

    func saveSettings() {
        if let data = try? JSONEncoder().encode(settings) {
            UserDefaults.standard.set(data, forKey: Self.settingsKey)
        }
    }

    @MainActor
    func importItems(_ items: [PhotosPickerItem]) async {
        guard !items.isEmpty else { return }
        isImporting = true
        importTotal = items.count
        importedCount = 0
        var failed = 0
        for item in items {
            if let photo = await PhotoImporter.importPhoto(item) {
                photos.append(photo)
            } else {
                failed += 1
            }
            importedCount += 1
        }
        isImporting = false
        if failed > 0 {
            importMessage = failed == 1
                ? "1 Foto konnte nicht geladen werden."
                : "\(failed) Fotos konnten nicht geladen werden."
        }
    }

    func move(from source: IndexSet, to destination: Int) {
        photos.move(fromOffsets: source, toOffset: destination)
    }

    func remove(at offsets: IndexSet) {
        offsets.forEach { deleteFile(of: photos[$0]) }
        photos.remove(atOffsets: offsets)
    }

    func remove(_ photo: SelectedPhoto) {
        deleteFile(of: photo)
        photos.removeAll { $0.id == photo.id }
    }

    func removeAll() {
        photos.forEach(deleteFile(of:))
        photos.removeAll()
    }

    private func deleteFile(of photo: SelectedPhoto) {
        try? FileManager.default.removeItem(at: photo.fileURL)
    }
}
