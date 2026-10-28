import SwiftUI

/// Leiste mit allen ausgewählten Fotos in PDF-Reihenfolge.
struct PhotoStripView: View {
    @Environment(ProjectViewModel.self) private var project

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            LazyHStack(spacing: 8) {
                ForEach(Array(project.photos.enumerated()), id: \.element.id) { index, photo in
                    Image(uiImage: photo.thumbnail)
                        .resizable()
                        .scaledToFill()
                        .frame(width: 64, height: 64)
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                        .overlay(alignment: .topLeading) {
                            Text("\(index + 1)")
                                .font(.caption2.bold())
                                .padding(.horizontal, 5)
                                .padding(.vertical, 2)
                                .background(.ultraThinMaterial, in: Capsule())
                                .padding(3)
                        }
                        .contextMenu {
                            Button("Entfernen", systemImage: "trash", role: .destructive) {
                                project.remove(photo)
                            }
                        }
                }
            }
            .padding(.vertical, 4)
        }
        .frame(height: 76)
    }
}

/// Fotos per Ziehen umsortieren oder entfernen.
struct ReorderView: View {
    @Environment(ProjectViewModel.self) private var project
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            List {
                ForEach(Array(project.photos.enumerated()), id: \.element.id) { index, photo in
                    HStack(spacing: 12) {
                        Image(uiImage: photo.thumbnail)
                            .resizable()
                            .scaledToFill()
                            .frame(width: 56, height: 56)
                            .clipShape(RoundedRectangle(cornerRadius: 6))
                        Text("Foto \(index + 1)")
                        Spacer()
                        Text("Seite \(index / project.settings.photosPerPage + 1)")
                            .foregroundStyle(.secondary)
                    }
                }
                .onMove { project.move(from: $0, to: $1) }
                .onDelete { project.remove(at: $0) }
            }
            .environment(\.editMode, .constant(.active))
            .navigationTitle("Reihenfolge")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Fertig") { dismiss() }
                }
            }
        }
    }
}
