import SwiftUI

/// Blättert durch die Seiten des entstehenden PDFs.
struct PagePreviewPager: View {
    @Environment(ProjectViewModel.self) private var project
    @State private var page = 0

    var body: some View {
        let settings = project.settings
        let pageCount = max(project.pageCount, 1)

        TabView(selection: $page) {
            ForEach(0..<pageCount, id: \.self) { index in
                PagePreview(photos: photos(onPage: index), settings: settings)
                    .padding(.horizontal, 24)
                    .padding(.top, 8)
                    .padding(.bottom, 40)
                    .tag(index)
            }
        }
        .tabViewStyle(.page(indexDisplayMode: pageCount > 1 ? .always : .never))
        .indexViewStyle(.page(backgroundDisplayMode: .always))
        .frame(height: settings.orientation == .portrait ? 440 : 320)
        .onChange(of: pageCount) { _, newCount in
            if page >= newCount { page = newCount - 1 }
        }
    }

    private func photos(onPage page: Int) -> [SelectedPhoto] {
        let perPage = project.settings.photosPerPage
        let start = page * perPage
        guard start < project.photos.count else { return [] }
        return Array(project.photos[start..<min(start + perPage, project.photos.count)])
    }
}

/// Eine Seite, genauso aufgebaut wie im PDF (gleiche Layout-Berechnung).
struct PagePreview: View {
    let photos: [SelectedPhoto]
    let settings: LayoutSettings

    var body: some View {
        let pageSize = settings.pageSize
        let cells = GridLayout.cellRects(for: settings)

        GeometryReader { proxy in
            let scale = min(proxy.size.width / pageSize.width, proxy.size.height / pageSize.height)

            ZStack(alignment: .topLeading) {
                Rectangle().fill(.white)
                ForEach(Array(cells.enumerated()), id: \.offset) { index, cell in
                    if index < photos.count {
                        photoView(photos[index], cell: cell, scale: scale)
                    } else {
                        Rectangle()
                            .strokeBorder(.gray.opacity(0.3), style: StrokeStyle(lineWidth: 1, dash: [4]))
                            .frame(width: cell.width * scale, height: cell.height * scale)
                            .offset(x: cell.minX * scale, y: cell.minY * scale)
                    }
                }
            }
            .frame(width: pageSize.width * scale, height: pageSize.height * scale)
            .clipped()
            .shadow(color: .black.opacity(0.25), radius: 4, y: 1)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }

    private func photoView(_ photo: SelectedPhoto, cell: CGRect, scale: CGFloat) -> some View {
        let placement = GridLayout.placement(for: photo.pixelSize, in: cell, settings: settings)
        let rect = placement.rect
        // Gedrehte Fotos werden mit vertauschten Seiten gezeichnet und dann um 90° gedreht.
        return Image(uiImage: photo.thumbnail)
            .resizable()
            .frame(width: (placement.rotated ? rect.height : rect.width) * scale,
                   height: (placement.rotated ? rect.width : rect.height) * scale)
            .rotationEffect(.degrees(placement.rotated ? 90 : 0))
            .frame(width: cell.width * scale, height: cell.height * scale)
            .clipped()
            .offset(x: cell.minX * scale, y: cell.minY * scale)
    }
}
