import UIKit

/// Ein aus der Galerie ausgewähltes Foto. Das Original liegt als Datei im Arbeitsordner,
/// im Speicher wird nur ein kleines Vorschaubild gehalten.
struct SelectedPhoto: Identifiable {
    let id = UUID()
    let fileURL: URL
    /// Pixelgröße wie angezeigt (EXIF-Drehung bereits berücksichtigt).
    let pixelSize: CGSize
    let thumbnail: UIImage
}
