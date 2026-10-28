import PhotosUI
import SwiftUI
import UniformTypeIdentifiers

/// Kopiert ein ausgewähltes Foto als Datei in den Arbeitsordner (statt es in den Speicher zu laden).
struct ImportedImageFile: Transferable {
    let url: URL

    static var transferRepresentation: some TransferRepresentation {
        FileRepresentation(importedContentType: .image) { received in
            let destination = WorkDirectory.newPhotoURL(pathExtension: received.file.pathExtension)
            try FileManager.default.copyItem(at: received.file, to: destination)
            return ImportedImageFile(url: destination)
        }
    }
}

enum PhotoImporter {
    /// Lange Seite der Vorschaubilder in Pixeln.
    static let thumbnailSize: CGFloat = 320

    static func importPhoto(_ item: PhotosPickerItem) async -> SelectedPhoto? {
        var fileURL: URL?
        if let file = try? await item.loadTransferable(type: ImportedImageFile.self) {
            fileURL = file.url
        } else if let data = try? await item.loadTransferable(type: Data.self) {
            let pathExtension = item.supportedContentTypes.first?.preferredFilenameExtension ?? "jpg"
            let url = WorkDirectory.newPhotoURL(pathExtension: pathExtension)
            if (try? data.write(to: url)) != nil {
                fileURL = url
            }
        }

        guard let fileURL,
              let pixelSize = ImageCompressor.orientedPixelSize(of: fileURL),
              let thumbnail = ImageCompressor.downsampledImage(at: fileURL, maxPixelSize: thumbnailSize)
        else { return nil }
        return SelectedPhoto(fileURL: fileURL, pixelSize: pixelSize, thumbnail: UIImage(cgImage: thumbnail))
    }
}
