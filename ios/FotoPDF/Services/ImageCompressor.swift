import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

/// Der eingebaute Kompressor: Fotos werden direkt in der benötigten Auflösung geladen
/// (ohne das volle Bild zu dekodieren) und als JPEG kodiert.
enum ImageCompressor {
    /// Pixelgröße des Fotos, wie es angezeigt wird (EXIF-Drehung berücksichtigt).
    static func orientedPixelSize(of url: URL) -> CGSize? {
        guard let source = CGImageSourceCreateWithURL(url as CFURL, nil),
              let properties = CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [CFString: Any],
              let width = properties[kCGImagePropertyPixelWidth] as? Double,
              let height = properties[kCGImagePropertyPixelHeight] as? Double
        else { return nil }
        // EXIF-Ausrichtungen 5–8 sind um 90° gedreht.
        let orientation = properties[kCGImagePropertyOrientation] as? Int ?? 1
        return (5...8).contains(orientation)
            ? CGSize(width: height, height: width)
            : CGSize(width: width, height: height)
    }

    /// Lädt das Foto verkleinert auf höchstens `maxPixelSize` an der langen Seite.
    static func downsampledImage(at url: URL, maxPixelSize: CGFloat) -> CGImage? {
        let sourceOptions = [kCGImageSourceShouldCache: false] as CFDictionary
        guard let source = CGImageSourceCreateWithURL(url as CFURL, sourceOptions) else { return nil }
        let options: [CFString: Any] = [
            kCGImageSourceCreateThumbnailFromImageAlways: true,
            kCGImageSourceCreateThumbnailWithTransform: true,
            kCGImageSourceShouldCacheImmediately: true,
            kCGImageSourceThumbnailMaxPixelSize: max(1, Int(maxPixelSize.rounded(.up))),
        ]
        return CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary)
    }

    /// Verkleinert und JPEG-komprimiert ein Foto.
    static func jpegData(from url: URL, maxPixelSize: CGFloat, quality: CGFloat) -> Data? {
        guard let image = downsampledImage(at: url, maxPixelSize: maxPixelSize) else { return nil }
        let data = NSMutableData()
        guard let destination = CGImageDestinationCreateWithData(
            data, UTType.jpeg.identifier as CFString, 1, nil
        ) else { return nil }
        let options = [kCGImageDestinationLossyCompressionQuality: quality] as CFDictionary
        CGImageDestinationAddImage(destination, image, options)
        return CGImageDestinationFinalize(destination) ? data as Data : nil
    }

    /// Benötigte Pixel an der langen Seite, damit das Foto in `placement` mit `dpi` scharf ist.
    /// Nie mehr, als das Original hergibt.
    static func targetLongSide(pixelSize: CGSize, placement: Placement, dpi: CGFloat) -> CGFloat {
        let longSidePoints = max(placement.rect.width, placement.rect.height)
        let wanted = longSidePoints / 72 * dpi
        return min(wanted, max(pixelSize.width, pixelSize.height))
    }
}
