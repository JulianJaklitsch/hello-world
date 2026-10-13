#!/usr/bin/env python3
"""Wohnungsportfolio Lea Rager – erzeugt eine InDesign-Datei (IDML) und ein Vorschau-PDF.

Beide Ausgaben entstehen aus demselben Layout-Modell (alle Maße in mm, Ursprung oben links).

    python3 build_portfolio.py                 # nur IDML
    python3 build_portfolio.py --fonts DIR     # zusätzlich PDF-Vorschau (Gelasio-*.ttf in DIR)
"""
import argparse
import os
import zipfile
from xml.sax.saxutils import escape

MM = 72 / 25.4
PAGE_W, PAGE_H = 210.0, 297.0
BLEED = 3.0

# ---------------------------------------------------------------- Farben (RGB)
COLORS = {
    "Creme": ("Creme", (251, 246, 240)),
    "Braun": ("Braun", (74, 62, 57)),
    "BraunHell": ("Braun hell", (128, 112, 104)),
    "Rose": ("Rosé", (233, 184, 168)),
    "RoseHell": ("Rosé hell", (246, 226, 218)),
    "RoseDunkel": ("Rosé dunkel", (184, 118, 102)),
    "Salbei": ("Salbei", (167, 186, 148)),
    "SalbeiHell": ("Salbei hell", (231, 236, 223)),
    "Linie": ("Linie", (236, 222, 213)),
    "Weiss": ("Weiß", (255, 255, 255)),
}

# ---------------------------------------------------------------- Stile
# family, style, size, leading, color, align, tracking, caps, space_after
PARA_STYLES = {
    "Label": ("Arial", "Bold", 7.5, 10, "RoseDunkel", "LeftAlign", 220, True, 0),
    "LabelMitte": ("Arial", "Bold", 7.5, 10, "BraunHell", "CenterAlign", 180, True, 0),
    "Gruss": ("Georgia", "Italic", 17, 22, "RoseDunkel", "LeftAlign", 0, False, 0),
    "Name": ("Georgia", "Regular", 40, 46, "Braun", "LeftAlign", -10, False, 6),
    "Untertitel": ("Arial", "Regular", 10.5, 15, "BraunHell", "LeftAlign", 10, False, 0),
    "Ueberschrift": ("Georgia", "Italic", 17, 21, "Braun", "LeftAlign", 0, False, 0),
    "Titel": ("Georgia", "Regular", 32, 38, "Braun", "LeftAlign", -10, False, 0),
    "Fliesstext": ("Arial", "Regular", 10.5, 16, "Braun", "LeftAlign", 0, False, 0),
    "KarteLabel": ("Arial", "Bold", 6.5, 9, "RoseDunkel", "LeftAlign", 160, True, 1.5),
    "KarteWert": ("Georgia", "Regular", 12.5, 15, "Braun", "LeftAlign", 0, False, 0),
    "ListeTitel": ("Georgia", "Regular", 13, 16, "Braun", "LeftAlign", 0, False, 1),
    "ListeText": ("Arial", "Regular", 8.5, 11.5, "BraunHell", "LeftAlign", 0, False, 0),
    "Abschluss": ("Georgia", "Italic", 15, 19, "Braun", "LeftAlign", 0, False, 2),
    "Kontakt": ("Arial", "Regular", 9.5, 15, "Braun", "LeftAlign", 0, False, 0),
    "Fusszeile": ("Arial", "Regular", 7.5, 10, "BraunHell", "CenterAlign", 20, False, 0),
    "FotoHinweis": ("Arial", "Regular", 8, 11, "RoseDunkel", "CenterAlign", 60, False, 0),
}
# name -> (font style override or None, color or None)
CHAR_STYLES = {
    "Platzhalter": (None, "RoseDunkel"),
    "Fett": ("Bold", None),
}


# ---------------------------------------------------------------- Layout-Elemente
def rect(x, y, w, h, fill, radius=0, stroke=None, sw=0, name="", photo=False, image=None):
    """photo=True: leerer Grafikrahmen in InDesign; image: Bild nur für die PDF-Vorschau."""
    return dict(kind="rect", x=x, y=y, w=w, h=h, fill=fill, radius=radius, stroke=stroke, sw=sw, name=name,
                photo=photo, image=image)


def oval(x, y, w, h, fill=None, stroke=None, sw=0, photo=False, name=""):
    return dict(kind="oval", x=x, y=y, w=w, h=h, fill=fill, stroke=stroke, sw=sw, photo=photo, name=name)


def line(points, color, weight, name=""):
    return dict(kind="line", points=points, stroke=color, sw=weight, name=name)


