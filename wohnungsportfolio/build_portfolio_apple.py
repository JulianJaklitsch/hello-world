#!/usr/bin/env python3
"""Wohnungsportfolio Lea Rager – Variante im Apple-Stil (iOS-Einstellungen / apple.com).

Nutzt die Engine aus build_portfolio.py und ersetzt nur Farben, Stile und Seiten.

    python3 build_portfolio_apple.py --fonts DIR   # IDML + PDF-Vorschau (Inter-*.ttf in DIR)
"""
import argparse
import os

import build_portfolio as bp
from build_portfolio import line, oval, rect, text

bp.COLORS.clear()
bp.COLORS.update({
    "Hintergrund": ("Hintergrund", (245, 245, 247)),
    "Weiss": ("Weiß", (255, 255, 255)),
    "Text": ("Text", (29, 29, 31)),
    "Grau": ("Grau", (110, 110, 115)),
    "GrauHell": ("Grau hell", (134, 134, 139)),
    "FotoGrau": ("Foto Platzhalter", (232, 232, 237)),
    "Trenner": ("Trennlinie", (229, 229, 234)),
    "Link": ("Link-Blau", (0, 113, 227)),
    # iOS-Systemfarben für die Symbole
    "Blau": ("System Blau", (0, 122, 255)),
    "Gruen": ("System Grün", (52, 199, 89)),
    "Orange": ("System Orange", (255, 149, 0)),
    "Rot": ("System Rot", (255, 59, 48)),
    "Indigo": ("System Indigo", (88, 86, 214)),
    "Pink": ("System Pink", (255, 45, 85)),
    "Teal": ("System Teal", (48, 176, 199)),
})

# family, style, size, leading, color, align, tracking, caps, space_after
bp.PARA_STYLES.clear()
bp.PARA_STYLES.update({
    "Eyebrow": ("Inter", "SemiBold", 9, 12, "GrauHell", "CenterAlign", 0, False, 0),
    "EyebrowLinks": ("Inter", "SemiBold", 9, 12, "GrauHell", "LeftAlign", 0, False, 0),
    "Name": ("Inter", "Bold", 40, 44, "Text", "CenterAlign", -25, False, 0),
    "Untertitel": ("Inter", "Medium", 14, 19, "Grau", "CenterAlign", -10, False, 0),
    "Titel": ("Inter", "Bold", 32, 36, "Text", "LeftAlign", -25, False, 0),
    "Intro": ("Inter", "Medium", 12, 17, "Grau", "LeftAlign", -5, False, 0),
    "Sektion": ("Inter", "Bold", 15, 19, "Text", "LeftAlign", -10, False, 0),
    "Fliesstext": ("Inter", "Regular", 10, 15, "Text", "LeftAlign", 0, False, 0),
    "Zeile": ("Inter", "Regular", 10.5, 13, "Text", "LeftAlign", 0, False, 0),
    "ZeileWert": ("Inter", "Regular", 10.5, 13, "Grau", "RightAlign", 0, False, 0),
    "ZeileTitel": ("Inter", "SemiBold", 10.5, 13, "Text", "LeftAlign", 0, False, 0.6),
    "ZeileText": ("Inter", "Regular", 8.5, 11, "Grau", "LeftAlign", 0, False, 0),
    "Abschluss": ("Inter", "SemiBold", 12, 16, "Text", "CenterAlign", -5, False, 0),
    "Fusszeile": ("Inter", "Regular", 7.5, 10, "GrauHell", "CenterAlign", 0, False, 0),
    "FotoHinweis": ("Inter", "Medium", 8, 11, "GrauHell", "CenterAlign", 0, False, 0),
})
bp.CHAR_STYLES.clear()
bp.CHAR_STYLES.update({
    "Platzhalter": (None, "Link"),
    "Fett": ("SemiBold", None),
})

