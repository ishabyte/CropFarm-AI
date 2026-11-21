
import os
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle
)


FONT_PATH = r"C:\Windows\Fonts\Nirmala.ttc"
FONT_NAME = "NirmalaUI"


LANGUAGE_LABELS = {
    "en": {
        "title": "cropFarm AI",
        "subtitle": "Crop Disease Diagnosis Report",
        "summary": "Diagnosis Summary",
        "disease": "Detected Disease",
        "confidence": "AI Confidence",
        "description": "Description",
        "symptoms": "Symptoms",
        "treatment": "General Treatment",
        "organic": "Organic Treatment",
        "chemical": "Chemical Treatment",
        "recovery": "Recovery",
        "prevention": "Prevention",
        "note": "Note: This AI-generated report is for guidance only. Consult an agricultural expert before applying treatment."
    },
    "hi": {
        "title": "एग्रीविजन एआई",
        "subtitle": "फसल रोग निदान रिपोर्ट",
        "summary": "निदान सारांश",
        "disease": "पहचाना गया रोग",
        "confidence": "एआई विश्वास स्तर",
        "description": "विवरण",
        "symptoms": "लक्षण",
        "treatment": "सामान्य उपचार",
        "organic": "जैविक उपचार",
        "chemical": "रासायनिक उपचार",
        "recovery": "सुधार",
        "prevention": "बचाव",
        "note": "नोट: यह एआई रिपोर्ट केवल मार्गदर्शन के लिए है। उपचार करने से पहले कृषि विशेषज्ञ से सलाह लें।"
    },
    "as": {
        "title": "এগ্ৰিভিজন এআই",
        "subtitle": "শস্যৰ ৰোগ নিৰ্ণয় প্ৰতিবেদন",
        "summary": "ৰোগ নিৰ্ণয়ৰ সাৰাংশ",
        "disease": "চিনাক্ত কৰা ৰোগ",
        "confidence": "এআইৰ বিশ্বাসযোগ্যতা",
        "description": "বিৱৰণ",
        "symptoms": "লক্ষণ",
        "treatment": "সাধাৰণ চিকিৎসা",
        "organic": "জৈৱিক চিকিৎসা",
        "chemical": "ৰাসায়নিক চিকিৎসা",
        "recovery": "আৰোগ্য",
        "prevention": "প্ৰতিৰোধ",
        "note": "টোকা: এই এআই প্ৰতিবেদন কেৱল নিৰ্দেশনাৰ বাবে। চিকিৎসা কৰাৰ আগতে কৃষি বিশেষজ্ঞৰ পৰামৰ্শ লওক।"
    },
    "bn": {
        "title": "এগ্রিভিশন এআই",
        "subtitle": "ফসলের রোগ নির্ণয় প্রতিবেদন",
        "summary": "রোগ নির্ণয়ের সারাংশ",
        "disease": "শনাক্ত করা রোগ",
        "confidence": "এআই নির্ভরযোগ্যতা",
        "description": "বিবরণ",
        "symptoms": "লক্ষণ",
        "treatment": "সাধারণ চিকিৎসা",
        "organic": "জৈবিক চিকিৎসা",
        "chemical": "রাসায়নিক চিকিৎসা",
        "recovery": "পুনরুদ্ধার",
        "prevention": "প্রতিরোধ",
        "note": "নোট: এই এআই প্রতিবেদনটি শুধুমাত্র নির্দেশনার জন্য। চিকিৎসা প্রয়োগের আগে কৃষি বিশেষজ্ঞের পরামর্শ নিন।"
    }
}


def register_indian_font():

    if not os.path.exists(FONT_PATH):
        raise FileNotFoundError("Nirmala UI font was not found.")

    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        font = TTFont(
            FONT_NAME,
            FONT_PATH,
            subfontIndex=0,
            shapable=True
        )

        pdfmetrics.registerFont(font)

        pdfmetrics.registerFontFamily(
            FONT_NAME,
            normal=FONT_NAME,
            bold=FONT_NAME,
            italic=FONT_NAME,
            boldItalic=FONT_NAME
        )


def generate_pdf_report(
    image_path,
    disease_name,
    confidence,
    disease_details,
    language="en"
):

    register_indian_font()

    language = language if language in LANGUAGE_LABELS else "en"
    labels = LANGUAGE_LABELS[language]

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName=FONT_NAME,
        fontSize=20,
        leading=28,
        textColor=colors.HexColor("#247A3D"),
        alignment=1,
        shaping=1
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName=FONT_NAME,
        fontSize=13,
        leading=20,
        textColor=colors.HexColor("#247A3D"),
        spaceBefore=12,
        spaceAfter=6,
        shaping=1
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontName=FONT_NAME,
        fontSize=10,
        leading=17,
        shaping=1
    )

    bold_style = ParagraphStyle(
        "ReportBold",
        parent=body_style,
        fontSize=10
    )

    note_style = ParagraphStyle(
        "ReportNote",
        parent=body_style,
        fontSize=9,
        textColor=colors.grey
    )

    story = []

    story.append(Paragraph(labels["title"], title_style))
    story.append(Paragraph(labels["subtitle"], heading_style))
    story.append(Spacer(1, 15))

    if image_path and os.path.exists(image_path):
        crop_image = Image(
            image_path,
            width=2.2 * inch,
            height=2.2 * inch,
            kind="proportional"
        )
        crop_image.hAlign = "CENTER"
        story.append(crop_image)
        story.append(Spacer(1, 15))

    story.append(
        Paragraph(labels["summary"], heading_style)
    )

    summary_data = [
        [
            Paragraph(escape(labels["disease"]), bold_style),
            Paragraph(escape(str(disease_name)), body_style)
        ],
        [
            Paragraph(escape(labels["confidence"]), bold_style),
            Paragraph(escape(str(confidence)) + "%", body_style)
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[150, 300]
    )

    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1),
         colors.HexColor("#E8F5E9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(summary_table)

    sections = [
        ("description", "description"),
        ("symptoms", "symptoms"),
        ("treatment", "treatment"),
        ("organic", "organic_treatment"),
        ("chemical", "chemical_treatment"),
        ("recovery", "recovery"),
        ("prevention", "prevention")
    ]

    for label_key, data_key in sections:

        content = disease_details.get(
            data_key,
            "Information not available."
        )

        story.append(
            Paragraph(labels[label_key], heading_style)
        )

        story.append(
            Paragraph(escape(str(content)), body_style)
        )

        story.append(Spacer(1, 6))

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            escape(labels["note"]),
            note_style
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer
