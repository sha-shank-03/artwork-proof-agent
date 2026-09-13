import base64
import io
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, KeepTogether

def build_pdf(run):
    output=io.BytesIO(); styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Meta",fontSize=8,leading=12,textColor=colors.HexColor("#58646b")))
    doc=SimpleDocTemplate(output,pagesize=(595,842),rightMargin=42,leftMargin=42,topMargin=42,bottomMargin=42)
    content=[Paragraph("ARTWORK / PROOF REPORT",styles["Title"]),Spacer(1,12),
             Paragraph("Independent portfolio demonstration. Not print certification. No artwork has been sent to a printer.",styles["Meta"]),Spacer(1,12),
             Paragraph(escape(run["report"]["summary"]),styles["BodyText"]),Spacer(1,12)]
    for i,preview in enumerate(run["previews"]):
        data=base64.b64decode(preview); image=ImageReader(io.BytesIO(data));w,h=image.getSize();scale=min(460/w,260/h)
        content.extend([Paragraph(f"Page {i+1} preview",styles["Heading2"]),Image(io.BytesIO(data),width=w*scale,height=h*scale),Spacer(1,12)])
    for f in run["report"]["findings"]:
        content.append(KeepTogether([Paragraph(escape(f["title"]),styles["Heading3"]),Paragraph(escape(f["category"]+" / "+f["severity"]+" / "+f["evidence_id"]),styles["Meta"]),Paragraph(escape(f["detail"]),styles["BodyText"]),Spacer(1,8)]))
    content.extend([Spacer(1,12),Paragraph("Artwork hash: "+escape(run["artworkHash"]),styles["Meta"]),Paragraph("Report digest: "+escape(run["reportDigest"]),styles["Meta"]),Paragraph(f"Version {run['version']} | {run['report']['specVersion']} | Status: {run['state']}",styles["Meta"])])
    def footer(canvas,document):
        canvas.setFont("Helvetica",8);canvas.setFillColor(colors.HexColor("#58646b"));canvas.drawString(42,25,"Artwork Proof Agent - demonstration specifications only");canvas.drawRightString(553,25,str(document.page))
    doc.build(content,onFirstPage=footer,onLaterPages=footer)
    return output.getvalue()