L, W = 18, 174           # Satzspiegel
ROW = 10                 # Zeilenhöhe in Listen (≈ 28 pt, wie iOS)
ICON = 6.5               # Symbolgröße
RADIUS = 4               # Kartenradius


# ---------------------------------------------------------------- Symbole (weiß auf iOS-Farbe)
def icon(kind, x, y, color):
    s = ICON
    items = [rect(x, y, s, s, color, radius=s * 0.23, name=f"Symbol {kind}")]
    cx, cy = x + s / 2, y + s / 2
    sw = 1.1
    if kind == "person":
        items += [oval(cx - 0.14 * s, y + 0.18 * s, 0.28 * s, 0.28 * s, fill="Weiss"),
                  rect(cx - 0.25 * s, y + 0.54 * s, 0.5 * s, 0.26 * s, "Weiss", radius=0.12 * s)]
    elif kind == "uhr":
        items += [oval(cx - 0.3 * s, cy - 0.3 * s, 0.6 * s, 0.6 * s, stroke="Weiss", sw=sw),
                  line([(cx, cy - 0.17 * s), (cx, cy), (cx + 0.14 * s, cy + 0.08 * s)], "Weiss", sw)]
    elif kind == "ort":
        items += [line([(cx, cy + 0.02 * s), (cx, y + 0.82 * s)], "Weiss", 1.4),
                  oval(cx - 0.21 * s, y + 0.16 * s, 0.42 * s, 0.42 * s, fill="Weiss"),
                  oval(cx - 0.08 * s, y + 0.29 * s, 0.16 * s, 0.16 * s, fill=color)]
    elif kind == "rauchfrei":
        d = 0.3 * s * 0.7071
        items += [oval(cx - 0.3 * s, cy - 0.3 * s, 0.6 * s, 0.6 * s, stroke="Weiss", sw=sw),
                  line([(cx - d, cy - d), (cx + d, cy + d)], "Weiss", sw)]
    elif kind == "pfote":
        items += [oval(cx - 0.17 * s, y + 0.5 * s, 0.34 * s, 0.28 * s, fill="Weiss")]
        for dx, dy in ((-0.27, 0.36), (-0.1, 0.2), (0.1, 0.2), (0.27, 0.36)):
            items.append(oval(cx + dx * s - 0.065 * s, y + dy * s, 0.13 * s, 0.15 * s, fill="Weiss"))
    elif kind == "kalender":
        items += [rect(cx - 0.28 * s, y + 0.22 * s, 0.56 * s, 0.56 * s, None, radius=0.08 * s,
                       stroke="Weiss", sw=sw),
                  rect(cx - 0.28 * s, y + 0.22 * s, 0.56 * s, 0.14 * s, "Weiss"),
                  oval(cx - 0.05 * s, y + 0.52 * s, 0.1 * s, 0.1 * s, fill="Weiss")]
    elif kind == "telefon":
        items += [rect(cx - 0.17 * s, y + 0.18 * s, 0.34 * s, 0.64 * s, None, radius=0.07 * s,
                       stroke="Weiss", sw=sw),
                  line([(cx - 0.05 * s, y + 0.7 * s), (cx + 0.05 * s, y + 0.7 * s)], "Weiss", sw)]
    elif kind == "mail":
        items += [rect(cx - 0.3 * s, y + 0.28 * s, 0.6 * s, 0.44 * s, None, radius=0.06 * s,
                       stroke="Weiss", sw=sw),
                  line([(cx - 0.27 * s, y + 0.32 * s), (cx, y + 0.52 * s), (cx + 0.27 * s, y + 0.32 * s)],
                       "Weiss", sw)]
    elif kind == "dokument":
        items += [rect(cx - 0.23 * s, y + 0.18 * s, 0.46 * s, 0.64 * s, None, radius=0.06 * s,
                       stroke="Weiss", sw=sw)]
        for i in range(3):
            yy = y + (0.38 + 0.13 * i) * s
            items.append(line([(cx - 0.11 * s, yy), (cx + (0.11 if i < 2 else 0.02) * s, yy)], "Weiss", 0.9))
    return items


