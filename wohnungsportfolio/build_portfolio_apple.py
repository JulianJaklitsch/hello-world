#!/usr/bin/env python3
"""Wohnungsportfolio Lea Rager – Apple-Designprinzipien, aber warm und freundlich.

Klarheit, viel Weißraum, klare Hierarchie und das Foto als Hauptdarsteller; dazu warme Pastell-
Kacheln („Bento“) statt App-Listen. Nutzt die Engine aus build_portfolio.py.

Persönliche Daten (Telefon, E-Mail, Foto …) stehen NICHT im Repo, sondern in privat/daten.json
(per .gitignore ausgeschlossen). Ohne --privat entsteht eine Version mit Platzhaltern.

    python3 build_portfolio_apple.py --fonts DIR             # Platzhalter-Version
    python3 build_portfolio_apple.py --fonts DIR --privat    # mit privat/daten.json, Ausgabe in privat/
"""
import argparse
import json
import os

import build_portfolio as bp
from build_portfolio import line, oval, rect, text

HERE = os.path.dirname(os.path.abspath(__file__))

# Platzhalter – werden von privat/daten.json überschrieben
DATEN = {
    "telefon": None,
    "email": None,
    "foto": None,
    "alter": None,
    "netto": None,
    "arbeitgeber": None,
}

TINTS = {  # Kachelfarbe (hell) und passende dunkle Schriftfarbe
    "Apricot": ((252, 229, 214), (180, 87, 58)),
    "Salbei": ((227, 236, 220), (88, 116, 74)),
    "Himmel": ((221, 233, 244), (61, 106, 146)),
    "Lavendel": ((233, 227, 243), (103, 89, 154)),
    "Rose": ((248, 223, 227), (161, 78, 94)),
    "Sand": ((242, 234, 219), (134, 104, 58)),
}

bp.COLORS.clear()
bp.COLORS.update({
    "Hintergrund": ("Hintergrund", (251, 248, 244)),
    "Text": ("Text", (43, 37, 34)),
    "Grau": ("Grau", (117, 105, 95)),
    "Akzent": ("Akzent Terrakotta", (201, 96, 63)),
    "AkzentHell": ("Akzent hell", (248, 222, 210)),
    "Weiss": ("Weiß", (255, 255, 255)),
    "Karte": ("Karte", (243, 237, 229)),
    "FotoPlatz": ("Foto Platzhalter", (239, 230, 220)),
})
for t, (light, dark) in TINTS.items():
    bp.COLORS[t] = (t, light)
    bp.COLORS[t + "Dunkel"] = (t + " dunkel", dark)

