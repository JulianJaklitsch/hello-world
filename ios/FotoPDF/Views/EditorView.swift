import PhotosUI
import SwiftUI

/// Hauptbildschirm: Fotos auswählen, Vorschau, Layout einstellen.
struct EditorView: View {
    @Environment(ProjectViewModel.self) private var project
    @State private var pickerItems: [PhotosPickerItem] = []
    @State private var showExport = false
    @State private var showReorder = false
    @State private var confirmRemoveAll = false

    var body: some View {
        @Bindable var project = project

        NavigationStack {
            Group {
                if project.photos.isEmpty && !project.isImporting {
                    emptyState
                } else {
                    Form {
                        Section {
                            PagePreviewPager()
                        } footer: {
                            Text(summary)
                        }

                        Section("Fotos") {
                            PhotoStripView()
                            Button("Reihenfolge ändern", systemImage: "arrow.up.arrow.down") {
                                showReorder = true
                            }
                            Button("Alle entfernen", systemImage: "trash", role: .destructive) {
                                confirmRemoveAll = true
                            }
                        }

                        LayoutControlsView(settings: $project.settings)
                    }
                }
            }
            .navigationTitle("FotoPDF")
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    NavigationLink {
                        LibraryView()
                    } label: {
                        Label("Meine PDFs", systemImage: "folder")
                    }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    photosPicker {
                        Label("Fotos hinzufügen", systemImage: "plus")
                    }
                }
            }
            .safeAreaInset(edge: .bottom) {
                if !project.photos.isEmpty {
                    Button {
                        showExport = true
                    } label: {
                        Text("PDF erstellen")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    .disabled(project.isImporting)
                    .padding()
                    .background(.bar)
                }
            }
            .overlay {
                if project.isImporting {
                    importProgress
                }
            }
            .onChange(of: pickerItems) { _, items in
                guard !items.isEmpty else { return }
                pickerItems = []
                Task { await project.importItems(items) }
            }
            .onChange(of: project.settings) { _, _ in
                project.saveSettings()
            }
            .sheet(isPresented: $showExport) {
                ExportView()
            }
            .sheet(isPresented: $showReorder) {
                ReorderView()
            }
            .confirmationDialog("Alle Fotos entfernen?", isPresented: $confirmRemoveAll, titleVisibility: .visible) {
                Button("Alle entfernen", role: .destructive) { project.removeAll() }
            }
            .alert("Hinweis", isPresented: Binding(
                get: { project.importMessage != nil },
                set: { if !$0 { project.importMessage = nil } }
            )) {
                Button("OK") {}
            } message: {
                Text(project.importMessage ?? "")
            }
        }
    }

    private var summary: String {
        let photos = project.photos.count == 1 ? "1 Foto" : "\(project.photos.count) Fotos"
        let pages = project.pageCount == 1 ? "1 Seite" : "\(project.pageCount) Seiten"
        return "\(photos) → \(pages) · \(project.settings.photosPerPage) pro Seite"
    }

    private var emptyState: some View {
        ContentUnavailableView {
            Label("Keine Fotos ausgewählt", systemImage: "photo.on.rectangle.angled")
        } description: {
            Text("Wähle Fotos aus deiner Galerie. Sie werden zu einem A4-PDF zusammengestellt – standardmäßig 4 Fotos pro Seite (2×2).")
        } actions: {
            photosPicker {
                Text("Fotos auswählen")
            }
            .buttonStyle(.borderedProminent)
        }
    }

    private var importProgress: some View {
        VStack(spacing: 12) {
            ProgressView(value: Double(project.importedCount), total: Double(max(project.importTotal, 1)))
            Text("Fotos werden geladen … \(project.importedCount) von \(project.importTotal)")
                .font(.footnote)
        }
        .padding()
        .frame(maxWidth: 280)
        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16))
    }

    private func photosPicker<Content: View>(@ViewBuilder label: () -> Content) -> some View {
        PhotosPicker(selection: $pickerItems,
                     selectionBehavior: .ordered,
                     matching: .images,
                     preferredItemEncoding: .current,
                     label: label)
    }
}