def text(x, y, w, h, paras, valign="TopAlign", name=""):
    """paras: Liste von (Absatzstil, Text) oder (Absatzstil, [(Text, Zeichenstil|None), ...])."""
    norm = []
    for style, content in paras:
        runs = [(content, None)] if isinstance(content, str) else content
        norm.append((style, runs))
    return dict(kind="text", x=x, y=y, w=w, h=h, paras=norm, valign=valign, name=name)


def checkmark(cx, cy, s, color):
    return line([(cx - 0.45 * s, cy + 0.02 * s), (cx - 0.12 * s, cy + 0.32 * s), (cx + 0.45 * s, cy - 0.3 * s)],
                color, 1.4, name="Haken")


def background(mirror=False):
    items = [rect(-BLEED, -BLEED, PAGE_W + 2 * BLEED, PAGE_H + 2 * BLEED, "Creme", name="Hintergrund")]
    if not mirror:
        items += [
            oval(138, -42, 112, 112, fill="SalbeiHell", name="Deko Kreis groß"),
            oval(-32, 262, 70, 70, fill="RoseHell", name="Deko Kreis unten"),
            oval(178, 82, 8, 8, fill="Rose", name="Deko Punkt"),
            oval(184, 92, 4, 4, fill="Salbei", name="Deko Punkt klein"),
        ]
    else:
        items += [
            oval(-40, -40, 100, 100, fill="RoseHell", name="Deko Kreis groß"),
            oval(168, 248, 78, 78, fill="SalbeiHell", name="Deko Kreis unten"),
            oval(178, 34, 7, 7, fill="Salbei", name="Deko Punkt"),
            oval(186, 42, 3.5, 3.5, fill="Rose", name="Deko Punkt klein"),
        ]
    return items


