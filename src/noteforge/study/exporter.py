import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def export_to_pdf(notes_text: str, output_path: str):
    """Exports generated notes to a formatted PDF."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Lecture Study Guide", styles['Title']))
    story.append(Spacer(1, 12))

    lines = notes_text.split('\n')
    for line in lines:
        if line.startswith('###'):
            story.append(Spacer(1, 12))
            story.append(Paragraph(line.replace('###', '').strip(), styles['Heading1']))
        elif line.startswith('- **'):
            header_match = re.search(r'\*\*(.*?)\*\*', line)
            if header_match:
                label = header_match.group(1)
                content = line.split('**:', 1)[-1].strip()
                story.append(Paragraph(f"<b>{label}</b>", styles['Heading2']))
                if content:
                    story.append(Paragraph(content, styles['Normal']))
            else:
                story.append(Paragraph(line, styles['Normal']))
        elif line.strip():
            story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 4))

    doc.build(story)
    return True
