import MessageUI
import SwiftUI
import UIKit

/// Ein Sende-Auftrag: ein oder mehrere PDFs per Mail bzw. Teilen-Menü.
struct SendRequest: Identifiable {
    let id = UUID()
    let urls: [URL]
    let subject: String
    let route: MailRoute

    /// Fällt auf das Teilen-Menü zurück, wenn in Apple Mail kein Konto eingerichtet ist.
    init(urls: [URL], preferredRoute: MailRoute) {
        self.urls = urls
        subject = urls.first?.deletingPathExtension().lastPathComponent ?? "FotoPDF"
        route = preferredRoute == .appleMail && MailView.canSend ? .appleMail : .otherApp
    }
}

extension View {
    /// Zeigt für einen Sende-Auftrag das Mail-Fenster oder das Teilen-Menü (z. B. für Outlook).
    func pdfSending(_ request: Binding<SendRequest?>, onSent: @escaping ([URL]) -> Void = { _ in }) -> some View {
        sheet(item: request) { current in
            switch current.route {
            case .appleMail:
                MailView(subject: current.subject, attachments: current.urls) { result in
                    if result == .sent { onSent(current.urls) }
                    request.wrappedValue = nil
                }
                .ignoresSafeArea()
            case .otherApp:
                ActivityView(items: current.urls.map { PDFShareItem(url: $0, subject: current.subject) }) { completed in
                    if completed { onSent(current.urls) }
                    request.wrappedValue = nil
                }
                .presentationDetents([.medium, .large])
                .ignoresSafeArea()
            }
        }
    }
}

/// Mail-Fenster direkt in der App (Apple Mail).
struct MailView: UIViewControllerRepresentable {
    let subject: String
    let attachments: [URL]
    let onFinish: (MFMailComposeResult) -> Void

    static var canSend: Bool { MFMailComposeViewController.canSendMail() }

    func makeUIViewController(context: Context) -> MFMailComposeViewController {
        let mail = MFMailComposeViewController()
        mail.mailComposeDelegate = context.coordinator
        mail.setSubject(subject)
        for url in attachments {
            if let data = try? Data(contentsOf: url) {
                mail.addAttachmentData(data, mimeType: "application/pdf", fileName: url.lastPathComponent)
            }
        }
        return mail
    }

    func updateUIViewController(_ controller: MFMailComposeViewController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(onFinish: onFinish)
    }

    final class Coordinator: NSObject, MFMailComposeViewControllerDelegate {
        let onFinish: (MFMailComposeResult) -> Void

        init(onFinish: @escaping (MFMailComposeResult) -> Void) {
            self.onFinish = onFinish
        }

        func mailComposeController(_ controller: MFMailComposeViewController,
                                   didFinishWith result: MFMailComposeResult, error: Error?) {
            onFinish(result)
        }
    }
}

/// Das iOS-Teilen-Menü (Outlook, Gmail, AirDrop, Drucken …).
struct ActivityView: UIViewControllerRepresentable {
    let items: [Any]
    let onComplete: (Bool) -> Void

    func makeUIViewController(context: Context) -> UIActivityViewController {
        let controller = UIActivityViewController(activityItems: items, applicationActivities: nil)
        controller.completionWithItemsHandler = { _, completed, _, _ in
            onComplete(completed)
        }
        return controller
    }

    func updateUIViewController(_ controller: UIActivityViewController, context: Context) {}
}

/// PDF-Datei fürs Teilen-Menü, mit Betreff für Mail-Apps.
final class PDFShareItem: NSObject, UIActivityItemSource {
    let url: URL
    let subject: String

    init(url: URL, subject: String) {
        self.url = url
        self.subject = subject
    }

    func activityViewControllerPlaceholderItem(_ controller: UIActivityViewController) -> Any {
        url
    }

    func activityViewController(_ controller: UIActivityViewController,
                                itemForActivityType activityType: UIActivity.ActivityType?) -> Any? {
        url
    }

    func activityViewController(_ controller: UIActivityViewController,
                                subjectForActivityType activityType: UIActivity.ActivityType?) -> String {
        subject
    }
}

/// System-Ordnerauswahl zum Sichern in „Dateien“ (iCloud Drive, Auf meinem iPhone, OneDrive …).
struct SaveToFilesView: UIViewControllerRepresentable {
    let files: [URL]
    let onDismiss: () -> Void

    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let picker = UIDocumentPickerViewController(forExporting: files, asCopy: true)
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ controller: UIDocumentPickerViewController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(onDismiss: onDismiss)
    }

    final class Coordinator: NSObject, UIDocumentPickerDelegate {
        let onDismiss: () -> Void

        init(onDismiss: @escaping () -> Void) {
            self.onDismiss = onDismiss
        }

        func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
            onDismiss()
        }

        func documentPickerWasCancelled(_ controller: UIDocumentPickerViewController) {
            onDismiss()
        }
    }
}
