import Foundation

/// Plant die Aufteilung in mehrere PDFs, damit keines größer als 20 MB wird.
enum PDFSplitter {
    /// Harte Obergrenze pro PDF (20 MB, dezimal gezählt wie in „Dateien“ und Mail).
    static let maxFileSize = 20_000_000
    /// Planungsgröße mit Sicherheitsabstand für PDF-Verwaltungsdaten.
    static let targetPartSize = 18_500_000

    /// Zusammenhängende Seitenbereiche, keiner größer als `cap` Byte.
    static func greedyParts(_ pageSizes: [Int], cap: Int) -> [Range<Int>] {
        var parts: [Range<Int>] = []
        var start = 0
        var sum = 0
        for (index, size) in pageSizes.enumerated() {
            if sum + size > cap && index > start {
                parts.append(start..<index)
                start = index
                sum = 0
            }
            sum += size
        }
        if start < pageSizes.count {
            parts.append(start..<pageSizes.count)
        }
        return parts
    }

    /// So wenige Teile wie nötig, dabei möglichst gleich groß.
    static func balancedParts(_ pageSizes: [Int], limit: Int = targetPartSize) -> [Range<Int>] {
        let count = greedyParts(pageSizes, cap: limit).count
        var low = pageSizes.max() ?? 0
        var high = limit
        // Kleinste Obergrenze suchen, die mit `count` Teilen auskommt.
        while low < high {
            let mid = (low + high) / 2
            if greedyParts(pageSizes, cap: mid).count <= count {
                high = mid
            } else {
                low = mid + 1
            }
        }
        return greedyParts(pageSizes, cap: low)
    }
}
