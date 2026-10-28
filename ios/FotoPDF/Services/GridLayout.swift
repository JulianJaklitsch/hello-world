import CoreGraphics

/// Wo ein Foto auf der Seite landet.
struct Placement {
    /// Fläche auf der Seite, die das (ggf. gedrehte) Foto einnimmt.
    /// Bei „Füllen“ kann sie über die Zelle hinausragen und wird dann abgeschnitten.
    let rect: CGRect
    /// Foto wird um 90° gedreht gezeichnet.
    let rotated: Bool
}

enum GridLayout {
    /// Rechtecke aller Zellen einer Seite, zeilenweise von links oben.
    static func cellRects(for settings: LayoutSettings) -> [CGRect] {
        let content = CGRect(origin: .zero, size: settings.pageSize)
            .insetBy(dx: settings.margin, dy: settings.margin)
        let columns = CGFloat(settings.columns)
        let rows = CGFloat(settings.rows)
        let width = max(1, (content.width - (columns - 1) * settings.spacing) / columns)
        let height = max(1, (content.height - (rows - 1) * settings.spacing) / rows)
        return (0..<settings.rows).flatMap { row in
            (0..<settings.columns).map { column in
                CGRect(x: content.minX + CGFloat(column) * (width + settings.spacing),
                       y: content.minY + CGFloat(row) * (height + settings.spacing),
                       width: width, height: height)
            }
        }
    }

    static func placement(for imageSize: CGSize, in cell: CGRect, settings: LayoutSettings) -> Placement {
        let rotated = shouldRotate(imageSize, in: cell, settings: settings)
        let size = rotated ? CGSize(width: imageSize.height, height: imageSize.width) : imageSize
        return Placement(rect: imageRect(for: size, in: cell, mode: settings.fitMode), rotated: rotated)
    }

    /// Foto proportional in die Zelle einpassen oder sie damit füllen, zentriert.
    static func imageRect(for size: CGSize, in cell: CGRect, mode: FitMode) -> CGRect {
        guard size.width > 0, size.height > 0 else { return cell }
        let scaleX = cell.width / size.width
        let scaleY = cell.height / size.height
        let scale = mode == .fit ? min(scaleX, scaleY) : max(scaleX, scaleY)
        let width = size.width * scale
        let height = size.height * scale
        return CGRect(x: cell.midX - width / 2, y: cell.midY - height / 2, width: width, height: height)
    }

    /// Quer-Fotos in Hoch-Zellen drehen (und umgekehrt), wenn gewünscht.
    private static func shouldRotate(_ imageSize: CGSize, in cell: CGRect, settings: LayoutSettings) -> Bool {
        guard settings.autoRotate,
              imageSize.width != imageSize.height,
              cell.width != cell.height else { return false }
        return (imageSize.width > imageSize.height) != (cell.width > cell.height)
    }
}
