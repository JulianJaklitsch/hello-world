import UIKit

struct PhotoInput {
    let fileURL: URL
    let pixelSize: CGSize
}

enum PDFComposerError: LocalizedError {
    case noPhotos
    case compressionFailed(photo: Int)
    case pageTooLarge(page: Int)

    var errorDescription: String? {
        switch self {
        case .noPhotos:
            "Es sind keine Fotos ausgewählt."
        case .compressionFailed(let photo):
            "Foto \(photo) konnte nicht gelesen werden."
        case .pageTooLarge(let page):
            "Seite \(page) ist selbst nach starker Kompression größer als 20 MB."
        }
    }
}

/// Erstellt die PDFs: erst komprimieren, dann schreiben, Größe messen und bei Bedarf aufteilen.
struct PDFComposer {
    typealias Progress = (_ fraction: Double, _ message: String) -> Void

    let photos: [PhotoInput]
    let settings: LayoutSettings
    /// Dokumenttitel in den PDF-Metadaten.
    let title: String

    /// Geschätzter Platzbedarf einer Seite ohne Fotos.
    private static let pageOverhead = 3_000

    private struct CompressedPhoto {
        let url: URL
        let byteCount: Int
        let cell: CGRect
        let placement: Placement
    }

    /// Gibt die fertigen Teile in Seitenreihenfolge zurück (temporäre Dateien, jede ≤ 20 MB).
    func run(progress: Progress) throws -> [URL] {
        guard !photos.isEmpty else { throw PDFComposerError.noPhotos }

        let fileManager = FileManager.default
        let work = try WorkDirectory.newJobDirectory()
        defer { try? fileManager.removeItem(at: work) }
        let output = try WorkDirectory.newJobDirectory()

        let cells = GridLayout.cellRects(for: settings)
        let pageCount = settings.pageCount(forPhotoCount: photos.count)

        // 1. Komprimieren
        var compressed: [CompressedPhoto] = []
        for index in photos.indices {
            progress(0.8 * Double(index) / Double(photos.count),
                     "Komprimiere Foto \(index + 1) von \(photos.count) …")
            compressed.append(try compress(index, cell: cells[index % cells.count], strength: 1, into: work))
        }

        // 2. Seitengrößen schätzen (die JPEGs werden unverändert eingebettet)
        var pageSizes = (0..<pageCount).map { page in
            photoIndices(onPage: page).reduce(Self.pageOverhead) { $0 + compressed[$1].byteCount }
        }

        // 3. Schreiben, messen und bei Bedarf weiter aufteilen
        var pending = PDFSplitter.balancedParts(pageSizes)
        var finished: [URL] = []
        var finishedPages = 0
        var shrinkAttempts: [Int: Int] = [:]

        while !pending.isEmpty {
            let pages = pending.removeFirst()
            progress(0.8 + 0.2 * Double(finishedPages) / Double(pageCount), "Erstelle PDF …")

            let url = output.appendingPathComponent("Teil-\(UUID().uuidString).pdf")
            try render(pages: pages, compressed: compressed, to: url)
            let size = try fileSize(of: url)

            if size <= PDFSplitter.maxFileSize {
                finished.append(url)
                finishedPages += pages.count
                continue
            }
            try fileManager.removeItem(at: url)

            if pages.count > 1 {
                // Schätzung war zu niedrig: an die echte Größe anpassen und diesen Teil neu aufteilen.
                let estimate = pages.reduce(0) { $0 + pageSizes[$1] }
                let factor = Double(size) / Double(max(estimate, 1)) * 1.05
                for page in pages {
                    pageSizes[page] = Int(Double(pageSizes[page]) * factor)
                }
                var subParts = PDFSplitter.balancedParts(Array(pageSizes[pages])).map {
                    ($0.lowerBound + pages.lowerBound)..<($0.upperBound + pages.lowerBound)
                }
                if subParts.count < 2 {
                    let middle = pages.lowerBound + pages.count / 2
                    subParts = [pages.lowerBound..<middle, middle..<pages.upperBound]
                }
                pending.insert(contentsOf: subParts, at: 0)
            } else {
                // Eine einzelne Seite ist zu groß: nur ihre Fotos stärker komprimieren.
                let page = pages.lowerBound
                let attempt = (shrinkAttempts[page] ?? 0) + 1
                guard attempt <= 4 else { throw PDFComposerError.pageTooLarge(page: page + 1) }
                shrinkAttempts[page] = attempt
                let strength = pow(0.7, Double(attempt))
                for index in photoIndices(onPage: page) {
                    compressed[index] = try compress(index, cell: cells[index % cells.count],
                                                     strength: strength, into: work)
                }
                pending.insert(pages, at: 0)
            }
        }

        progress(1, "Fertig")
        return finished
    }