def page_profile():
    items = background()
    L, W = 20, 170
    items.append(text(L, 18, 120, 6, [("Label", "Wohnungsbewerbung")], name="Label"))

    # Foto
    items += [
        oval(L, 32, 66, 66, fill="Rose", name="Foto Ring"),
        oval(L + 3, 35, 60, 60, fill="RoseHell", name="Foto Hintergrund"),
        text(L + 8, 59, 50, 12, [("FotoHinweis", "Foto hier platzieren"),
                                 ("FotoHinweis", "(Datei › Platzieren)")], valign="CenterAlign", name="Foto Hinweis"),
        oval(L + 3, 35, 60, 60, stroke="Weiss", sw=2.5, photo=True, name="Foto"),
    ]

    # Name
    items.append(text(96, 34, 96, 62, [
        ("Gruss", "Hallo, ich bin"),
        ("Name", "Lea Rager"),
        ("Untertitel", "Pädagogin  ·  auf der Suche nach einem"),
        ("Untertitel", "neuen Zuhause in Wien"),
    ], valign="CenterAlign", name="Name"))

    # Über mich
    y = 112
    items.append(text(L, y, W, 9, [("Ueberschrift", "Ein paar Worte über mich")], name="Überschrift Über mich"))
    items.append(line([(L, y + 10.5), (L + 14, y + 10.5)], "Rose", 1.5, name="Unterstrich"))
    items.append(text(L, y + 15, W, 40, [("Fliesstext",
        "Ich bin Lea, arbeite seit zweieinhalb Jahren mit viel Freude als Pädagogin und suche "
        "nun eine Wohnung in Wien, in der ich mich so richtig zuhause fühlen kann. Ich bin ein "
        "zuverlässiger und ordentlicher Mensch, gehe sorgsam mit meinem Zuhause um und schätze "
        "ein freundliches, respektvolles Miteinander in der Nachbarschaft. Ich würde mich sehr "
        "freuen, Sie persönlich kennenzulernen!")], name="Text Über mich"))

    # Auf einen Blick
    y = 166
    items.append(text(L, y, W, 9, [("Ueberschrift", "Auf einen Blick")], name="Überschrift Auf einen Blick"))
    items.append(line([(L, y + 10.5), (L + 14, y + 10.5)], "Rose", 1.5, name="Unterstrich"))
    facts = [
        ("Beruf", "Pädagogin"),
        ("Im Beruf seit", "2,5 Jahren"),
        ("Gesucht in", "Wien"),
        ("Rauchen", "Nichtraucherin"),
        ("Haustiere", "Keine"),
        ("Einzug ab", [("[Datum]", "Platzhalter")]),
    ]
    gap, cw, ch = 6, (W - 12) / 3, 24
    for i, (label, value) in enumerate(facts):
        cx = L + (i % 3) * (cw + gap)
        cy = y + 16 + (i // 3) * (ch + gap)
        dot = "SalbeiHell" if i % 2 == 0 else "RoseHell"
        items += [
            rect(cx, cy, cw, ch, "Weiss", radius=4, stroke="Linie", sw=0.6, name=f"Karte {label}"),
            oval(cx + 5, cy + ch / 2 - 4, 8, 8, fill=dot, name="Karte Punkt"),
            text(cx + 16, cy + 3, cw - 18, ch - 6, [("KarteLabel", label), ("KarteWert", value)],
                 valign="CenterAlign", name=f"Karte Text {label}"),
        ]

    # Kontakt
    y = 246
    items += [
        rect(L, y, W, 30, "SalbeiHell", radius=5, name="Kontakt Box"),
        text(L + 8, y + 4, 82, 22, [("Abschluss", "Ich freue mich auf"),
                                    ("Abschluss", "Ihre Nachricht!")], valign="CenterAlign", name="Abschluss"),
        text(L + 98, y + 4, 66, 22, [
            ("KarteLabel", "Kontakt"),
            ("Kontakt", [("Telefon  ", "Fett"), ("[+43 …]", "Platzhalter")]),
            ("Kontakt", [("E-Mail  ", "Fett"), ("[E-Mail-Adresse]", "Platzhalter")]),
        ], valign="CenterAlign", name="Kontakt"),
    ]
    items.append(text(L, 283, W, 5, [("Fusszeile",
        "Meine Unterlagen (Gehaltszettel u. a.) finden Sie auf den folgenden Seiten.")], name="Fußzeile"))
    return items


def page_documents():
    items = background(mirror=True)
    L, W = 20, 170
    items.append(text(L, 18, 150, 6, [("Label", "Wohnungsbewerbung  ·  Lea Rager")], name="Label"))
    items.append(text(L, 44, W, 16, [("Titel", "Meine Unterlagen")], name="Titel"))
    items.append(line([(L, 61), (L + 14, 61)], "Rose", 1.5, name="Unterstrich"))
    items.append(text(L, 68, 150, 20, [("Fliesstext",
        "Damit Sie sich ein vollständiges Bild machen können, habe ich die wichtigsten "
        "Unterlagen für Sie zusammengestellt. Sie finden sie auf den folgenden Seiten.")], name="Intro"))

    docs = [
        ("Gehaltszettel", "Lohn- bzw. Gehaltsabrechnungen der letzten drei Monate"),
        ("Arbeitsbestätigung", "Bestätigung meines Dienstgebers über das aufrechte Dienstverhältnis"),
        ("Lichtbildausweis", "Kopie von Reisepass oder Personalausweis"),
        ("Meldezettel", "Aktuelle Meldebestätigung"),
        ("KSV-Auskunft", "Bonitätsauskunft des KSV1870 (optional)"),
    ]
    y0, rh, gap = 96, 22, 6
    for i, (title, desc) in enumerate(docs):
        y = y0 + i * (rh + gap)
        circ = "Salbei" if i % 2 == 0 else "Rose"
        items += [
            rect(L, y, W, rh, "Weiss", radius=4, stroke="Linie", sw=0.6, name=f"Zeile {title}"),
            oval(L + 7, y + rh / 2 - 5, 10, 10, fill=circ, name="Haken Kreis"),
            checkmark(L + 12, y + rh / 2, 5.2, "Weiss"),
            text(L + 24, y + 3, W - 30, rh - 6, [("ListeTitel", title), ("ListeText", desc)],
                 valign="CenterAlign", name=f"Zeile Text {title}"),
        ]

    items.append(text(L, 246, W, 18, [
        ("Abschluss", "Vielen Dank für Ihr Vertrauen!"),
        ("Fliesstext", "Bitte behandeln Sie meine Unterlagen vertraulich."),
    ], name="Dank"))
    items.append(text(L, 283, W, 5, [("Fusszeile", [
        ("Lea Rager  ·  ", None), ("[+43 …]", "Platzhalter"), ("  ·  ", None),
        ("[E-Mail-Adresse]", "Platzhalter")])], name="Fußzeile"))
    return items


PAGES = [page_profile(), page_documents()]


# ================================================================ IDML
NS = 'xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="8.0"'
HEAD = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'


def f(v):
    return f"{v:.4f}".rstrip("0").rstrip(".")


def color_ref(name):
    return "Swatch/None" if name is None else f"Color/{name}"


def path_xml(points, open_path=False):
    """points: Liste von (anchor, left, right) in pt (Spread-Koordinaten)."""
    pts = "".join(
        f'<PathPointType Anchor="{f(a[0])} {f(a[1])}" LeftDirection="{f(l[0])} {f(l[1])}" '
        f'RightDirection="{f(r[0])} {f(r[1])}"/>' for a, l, r in points)
    return (f'<Properties><PathGeometry><GeometryPathType PathOpen="{str(open_path).lower()}">'
            f'<PathPointArray>{pts}</PathPointArray></GeometryPathType></PathGeometry></Properties>')


def rect_points(x, y, w, h):
    c = [(x, y), (x, y + h), (x + w, y + h), (x + w, y)]
    return [(p, p, p) for p in c]


def oval_points(x, y, w, h):
    k = 0.5522847498
    cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2, h / 2
    return [
        ((cx - rx, cy), (cx - rx, cy + k * ry), (cx - rx, cy - k * ry)),
        ((cx, cy - ry), (cx - k * rx, cy - ry), (cx + k * rx, cy - ry)),
        ((cx + rx, cy), (cx + rx, cy - k * ry), (cx + rx, cy + k * ry)),
        ((cx, cy + ry), (cx + k * rx, cy + ry), (cx - k * rx, cy + ry)),
    ]


FIT_XML = ('<FrameFittingOption AutoFit="true" FittingOnEmptyFrame="FillProportionally" '
           'FittingAlignment="CenterAnchor"/>')


class IdmlWriter:
    def __init__(self):
        self.n = 0
        self.stories = {}

    def uid(self, prefix="ui"):
        self.n += 1
        return f"{prefix}{self.n:x}"

    def item_xml(self, it, dy):
        """dy: Verschiebung Seite -> Spread (Seite liegt bei y = -H/2)."""
        def tp(x_mm, y_mm):
            return (x_mm * MM, y_mm * MM + dy)

        common = (f'ItemLayer="uL1" Locked="false" Visible="true" Name="{escape(it["name"] or "$ID/")}" '
                  f'ItemTransform="1 0 0 1 0 0" AppliedObjectStyle="ObjectStyle/$ID/[None]"')
        kind = it["kind"]
        if kind in ("rect", "oval", "text"):
            x0, y0 = tp(it["x"], it["y"])
            w, h = it["w"] * MM, it["h"] * MM
        if kind == "rect":
            corners = ""
            if it["radius"]:
                r = f(it["radius"] * MM)
                corners = "".join(f' {c}CornerOption="RoundedCorner" {c}CornerRadius="{r}"'
                                  for c in ("TopLeft", "TopRight", "BottomLeft", "BottomRight"))
            ct = "GraphicType" if it["photo"] else "Unassigned"
            return (f'<Rectangle Self="{self.uid()}" ContentType="{ct}" {common} '
                    f'FillColor="{color_ref(it["fill"])}" StrokeColor="{color_ref(it["stroke"])}" '
                    f'StrokeWeight="{f(it["sw"])}"{corners}>{path_xml(rect_points(x0, y0, w, h))}'
                    f'{FIT_XML if it["photo"] else ""}</Rectangle>')
        if kind == "oval":
            ct = "GraphicType" if it["photo"] else "Unassigned"
            fit = FIT_XML if it["photo"] else ""
            return (f'<Oval Self="{self.uid()}" ContentType="{ct}" {common} '
                    f'FillColor="{color_ref(it["fill"])}" StrokeColor="{color_ref(it["stroke"])}" '
                    f'StrokeWeight="{f(it["sw"])}" StrokeAlignment="InsideAlignment">'
                    f'{path_xml(oval_points(x0, y0, w, h))}{fit}</Oval>')
        if kind == "line":
            pts = [tp(*p) for p in it["points"]]
            tag = "GraphicLine" if len(pts) == 2 else "Polygon"
            return (f'<{tag} Self="{self.uid()}" ContentType="Unassigned" {common} FillColor="Swatch/None" '
                    f'StrokeColor="{color_ref(it["stroke"])}" StrokeWeight="{f(it["sw"])}" '
                    f'EndCap="RoundEndCap" EndJoin="RoundEndJoin">'
                    f'{path_xml([(p, p, p) for p in pts], open_path=True)}</{tag}>')
        if kind == "text":
            sid = self.uid("st")
            self.stories[sid] = self.story_xml(sid, it["paras"])
            return (f'<TextFrame Self="{self.uid()}" ParentStory="{sid}" PreviousTextFrame="n" NextTextFrame="n" '
                    f'ContentType="TextType" {common} FillColor="Swatch/None" StrokeColor="Swatch/None" '
                    f'StrokeWeight="0">{path_xml(rect_points(x0, y0, w, h))}'
                    f'<TextFramePreference TextColumnCount="1" VerticalJustification="{it["valign"]}" '
                    f'FirstBaselineOffset="AscentOffset" AutoSizingType="Off"/></TextFrame>')
        raise ValueError(kind)

    @staticmethod
    def story_xml(sid, paras):
        out = []
        for i, (pstyle, runs) in enumerate(paras):
            last = i == len(paras) - 1
            csr = []
            for j, (txt, cstyle) in enumerate(runs):
                cs = f"CharacterStyle/{cstyle}" if cstyle else "CharacterStyle/$ID/[No character style]"
                br = "" if (last or j < len(runs) - 1) else "<Br/>"
                csr.append(f'<CharacterStyleRange AppliedCharacterStyle="{cs}">'
                           f'<Content>{escape(txt)}</Content>{br}</CharacterStyleRange>')
            out.append(f'<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{pstyle}">'
                       + "".join(csr) + "</ParagraphStyleRange>")
        return (HEAD + f'<idPkg:Story {NS}><Story Self="{sid}" AppliedTOCStyle="n" TrackChanges="false" '
                f'StoryTitle="$ID/" AppliedNamedGrid="n"><StoryPreference OpticalMarginAlignment="false" '
                f'OpticalMarginSize="12" FrameType="TextFrameType" StoryOrientation="Horizontal" '
                f'StoryDirection="LeftToRightDirection"/>' + "".join(out) + "</Story></idPkg:Story>")

    def write(self, path):
        pw, ph = PAGE_W * MM, PAGE_H * MM
        margin = 20 * MM
        margin_xml = (f'<MarginPreference ColumnCount="1" ColumnGutter="{f(5 * MM)}" Top="{f(margin)}" '
                      f'Bottom="{f(margin)}" Left="{f(margin)}" Right="{f(margin)}" ColumnDirection="Horizontal" '
                      f'ColumnsPositions="0 {f(pw - 2 * margin)}"/>')
        page_bounds = f'GeometricBounds="0 0 {f(ph)} {f(pw)}" ItemTransform="1 0 0 1 0 {f(-ph / 2)}"'

        files = {}
        # Grafik: Farben, Farbfelder, Druckfarben, Konturstile
        colors = "".join(
            f'<Color Self="Color/{key}" Model="Process" Space="RGB" ColorValue="{r} {g} {b}" '
            f'ColorOverride="Normal" AlternateSpace="NoAlternateColor" AlternateColorValue="" '
            f'Name="{escape(name)}" ColorEditable="true" ColorRemovable="true" Visible="true" '
            f'SwatchCreatorID="7937"/>' for key, (name, (r, g, b)) in COLORS.items())
        inks = "".join(
            f'<Ink Self="Ink/$ID/Process {c}" Name="$ID/Process {c}" Angle="{a}" ConvertToProcess="false" '
            f'Frequency="70" NeutralDensity="{nd}" PrintInk="true" TrapOrder="{i + 1}" InkType="Normal"/>'
            for i, (c, a, nd) in enumerate([("Cyan", 75, 0.61), ("Magenta", 15, 0.76),
                                            ("Yellow", 0, 0.16), ("Black", 45, 1.7)]))
        files["Resources/Graphic.xml"] = (
            HEAD + f'<idPkg:Graphic {NS}>'
            '<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" '
            'ColorOverride="Specialblack" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Black" '
            'ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
            '<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" '
            'ColorOverride="Specialpaper" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Paper" '
            'ColorEditable="true" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>'
            '<Color Self="Color/Registration" Model="Registration" Space="CMYK" ColorValue="100 100 100 100" '
            'ColorOverride="Specialregistration" AlternateSpace="NoAlternateColor" AlternateColorValue="" '
            'Name="Registration" ColorEditable="false" ColorRemovable="false" Visible="true" '
            'SwatchCreatorID="7937"/>' + colors + inks +
            '<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" '
            'SwatchCreatorID="7937"/>'
            '<StrokeStyle Self="StrokeStyle/$ID/Solid" Name="$ID/Solid"/>'
            '</idPkg:Graphic>')

        # Stile
        pstyles = []
        for name, (fam, sty, size, lead, col, align, track, caps, after) in PARA_STYLES.items():
            pstyles.append(
                f'<ParagraphStyle Self="ParagraphStyle/{name}" Name="{name}" Imported="false" NextStyle="ParagraphStyle/{name}" '
                f'FontStyle="{sty}" PointSize="{f(size)}" FillColor="Color/{col}" Justification="{align}" '
                f'Tracking="{track}" Capitalization="{"AllCaps" if caps else "Normal"}" '
                f'SpaceAfter="{f(after * MM)}" Hyphenation="false" KeyboardShortcut="0 0">'
                f'<Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn>'
                f'<AppliedFont type="string">{fam}</AppliedFont><Leading type="unit">{f(lead)}</Leading>'
                f'</Properties></ParagraphStyle>')
        cstyles = []
        for name, (sty, col) in CHAR_STYLES.items():
            attrs = (f' FontStyle="{sty}"' if sty else "") + (f' FillColor="Color/{col}"' if col else "")
            cstyles.append(f'<CharacterStyle Self="CharacterStyle/{name}" Name="{name}" Imported="false" '
                           f'KeyboardShortcut="0 0"{attrs}><Properties><BasedOn type="string">'
                           f'$ID/[No character style]</BasedOn></Properties></CharacterStyle>')
        files["Resources/Styles.xml"] = (
            HEAD + f'<idPkg:Styles {NS}>'
            '<RootCharacterStyleGroup Self="u79"><CharacterStyle Self="CharacterStyle/$ID/[No character style]" '
            'Imported="false" Name="$ID/[No character style]"/>' + "".join(cstyles) + '</RootCharacterStyleGroup>'
            '<RootParagraphStyleGroup Self="u78"><ParagraphStyle Self="ParagraphStyle/$ID/[No paragraph style]" '
            'Name="$ID/[No paragraph style]" Imported="false" FontStyle="Regular" PointSize="10" '
            'FillColor="Color/Black" Justification="LeftAlign" Hyphenation="false">'
            '<Properties><AppliedFont type="string">Arial</AppliedFont><Leading type="enumeration">Auto</Leading>'
            '</Properties></ParagraphStyle>'
            '<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle" '
            'Imported="false" NextStyle="ParagraphStyle/$ID/NormalParagraphStyle" KeyboardShortcut="0 0">'
            '<Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn></Properties></ParagraphStyle>'
            + "".join(pstyles) + '</RootParagraphStyleGroup>'
            '<RootObjectStyleGroup Self="u7a">'
            '<ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]" FillColor="Swatch/None" '
            'StrokeColor="Swatch/None" StrokeWeight="0"/>'
            '<ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]" '
            'FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0">'
            '<Properties><BasedOn type="string">$ID/[None]</BasedOn></Properties></ObjectStyle>'
            '<ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]" '
            'FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0">'
            '<Properties><BasedOn type="string">$ID/[None]</BasedOn></Properties></ObjectStyle>'
            '</RootObjectStyleGroup></idPkg:Styles>')

        bl = f(BLEED * MM)
        files["Resources/Preferences.xml"] = (
            HEAD + f'<idPkg:Preferences {NS}>'
            f'<DocumentPreference PageHeight="{f(ph)}" PageWidth="{f(pw)}" PagesPerDocument="{len(PAGES)}" '
            f'FacingPages="false" DocumentBleedTopOffset="{bl}" DocumentBleedBottomOffset="{bl}" '
            f'DocumentBleedInsideOrLeftOffset="{bl}" DocumentBleedOutsideOrRightOffset="{bl}" '
            f'DocumentBleedUniformSize="true" AllowPageShuffle="true" PageBinding="LeftToRight" '
            f'Intent="PrintIntent" StartPageNumber="1"/>'
            '<ViewPreference HorizontalMeasurementUnits="Millimeters" VerticalMeasurementUnits="Millimeters"/>'
            + margin_xml + '</idPkg:Preferences>')

        files["MasterSpreads/MasterSpread_um1.xml"] = (
            HEAD + f'<idPkg:MasterSpread {NS}><MasterSpread Self="um1" ItemTransform="1 0 0 1 0 0" '
            'Name="A-Musterseite" NamePrefix="A" BaseName="Musterseite" ShowMasterItems="true" PageCount="1" '
            'OverriddenPageItemProps="" PrimaryTextFrame="n">'
            f'<Page Self="um1p" Name="A" AppliedMaster="n" OverrideList="" TabOrder="" {page_bounds} '
            f'MasterPageTransform="1 0 0 1 0 0" GridStartingPoint="TopOutside" UseMasterGrid="true">'
            f'{margin_xml}</Page></MasterSpread></idPkg:MasterSpread>')

        spread_ids = []
        for i, items in enumerate(PAGES):
            sid = f"us{i + 1}"
            spread_ids.append(sid)
            body = "".join(self.item_xml(it, -ph / 2) for it in items)
            files[f"Spreads/Spread_{sid}.xml"] = (
                HEAD + f'<idPkg:Spread {NS}><Spread Self="{sid}" FlattenerOverride="Default" '
                f'ShowMasterItems="true" PageCount="1" BindingLocation="0" AllowPageShuffle="true" '
                f'ItemTransform="1 0 0 1 0 {f(i * (ph + 40))}" PageTransitionType="None" '
                f'PageTransitionDirection="NotApplicable" PageTransitionDuration="Medium">'
                f'<Page Self="up{i + 1}" Name="{i + 1}" AppliedMaster="um1" OverrideList="" TabOrder="" '
                f'{page_bounds} MasterPageTransform="1 0 0 1 0 0" GridStartingPoint="TopOutside" '
                f'UseMasterGrid="true">{margin_xml}</Page>{body}</Spread></idPkg:Spread>')

        for sid, xml in self.stories.items():
            files[f"Stories/Story_{sid}.xml"] = xml

        files["designmap.xml"] = (
            HEAD + '<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="8.0(370)" ?>\n'
            f'<Document {NS} Self="d" StoryList="{" ".join(self.stories)}" ZeroPoint="0 0" ActiveLayer="uL1" '
            'CMYKProfile="Coated FOGRA39 (ISO 12647-2:2004)" RGBProfile="sRGB IEC61966-2.1" '
            'SolidColorIntent="UseColorSettings" AfterBlendingIntent="UseColorSettings" '
            'DefaultImageIntent="UseColorSettings" RGBPolicy="PreserveEmbeddedProfiles" '
            'CMYKPolicy="CombinationOfPreserveAndSafeCmyk" AccurateLABSpots="false">'
            '<idPkg:Graphic src="Resources/Graphic.xml"/>'
            '<idPkg:Styles src="Resources/Styles.xml"/>'
            '<idPkg:Preferences src="Resources/Preferences.xml"/>'
            '<Layer Self="uL1" Name="Ebene 1" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" '
            'LockGuides="false" UI="true" Expendable="true" Printable="true">'
            '<Properties><LayerColor type="enumeration">LightBlue</LayerColor></Properties></Layer>'
            '<idPkg:MasterSpread src="MasterSpreads/MasterSpread_um1.xml"/>'
            + "".join(f'<idPkg:Spread src="Spreads/Spread_{s}.xml"/>' for s in spread_ids) +
            f'<Section Self="usec1" Length="{len(PAGES)}" Name="" ContinueNumbering="true" '
            'IncludeSectionPrefix="false" PageNumberStyle="Arabic" PageStart="up1" SectionPrefix="" Marker=""/>'
            + "".join(f'<idPkg:Story src="Stories/Story_{s}.xml"/>' for s in self.stories) +
            '</Document>')

        files["META-INF/container.xml"] = (
            HEAD + '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">'
            '<rootfiles><rootfile full-path="designmap.xml" media-type="text/xml"/></rootfiles></container>')

        with zipfile.ZipFile(path, "w") as z:
            z.writestr(zipfile.ZipInfo("mimetype"), "application/vnd.adobe.indesign-idml-package",
                       compress_type=zipfile.ZIP_STORED)
            for name, content in files.items():
                z.writestr(name, content.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)


# ================================================================ PDF-Vorschau
def render_pdf(path, font_dir, pages=None):
    from reportlab.lib.colors import Color
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Paragraph

    lib = "/usr/share/fonts/truetype/liberation"
    # Gelasio ist metrisch kompatibel zu Georgia, Liberation Sans zu Arial.
    fonts = {
        ("Georgia", "Regular"): os.path.join(font_dir, "Gelasio-400-normal.ttf"),
        ("Georgia", "Italic"): os.path.join(font_dir, "Gelasio-400-italic.ttf"),
        ("Georgia", "Bold"): os.path.join(font_dir, "Gelasio-700-normal.ttf"),
        ("Arial", "Regular"): os.path.join(lib, "LiberationSans-Regular.ttf"),
        ("Arial", "Bold"): os.path.join(lib, "LiberationSans-Bold.ttf"),
        ("Arial", "Italic"): os.path.join(lib, "LiberationSans-Italic.ttf"),
        ("Inter", "Regular"): os.path.join(font_dir, "Inter-400.ttf"),
        ("Inter", "Medium"): os.path.join(font_dir, "Inter-500.ttf"),
        ("Inter", "SemiBold"): os.path.join(font_dir, "Inter-600.ttf"),
        ("Inter", "Bold"): os.path.join(font_dir, "Inter-700.ttf"),
    }
    for (fam, sty), file in fonts.items():
        if os.path.exists(file):
            pdfmetrics.registerFont(TTFont(f"{fam}-{sty}", file))

    def col(key):
        r, g, b = COLORS[key][1]
        return Color(r / 255, g / 255, b / 255)

    def hexcol(key):
        return "#%02x%02x%02x" % COLORS[key][1]

    def Y(y_mm):
        return (PAGE_H - y_mm) * MM

    c = canvas.Canvas(path, pagesize=(PAGE_W * MM, PAGE_H * MM))
    c.setTitle("Wohnungsbewerbung – Lea Rager")
    c.setAuthor("Lea Rager")
    for items in (pages or PAGES):
        for it in items:
            k = it["kind"]
            if k == "rect":
                if it["fill"]:
                    c.setFillColor(col(it["fill"]))
                if it["stroke"]:
                    c.setStrokeColor(col(it["stroke"]))
                    c.setLineWidth(it["sw"])
                args = (it["x"] * MM, Y(it["y"] + it["h"]), it["w"] * MM, it["h"] * MM)
                if it["fill"] or it["stroke"]:
                    if it["radius"]:
                        c.roundRect(*args, it["radius"] * MM, stroke=bool(it["stroke"]), fill=bool(it["fill"]))
                    else:
                        c.rect(*args, stroke=bool(it["stroke"]), fill=bool(it["fill"]))
                if it.get("image") and os.path.exists(it["image"]):
                    from reportlab.lib.utils import ImageReader
                    img = ImageReader(it["image"])
                    iw, ih = img.getSize()
                    x, y, w, h = args
                    scale = max(w / iw, h / ih)  # wie „Rahmen proportional füllen“
                    c.saveState()
                    clip = c.beginPath()
                    clip.roundRect(x, y, w, h, it["radius"] * MM)
                    c.clipPath(clip, stroke=0, fill=0)
                    c.drawImage(img, x + (w - iw * scale) / 2, y + (h - ih * scale) / 2, iw * scale, ih * scale)
                    c.restoreState()
            elif k == "oval":
                sw = it["sw"]
                inset = sw / 2 / MM if it["stroke"] else 0  # Kontur innen, wie in InDesign
                if it["fill"]:
                    c.setFillColor(col(it["fill"]))
                if it["stroke"]:
                    c.setStrokeColor(col(it["stroke"]))
                    c.setLineWidth(sw)
                c.ellipse((it["x"] + inset) * MM, Y(it["y"] + it["h"] - inset),
                          (it["x"] + it["w"] - inset) * MM, Y(it["y"] + inset),
                          stroke=bool(it["stroke"]), fill=bool(it["fill"]))
            elif k == "line":
                c.setStrokeColor(col(it["stroke"]))
                c.setLineWidth(it["sw"])
                c.setLineCap(1)
                c.setLineJoin(1)
                p = c.beginPath()
                (x, y), rest = it["points"][0], it["points"][1:]
                p.moveTo(x * MM, Y(y))
                for x, y in rest:
                    p.lineTo(x * MM, Y(y))
                c.drawPath(p, stroke=1, fill=0)
            elif k == "text":
                w = it["w"] * MM
                blocks = []  # (height, after, draw(x, top))
                for pstyle, runs in it["paras"]:
                    fam, sty, size, lead, pcol, align, track, caps, after = PARA_STYLES[pstyle]
                    if caps or track >= 50:  # einzeilige Labels mit Laufweite direkt zeichnen
                        s = "".join(t for t, _ in runs)
                        s = s.upper() if caps else s

                        def draw(x, top, s=s, fn=f"{fam}-{sty}", size=size, lead=lead, pcol=pcol,
                                 align=align, cs=size * track / 1000):
                            tw = pdfmetrics.stringWidth(s, fn, size) + cs * (len(s) - 1)
                            if align == "CenterAlign":
                                x += (w - tw) / 2
                            t = c.beginText()
                            t.setTextOrigin(x, top - lead + (lead - size) / 2 + size * 0.2)
                            t.setFont(fn, size)
                            t.setCharSpace(cs)
                            t.setFillColor(col(pcol))
                            t.textOut(s)
                            t.setCharSpace(0)  # Tc bleibt sonst im Grafikzustand aktiv
                            c.drawText(t)
                        blocks.append((lead, after * MM, draw))
                        continue
                    markup = ""
                    for t, cs in runs:
                        t = escape(t)
                        if cs:
                            csty, ccol = CHAR_STYLES[cs]
                            markup += (f'<font name="{fam}-{csty or sty}" color="{hexcol(ccol or pcol)}">'
                                       f'{t}</font>')
                        else:
                            markup += t
                    ps = ParagraphStyle(pstyle, fontName=f"{fam}-{sty}", fontSize=size, leading=lead,
                                        textColor=col(pcol),
                                        alignment={"LeftAlign": 0, "CenterAlign": 1, "RightAlign": 2}[align])
                    para = Paragraph(markup, ps)
                    _, h = para.wrap(w, 10000)
                    blocks.append((h, after * MM, lambda x, top, para=para, h=h: para.drawOn(c, x, top - h)))
                total = sum(h + a for h, a, _ in blocks) - blocks[-1][1]
                top = Y(it["y"])
                if it["valign"] == "CenterAlign":
                    top -= (it["h"] * MM - total) / 2
                elif it["valign"] == "BottomAlign":
                    top -= it["h"] * MM - total
                for h, a, draw in blocks:
                    draw(it["x"] * MM, top)
                    top -= h + a
        c.showPage()
    c.save()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", help="Ordner mit Gelasio-*.ttf für die PDF-Vorschau")
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()
    IdmlWriter().write(os.path.join(a.out, "Wohnungsportfolio_Lea_Rager.idml"))
    if a.fonts:
        render_pdf(os.path.join(a.out, "Wohnungsportfolio_Lea_Rager_Vorschau.pdf"), a.fonts)
        render_pdf(os.path.join(a.out, "Unterlagen_Deckblatt_Vorschau.pdf"), a.fonts, pages=PAGES[1:])