# family, style, size, leading, color, align, tracking, caps, space_after
S = {
    "Eyebrow": ("Inter", "SemiBold", 9, 12, "Akzent", "LeftAlign", 10, False, 0),
    "Gruss": ("Inter", "Medium", 15, 19, "Akzent", "LeftAlign", -10, False, 0),
    "Name": ("Inter", "Bold", 38, 42, "Text", "LeftAlign", -25, False, 0),
    "Untertitel": ("Inter", "Regular", 11.5, 16.5, "Grau", "LeftAlign", -5, False, 0),
    "Sektion": ("Inter", "Bold", 17, 21, "Text", "LeftAlign", -15, False, 0),
    "Fliesstext": ("Inter", "Regular", 10.5, 16.5, "Text", "LeftAlign", 0, False, 0),
    "KachelWert": ("Inter", "Bold", 18, 21, "Text", "LeftAlign", -20, False, 0),
    "KontaktSatz": ("Inter", "SemiBold", 14, 18, "Weiss", "LeftAlign", -10, False, 0),
    "KontaktLabel": ("Inter", "Medium", 8, 10, "AkzentHell", "LeftAlign", 0, False, 0.3),
    "KontaktWert": ("Inter", "SemiBold", 11, 14, "Weiss", "LeftAlign", 0, False, 1.8),
    "Fusszeile": ("Inter", "Regular", 7.5, 10, "Grau", "CenterAlign", 0, False, 0),
    "FotoHinweis": ("Inter", "Medium", 8.5, 12, "Grau", "CenterAlign", 0, False, 0),
    "Titel": ("Inter", "Bold", 32, 36, "Text", "LeftAlign", -25, False, 0),
    "Intro": ("Inter", "Regular", 12, 17.5, "Grau", "LeftAlign", -5, False, 0),
    "DokTitel": ("Inter", "Bold", 14, 17, "Text", "LeftAlign", -15, False, 1),
    "DokText": ("Inter", "Regular", 9.5, 13, "Grau", "LeftAlign", 0, False, 0),
    "DankeTitel": ("Inter", "Bold", 20, 24, "Weiss", "LeftAlign", -20, False, 1.2),
    "DankeText": ("Inter", "Regular", 9.5, 13, "AkzentHell", "LeftAlign", 0, False, 0),
    "Frage": ("Inter", "SemiBold", 12, 16, "Text", "LeftAlign", -10, False, 0),
    "KontaktRechts": ("Inter", "Medium", 10.5, 15, "Text", "RightAlign", 0, False, 0),
}
for t in TINTS:
    S["Pill" + t] = ("Inter", "Medium", 9, 11, t + "Dunkel", "CenterAlign", 0, False, 0)
    S["KachelLabel" + t] = ("Inter", "SemiBold", 8.5, 11, t + "Dunkel", "LeftAlign", 0, False, 0)
    S["DokStatus" + t] = ("Inter", "SemiBold", 8, 10, t + "Dunkel", "RightAlign", 0, False, 0)
bp.PARA_STYLES.clear()
bp.PARA_STYLES.update(S)
bp.CHAR_STYLES.clear()
bp.CHAR_STYLES.update({"Platzhalter": (None, "Akzent")})

L, W = 18, 174
R = 7            # großer Radius für Foto und Kacheln (weich, freundlich)


def wert(value, platzhalter):
    """Echter Wert oder sichtbarer Platzhalter in Akzentfarbe."""
    return value if value else [(platzhalter, "Platzhalter")]


def background():
    return [rect(-bp.BLEED, -bp.BLEED, bp.PAGE_W + 2 * bp.BLEED, bp.PAGE_H + 2 * bp.BLEED,
                 "Hintergrund", name="Hintergrund")]


def pill(x, y, w, label, tint):
    h = 8.5
    return [rect(x, y, w, h, tint, radius=h / 2, name=f"Pille {label}"),
            text(x, y, w, h, [("Pill" + tint, label)], valign="CenterAlign", name=f"Pille Text {label}")]


def tile(x, y, w, h, tint, label, value):
    return [rect(x, y, w, h, tint, radius=R, name=f"Kachel {label}"),
            text(x + 5, y + 4.5, w - 10, 6, [("KachelLabel" + tint, label)], name=f"Kachel Label {label}"),
            text(x + 5, y + h - 13, w - 10, 9, [("KachelWert", value)], valign="BottomAlign",
                 name=f"Kachel Wert {label}")]


def check_badge(x, y, tint):
    d = 8
    cx, cy = x + d / 2, y + d / 2
    return [oval(x, y, d, d, fill="Weiss", name="Haken Kreis"),
            line([(cx - 1.7, cy + 0.1), (cx - 0.5, cy + 1.3), (cx + 1.8, cy - 1.2)], tint + "Dunkel", 1.2,
                 name="Haken")]