def section(y, title):
    return text(L + 1, y, W, 7, [("Sektion", title)], valign="BottomAlign", name=f"Sektion {title}")


def grouped_list(y, rows, row_h=ROW, name="Liste"):
    """iOS-„Inset Grouped“-Liste. rows: (Symbol, Farbe, Links, Rechts) – Links/Rechts als Absatzliste."""
    items = [rect(L, y, W, row_h * len(rows), "Weiss", radius=RADIUS, name=name)]
    for i, (ic, color, left, right) in enumerate(rows):
        ry = y + i * row_h
        items += icon(ic, L + 4, ry + (row_h - ICON) / 2, color)
        items.append(text(L + 14, ry, 110, row_h, left, valign="CenterAlign", name=f"{name} Zeile {i + 1}"))
        if right:
            items.append(text(L + W - 4 - 60, ry, 60, row_h, right, valign="CenterAlign",
                              name=f"{name} Wert {i + 1}"))
        if i < len(rows) - 1:
            items.append(line([(L + 14, ry + row_h), (L + W, ry + row_h)], "Trenner", 0.5, name="Trennlinie"))
    return items


def background():
    return [rect(-bp.BLEED, -bp.BLEED, bp.PAGE_W + 2 * bp.BLEED, bp.PAGE_H + 2 * bp.BLEED,
                 "Hintergrund", name="Hintergrund")]


PLATZ_TEL = ("[Telefonnummer]", "Platzhalter")
PLATZ_MAIL = ("[E-Mail-Adresse]", "Platzhalter")


def contact_rows():
    return [
        ("telefon", "Gruen", [("Zeile", "Telefon")], [("ZeileWert", [PLATZ_TEL])]),
        ("mail", "Blau", [("Zeile", "E-Mail")], [("ZeileWert", [PLATZ_MAIL])]),
    ]


def page_profile():
    items = background()
    items.append(text(L, 15, W, 5, [("Eyebrow", "Wohnungsbewerbung")], name="Eyebrow"))

    d, px = 46, 105 - 23
    items += [
        oval(px, 25, d, d, fill="FotoGrau", name="Foto Hintergrund"),
        text(px + 5, 25 + d / 2 - 6, d - 10, 12, [("FotoHinweis", "Foto hier platzieren"),
                                                  ("FotoHinweis", "Datei › Platzieren")],
             valign="CenterAlign", name="Foto Hinweis"),
        oval(px, 25, d, d, stroke="Weiss", sw=3, photo=True, name="Foto"),
    ]
    items.append(text(L, 76, W, 16, [("Name", "Lea Rager")], valign="CenterAlign", name="Name"))
    items.append(text(L, 94, W, 9, [("Untertitel",
        "Pädagogin. Auf der Suche nach einem neuen Zuhause in Wien.")], valign="CenterAlign", name="Untertitel"))

    items.append(section(108, "Über mich"))
    items += [
        rect(L, 117, W, 38, "Weiss", radius=RADIUS, name="Karte Über mich"),
        text(L + 6, 122, W - 12, 28, [("Fliesstext",
            "Ich bin Lea, arbeite seit zweieinhalb Jahren mit viel Freude als Pädagogin und suche nun eine "
            "Wohnung in Wien, in der ich mich so richtig zuhause fühlen kann. Ich bin ein zuverlässiger und "
            "ordentlicher Mensch, gehe sorgsam mit meinem Zuhause um und schätze ein freundliches, "
            "respektvolles Miteinander in der Nachbarschaft. Ich würde mich sehr freuen, Sie persönlich "
            "kennenzulernen!")], valign="CenterAlign", name="Text Über mich"),
    ]

    items.append(section(162, "Auf einen Blick"))
    items += grouped_list(171, [
        ("person", "Blau", [("Zeile", "Beruf")], [("ZeileWert", "Pädagogin")]),
        ("uhr", "Indigo", [("Zeile", "Im Beruf seit")], [("ZeileWert", "2,5 Jahren")]),
        ("ort", "Rot", [("Zeile", "Gesuchter Wohnort")], [("ZeileWert", "Wien")]),
        ("rauchfrei", "Orange", [("Zeile", "Rauchen")], [("ZeileWert", "Nichtraucherin")]),
        ("pfote", "Teal", [("Zeile", "Haustiere")], [("ZeileWert", "Keine")]),
        ("kalender", "Pink", [("Zeile", "Einzug ab")], [("ZeileWert", [("[Datum]", "Platzhalter")])]),
    ], name="Auf einen Blick")

    items.append(section(236, "Kontakt"))
    items += grouped_list(245, contact_rows(), name="Kontakt")
    items.append(text(L, 270, W, 8, [("Abschluss", "Ich freue mich, von Ihnen zu hören.")],
                      valign="CenterAlign", name="Abschluss"))
    items.append(text(L, 283, W, 5, [("Fusszeile",
        "Meine Unterlagen (Gehaltszettel u. a.) finden Sie auf den folgenden Seiten.")], name="Fußzeile"))
    return items