    // MARK: - Schritte

    private func photoIndices(onPage page: Int) -> Range<Int> {
        let start = page * settings.photosPerPage
        return start..<min(start + settings.photosPerPage, photos.count)
    }

    /// `strength` < 1 verringert Auflösung und JPEG-Qualität zusätzlich.
    private func compress(_ index: Int, cell: CGRect, strength: Double, into directory: URL) throws -> CompressedPhoto {
        let photo = photos[index]
        let placement = GridLayout.placement(for: photo.pixelSize, in: cell, settings: settings)
        let longSide = ImageCompressor.targetLongSide(pixelSize: photo.pixelSize, placement: placement,
                                                      dpi: settings.compression.dpi) * CGFloat(strength)
        let quality = max(0.3, settings.compression.jpegQuality * CGFloat(strength))

        guard let data = ImageCompressor.jpegData(from: photo.fileURL, maxPixelSize: longSide, quality: quality)
        else { throw PDFComposerError.compressionFailed(photo: index + 1) }

        let url = directory.appendingPathComponent("\(index).jpg")
        try data.write(to: url, options: .atomic)
        return CompressedPhoto(url: url, byteCount: data.count, cell: cell, placement: placement)
    }

    private func render(pages: Range<Int>, compressed: [CompressedPhoto], to url: URL) throws {
        let format = UIGraphicsPDFRendererFormat()
        format.documentInfo = [
            kCGPDFContextTitle as String: title,
            kCGPDFContextCreator as String: "FotoPDF",
        ]
        let renderer = UIGraphicsPDFRenderer(bounds: CGRect(origin: .zero, size: settings.pageSize), format: format)
        try renderer.writePDF(to: url) { context in
            for page in pages {
                context.beginPage()
                for index in photoIndices(onPage: page) {
                    autoreleasepool {
                        draw(compressed[index], in: context.cgContext)
                    }
                }
            }
        }
    }

    private func draw(_ photo: CompressedPhoto, in context: CGContext) {
        // Aus JPEG-Daten erzeugte Bilder bettet Quartz in der Regel unverändert ein.
        guard let provider = CGDataProvider(url: photo.url as CFURL),
              let cgImage = CGImage(jpegDataProviderSource: provider, decode: nil,
                                    shouldInterpolate: true, intent: .defaultIntent)
        else { return }
        let image = UIImage(cgImage: cgImage)
        let rect = photo.placement.rect

        context.saveGState()
        context.clip(to: photo.cell)
        if photo.placement.rotated {
            context.translateBy(x: rect.midX, y: rect.midY)
            context.rotate(by: .pi / 2)
            image.draw(in: CGRect(x: -rect.height / 2, y: -rect.width / 2, width: rect.height, height: rect.width))
        } else {
            image.draw(in: rect)
        }
        context.restoreGState()
    }

    private func fileSize(of url: URL) throws -> Int {
        try FileManager.default.attributesOfItem(atPath: url.path)[.size] as? Int ?? 0
    }
}
