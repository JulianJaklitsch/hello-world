import SwiftUI

/// PDF benennen, erstellen und danach sichern bzw. per Mail senden.
struct ExportView: View {
    @Environment(ProjectViewModel.self) private var project
    @Environment(PDFLibrary.self) private var library
    @Environment(\.dismiss) private var dismiss
    @AppStorage("mailRoute") private var mailRoute = MailRoute.otherApp

    @State private var name = ""
    @State private var phase = Phase.naming
    @State private var progress = 0.0
    @State private var progressMessage = ""
    @State private var files: [URL] = []
    @State private var sentFiles: Set<URL> = []
    @State private var sendRequest: SendRequest?
    @State private var showSaveToFiles = false
    @State private var errorMessage: String?
    @FocusState private var nameFocused: Bool

    private enum Phase { case naming, working, done }

    private let defaultName = FileNaming.defaultBaseName()

    var body: some View {
        NavigationStack {
            Form {
                switch phase {
                case .naming: namingContent
                case .working: workingContent
                case .done: doneContent
                }
            }
            .navigationTitle(phase == .done ? "PDF fertig" : "PDF erstellen")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(phase == .done ? "Fertig" : "Abbrechen") { dismiss() }
                        .disabled(phase == .working)
                }
            }
            .interactiveDismissDisabled(phase == .working)
            .onAppear { nameFocused = true }
            .pdfSending($sendRequest) { urls in
                sentFiles.formUnion(urls)
            }
            .sheet(isPresented: $showSaveToFiles) {
                SaveToFilesView(files: files) { showSaveToFiles = false }
                    .ignoresSafeArea()
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
    }

    // MARK: - Schritt 1: Namen vergeben

    @ViewBuilder
    private var namingContent: some View {
        Section("Name des PDFs") {
            HStack(spacing: 4) {
                TextField(defaultName, text: $name)
                    .focused($nameFocused)
                    .submitLabel(.done)
                    .onSubmit(create)
                Text(".pdf")
                    .foregroundStyle(.secondary)
            }
        }

        Section {
            LabeledContent("Fotos", value: "\(project.photos.count)")
            LabeledContent("Seiten", value: "\(project.pageCount)")
            LabeledContent("Kompression", value: project.settings.compression.title)
            LabeledContent("Geschätzte Größe", value: estimateText)
        } footer: {
            Text("Erst wird komprimiert, dann die Größe geprüft. Jedes PDF ist höchstens 20 MB groß; wird es größer, teilt die App es automatisch in mehrere Teile auf.")
        }

        Section {
            Button(action: create) {
                Text("PDF erstellen")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            .listRowBackground(Color.clear)
            .listRowInsets(EdgeInsets())
        }
    }

    private var estimateText: String {
        let bytes = project.estimatedBytes
        let parts = max(1, Int((Double(bytes) / Double(PDFSplitter.targetPartSize)).rounded(.up)))
        let size = "ca. \(bytes.formattedBytes)"
        return parts == 1 ? "\(size) · 1 PDF" : "\(size) · \(parts) PDFs"
    }

    // MARK: - Schritt 2: Erstellen

    private var workingContent: some View {
        Section {
            VStack(spacing: 12) {
                ProgressView(value: progress)
                Text(progressMessage)
                    .font(.footnote)
                    .foregroundStyle(.secondary)
            }
            .padding(.vertical)
        }
    }

    private func create() {
        guard phase == .naming, !project.photos.isEmpty else { return }
        let baseName = FileNaming.sanitized(name, fallback: defaultName)
        let composer = PDFComposer(
            photos: project.photos.map { PhotoInput(fileURL: $0.fileURL, pixelSize: $0.pixelSize) },
            settings: project.settings,
            title: baseName
        )
        phase = .working
        progress = 0
        progressMessage = "Starte …"

        Task { @MainActor in
            do {
                let parts = try await Task.detached(priority: .userInitiated) {
                    try composer.run { fraction, message in
                        Task { @MainActor in
                            progress = fraction
                            progressMessage = message
                        }
                    }
                }.value
                files = try library.store(parts: parts, baseName: baseName)
                phase = .done
            } catch {
                errorMessage = error.localizedDescription
                phase = .naming
            }
        }
    }

    // MARK: - Schritt 3: Sichern und senden

    @ViewBuilder
    private var doneContent: some View {
        Section {
            ForEach(files, id: \.self) { url in
                HStack(spacing: 12) {
                    Image(systemName: "doc.richtext")
                        .font(.title2)
                        .foregroundStyle(.tint)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(url.lastPathComponent)
                            .lineLimit(2)
                        Text(fileSize(of: url).formattedBytes)
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                    Spacer()
                    if files.count > 1 {
                        Button {
                            send([url])
                        } label: {
                            Image(systemName: sentFiles.contains(url) ? "checkmark.circle.fill" : "envelope")
                                .font(.title3)
                        }
                        .buttonStyle(.borderless)
                        .accessibilityLabel("Diesen Teil per Mail senden")
                    }
                }
            }
        } header: {
            Text(files.count == 1 ? "Erstellt" : "Erstellt – \(files.count) Teile")
        } footer: {
            if files.count > 1 {
                Text("Jeder Teil ist höchstens 20 MB groß und wird als eigene Mail verschickt, damit der Mail-Anbieter ihn annimmt.")
            }
        }

        Section {
            Button {
                showSaveToFiles = true
            } label: {
                Label("In „Dateien“ sichern", systemImage: "folder")
            }

            if files.count == 1 {
                Button {
                    send(files)
                } label: {
                    Label(sentFiles.isEmpty ? "Per Mail senden" : "Erneut per Mail senden", systemImage: "envelope")
                }
            } else if let next = files.first(where: { !sentFiles.contains($0) }), let index = files.firstIndex(of: next) {
                Button {
                    send([next])
                } label: {
                    Label("Teil \(index + 1) von \(files.count) per Mail senden", systemImage: "envelope")
                }
            } else {
                Label("Alle Teile gesendet", systemImage: "checkmark.circle.fill")
                    .foregroundStyle(.secondary)
            }

            ShareLink(items: files) {
                Label("Weitere …", systemImage: "square.and.arrow.up")
            }
        }

        Section {
            Picker("Mail senden mit", selection: $mailRoute) {
                ForEach(MailRoute.allCases) { Text($0.title).tag($0) }
            }
        } footer: {
            Text("Die PDFs liegen außerdem unter „Meine PDFs“ und in der Dateien-App unter „Auf meinem iPhone › FotoPDF“.")
        }
    }

    private func send(_ urls: [URL]) {
        sendRequest = SendRequest(urls: urls, preferredRoute: mailRoute)
    }

    private func fileSize(of url: URL) -> Int {
        (try? url.resourceValues(forKeys: [.fileSizeKey]).fileSize) ?? 0
    }
}

extension Int {
    /// z. B. „12,3 MB“ (dezimal gezählt, wie in der Dateien-App).
    var formattedBytes: String {
        ByteCountFormatter.string(fromByteCount: Int64(self), countStyle: .file)
    }
}