def page_documents():
    items = background()
    items.append(text(L, 15, W, 5, [("EyebrowLinks", "Wohnungsbewerbung · Lea Rager")], name="Eyebrow"))
    items.append(text(L, 26, W, 14, [("Titel", "Meine Unterlagen.")], name="Titel"))
    items.append(text(L, 42, 150, 14, [("Intro",
        "Damit Sie sich ein vollständiges Bild machen können, finden Sie alle wichtigen "
        "Unterlagen auf den folgenden Seiten.")], name="Intro"))

    def doc(color, title, sub, status):
        return ("dokument", color, [("ZeileTitel", title), ("ZeileText", sub)], [("ZeileWert", status)])

    items.append(section(62, "Übersicht"))
    items += grouped_list(71, [
        doc("Blau", "Gehaltszettel", "Lohn- bzw. Gehaltsabrechnungen der letzten drei Monate", "Beiliegend"),
        doc("Indigo", "Arbeitsbestätigung", "Bestätigung über das aufrechte Dienstverhältnis", "Beiliegend"),
        doc("Gruen", "Lichtbildausweis", "Kopie von Reisepass oder Personalausweis", "Beiliegend"),
        doc("Orange", "Meldezettel", "Aktuelle Meldebestätigung", "Beiliegend"),
        doc("Pink", "KSV-Auskunft", "Bonitätsauskunft des KSV1870", "Optional"),
    ], row_h=15, name="Unterlagen")

    items.append(section(154, "Datenschutz"))
    items += [
        rect(L, 163, W, 16, "Weiss", radius=RADIUS, name="Karte Datenschutz"),
        text(L + 6, 163, W - 12, 16, [("Fliesstext",
            "Bitte behandeln Sie meine Unterlagen vertraulich. Vielen Dank für Ihr Vertrauen!")],
            valign="CenterAlign", name="Text Datenschutz"),
    ]
    items.append(section(186, "Kontakt"))
    items += grouped_list(195, contact_rows(), name="Kontakt")
    items.append(text(L, 283, W, 5, [("Fusszeile", "Lea Rager · Wohnungsbewerbung")], name="Fußzeile"))
    return items


bp.PAGES[:] = [page_profile(), page_documents()]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", help="Ordner mit Inter-*.ttf für die PDF-Vorschau")
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()
    bp.IdmlWriter().write(os.path.join(a.out, "Wohnungsportfolio_Lea_Rager_Apple.idml"))
    if a.fonts:
        bp.render_pdf(os.path.join(a.out, "Wohnungsportfolio_Lea_Rager_Apple_Vorschau.pdf"), a.fonts)
