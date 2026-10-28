import Foundation

/// Womit PDFs per Mail verschickt werden.
enum MailRoute: String, CaseIterable, Identifiable {
    /// Über das Teilen-Menü, z. B. an Outlook oder Gmail.
    case otherApp
    /// Über das eingebaute Mail-Fenster (Apple Mail).
    case appleMail

    var id: Self { self }

    var title: String {
        switch self {
        case .otherApp: "Outlook / andere App"
        case .appleMail: "Apple Mail"
        }
    }
}
