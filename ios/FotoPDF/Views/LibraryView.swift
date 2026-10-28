import PDFKit
import SwiftUI

/// „Meine PDFs“: früher erstellte PDFs ansehen, umbenennen, senden, sichern, löschen.
struct LibraryView: View {
    @Environment(PDFLibrary.self) private var library
    @AppStorage("mailRoute") private var mailRoute = MailRoute.otherApp

    @State private var renaming: LibraryFile?
    @State private var newName = ""
    @State private var saving: LibraryFile?
    @State private var sendRequest: SendRequest?
    @State private var errorMessage: String?

    var body: some View {
        List {
            ForEach(library.files) { file in
                NavigationLink {
                    PDFPreviewView(url: file.url)
                } label: {
                    row(for: file)
                }
                .swipeActions(edge: .trailing) {
                    Button("Löschen", systemImage: "trash", role: .destructive) {
                        library.delete(file)
                    }
                    Button("Umbenennen", systemImage: "pencil") {
                        startRenaming(file)
                    }
                    .tint(.orange)
                }
                .contextMenu {
                    Button("Umbenennen", systemImage: "pencil") { startRenaming(file) }
                    Button("Per Mail senden", systemImage: "envelope") {
                        sendRequest = SendRequest(urls: [file.url], preferredRoute: mailRoute)
                    }
                    Button("In „Dateien“ sichern", systemImage: "folder") { saving = file }
                    Divider()
                    Button("Löschen", systemImage: "trash", role: .destructive) { library.delete(file) }
                }
            }
        }
        .overlay {
            if library.files.isEmpty {
                ContentUnavailableView("Noch keine PDFs",
                                       systemImage: "doc.richtext",
                                       description: Text("Erstellte PDFs erscheinen hier."))
            }
        }
        .navigationTitle("Meine PDFs")
        .onAppear { library.reload() }
        .refreshable { library.reload() }
        .pdfSending($sendRequest)
        .sheet(item: $saving) { file in
            SaveToFilesView(files: [file.url]) { saving = nil }
                .ignoresSafeArea()
        }
        .alert("Umbenennen", isPresented: Binding(
            get: { renaming != nil },
            set: { if !$0 { renaming = nil } }
        )) {
            TextField("Name", text: $newName)
            Button("Abbrechen", role: .cancel) {}
            Button("Speichern") { commitRename() }
        } message: {
            Text("Neuer Name für das PDF")
        }
        .alert("Fehler", isPresented: Binding(
            get: { errorMessage != nil },
            set: { if !$0 { errorMessage = nil } }
        )) {
            Button("OK") {}
        } message: {
            Text(errorMessage ?? "")
        }
    }

    private func row(for file: LibraryFile) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(file.name)
                .lineLimit(2)
            Text("\(file.byteCount.formattedBytes) · \(file.modified.formatted(date: .abbreviated, time: .shortened))")
                .font(.caption)
                .foregroundStyle(.secondary)
        }
    }

    private func startRenaming(_ file: LibraryFile) {
        newName = file.name
        renaming = file
    }

    private func commitRename() {
        guard let file = renaming else { return }
        do {
            try library.rename(file, to: newName)
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

struct PDFPreviewView: View {
    let url: URL

    var body: some View {
        PDFKitView(url: url)
            .ignoresSafeArea(edges: .bottom)
            .navigationTitle(url.deletingPathExtension().lastPathComponent)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ShareLink(item: url)
            }
    }
}

private struct PDFKitView: UIViewRepresentable {
    let url: URL

    func makeUIView(context: Context) -> PDFView {
        let view = PDFView()
        view.autoScales = true
        view.document = PDFDocument(url: url)
        return view
    }

    func updateUIView(_ view: PDFView, context: Context) {
        if view.document?.documentURL != url {
            view.document = PDFDocument(url: url)
        }
    }
}