def page_profile(d):
    items = background()

    # Foto (Hauptdarsteller)
    items += [
        rect(L, 18, 80, 100, "FotoPlatz", radius=R, name="Foto Hintergrund"),
        text(L + 10, 62, 60, 12, [("FotoHinweis", "Foto hier platzieren"),
                                  ("FotoHinweis", "Datei › Platzieren")], valign="CenterAlign", name="Foto Hinweis"),
        rect(L, 18, 80, 100, None, radius=R, photo=True, image=d["foto"], name="Foto"),
    ]

    # Begrüßung
    X, CW = 106, 86
    items += [
        text(X, 22, CW, 5, [("Eyebrow", "Wohnungsbewerbung")], name="Eyebrow"),
        text(X, 36, CW, 7, [("Gruss", "Hallo, ich bin")], name="Gruß"),
        text(X, 43, CW, 15, [("Name", "Lea Rager")], name="Name"),
        text(X, 61, CW, 26, [("Untertitel", "Krabbelstubenpädagogin mit viel Herz."),
                             ("Untertitel", "Auf der Suche nach einem Zuhause in Wien.")],
             name="Untertitel"),
    ]
    items += pill(X, 86, 33, "Nichtraucherin", "Salbei")
    items += pill(X + 36, 86, 35, "Keine Haustiere", "Himmel")
    items += pill(X, 97, 36, "Ziehe allein ein", "Apricot")

    # Über mich
    items += [
        text(L, 130, W, 8, [("Sektion", "Über mich")], valign="BottomAlign", name="Sektion Über mich"),
        text(L, 141, W, 31, [("Fliesstext",
            "Ich bin Lea und arbeite seit zweieinhalb Jahren mit viel Freude als Krabbelstubenpädagogin. "
            "Für meinen nächsten Lebensabschnitt suche ich eine 2-Zimmer-Wohnung in Wien, in der ich mich "
            "so richtig zuhause fühlen kann. Ich bin zuverlässig und ordentlich, gehe sorgsam mit meinem "
            "Zuhause um, und ein freundliches, respektvolles Miteinander in der Nachbarschaft ist mir "
            "wichtig. Ich würde mich sehr freuen, Sie persönlich kennenzulernen!")], name="Text Über mich"),
    ]

    # Auf einen Blick (Bento-Kacheln)
    items.append(text(L, 176, W, 8, [("Sektion", "Auf einen Blick")], valign="BottomAlign",
                      name="Sektion Auf einen Blick"))
    gap, th = 5, 27
    tw = (W - 2 * gap) / 3
    tiles = [
        ("Apricot", "Berufserfahrung", "2,5 Jahre"),
        ("Salbei", "Wohnungswunsch", "2 Zimmer"),
        ("Himmel", "Einzug · flexibel", "ab 2027"),
        ("Lavendel", "Netto-Einkommen", wert(d["netto"], "[€ / Monat]")),
        ("Rose", "Alter", wert(d["alter"], "[Alter]")),
        ("Sand", "Arbeitgeber in Wien", wert(d["arbeitgeber"], "[folgt]")),
    ]
    for i, (tint, label, value) in enumerate(tiles):
        items += tile(L + (i % 3) * (tw + gap), 187 + (i // 3) * (th + gap), tw, th, tint, label, value)

    # Kontakt
    y = 252
    items += [
        rect(L, y, W, 26, "Akzent", radius=R, name="Kontakt Fläche"),
        text(L + 8, y, 80, 26, [("KontaktSatz", "Ich freue mich,"), ("KontaktSatz", "von Ihnen zu hören!")],
             valign="CenterAlign", name="Kontakt Satz"),
        text(L + 100, y, 70, 26, [
            ("KontaktLabel", "Telefon"), ("KontaktWert", wert(d["telefon"], "[Telefonnummer]")),
            ("KontaktLabel", "E-Mail"), ("KontaktWert", wert(d["email"], "[E-Mail-Adresse]")),
        ], valign="CenterAlign", name="Kontakt Daten"),
        text(L, 284, W, 5, [("Fusszeile", "Meine Unterlagen finden Sie auf den folgenden Seiten.")],
             name="Fußzeile"),
    ]
    return items


def page_documents(d):
    items = background()
    items += [
        text(L, 22, W, 5, [("Eyebrow", "Wohnungsbewerbung · Lea Rager")], name="Eyebrow"),
        text(L, 32, W, 13, [("Titel", "Meine Unterlagen")], name="Titel"),
        text(L, 48, 150, 14, [("Intro",
            "Damit Sie sich ein vollständiges Bild machen können, finden Sie alle wichtigen "
            "Unterlagen auf den folgenden Seiten.")], name="Intro"),
    ]
    docs = [
        ("Apricot", "Gehaltszettel", "Lohn- bzw. Gehaltsabrechnungen der letzten drei Monate", "beiliegend"),
        ("Salbei", "Arbeitsbestätigung", "Bestätigung über das aufrechte Dienstverhältnis", "beiliegend"),
        ("Himmel", "Lichtbildausweis", "Kopie von Reisepass oder Personalausweis", "beiliegend"),
        ("Lavendel", "Meldezettel", "Aktuelle Meldebestätigung", "beiliegend"),
        ("Rose", "KSV-Auskunft", "Bonitätsauskunft des KSV1870", "optional"),
    ]
    gap, th = 6, 40
    tw = (W - gap) / 2
    for i, (tint, title, desc, status) in enumerate(docs):
        x, y = L + (i % 2) * (tw + gap), 72 + (i // 2) * (th + gap)
        items += [rect(x, y, tw, th, tint, radius=R, name=f"Kachel {title}")]
        items += check_badge(x + 6, y + 6, tint)
        items += [
            text(x + tw - 46, y + 7, 40, 6, [("DokStatus" + tint, status)], name=f"Status {title}"),
            text(x + 6, y + 18, tw - 12, 18, [("DokTitel", title), ("DokText", desc)], name=f"Text {title}"),
        ]
    x, y = L + tw + gap, 72 + 2 * (th + gap)
    items += [
        rect(x, y, tw, th, "Akzent", radius=R, name="Kachel Danke"),
        text(x + 6, y + 6, tw - 12, th - 12, [("DankeTitel", "Danke!"), ("DankeText",
            "Bitte behandeln Sie meine Unterlagen vertraulich. Ich freue mich auf Ihre Rückmeldung.")],
            valign="BottomAlign", name="Text Danke"),
    ]

    y = 216
    items += [
        rect(L, y, W, 24, "Karte", radius=R, name="Kontakt Fläche"),
        text(L + 7, y, 90, 24, [("Frage", "Fragen? Ich bin gerne"), ("Frage", "für Sie erreichbar.")],
             valign="CenterAlign", name="Kontakt Satz"),
        text(L + W - 7 - 80, y, 80, 24, [("KontaktRechts", wert(d["telefon"], "[Telefonnummer]")),
                                         ("KontaktRechts", wert(d["email"], "[E-Mail-Adresse]"))],
             valign="CenterAlign", name="Kontakt Daten"),
        text(L, 284, W, 5, [("Fusszeile", "Lea Rager · Wohnungsbewerbung")], name="Fußzeile"),
    ]
    return items


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", help="Ordner mit Inter-*.ttf für die PDF-Vorschau")
    ap.add_argument("--privat", action="store_true", help="privat/daten.json einsetzen, Ausgabe nach privat/")
    a = ap.parse_args()

    daten, out = dict(DATEN), HERE
    if a.privat:
        out = os.path.join(HERE, "privat")
        with open(os.path.join(out, "daten.json"), encoding="utf-8") as fh:
            daten.update(json.load(fh))
        if daten.get("foto"):
            daten["foto"] = os.path.join(out, daten["foto"])

    bp.PAGES[:] = [page_profile(daten), page_documents(daten)]
    bp.IdmlWriter().write(os.path.join(out, "Wohnungsportfolio_Lea_Rager_Apple.idml"))
    if a.fonts:
        pdf = "Wohnungsportfolio_Lea_Rager_Apple.pdf" if a.privat else "Wohnungsportfolio_Lea_Rager_Apple_Vorschau.pdf"
        bp.render_pdf(os.path.join(out, pdf), a.fonts)
