import SwiftUI

@main
struct FotoPDFApp: App {
    @State private var project = ProjectViewModel()
    @State private var library = PDFLibrary()

    var body: some Scene {
        WindowGroup {
            EditorView()
                .environment(project)
                .environment(library)
        }
    }
}
