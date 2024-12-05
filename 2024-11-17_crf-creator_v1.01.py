import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Frame, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def clean_question_text(text):
    """Removes unnecessary HTML tags from the question."""
    if isinstance(text, str):
        return text.replace('<div style="padding-left: 3em">', '').replace('</div>', '').strip()
    return text

def wrap_text(c, text, width, margin, y):
    """Wraps text to fit within the page margins."""
    styles = getSampleStyleSheet()
    style = styles['Normal']
    frame_width = width - 2 * margin
    paragraph = Paragraph(text, style)
    available_height = y - margin
    f = Frame(margin, margin, frame_width, available_height)
    f.addFromList([paragraph], c)
    return f._aH

def create_pdf_from_csv(csv_file, output_pdf):
    # Load CSV data
    data = pd.read_csv(csv_file)
    
    # Initialize PDF canvas
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter
    margin = 50  # Margin for the page

    # Set styles
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']

    # Start drawing content
    y = height - margin  # Starting position from the top

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Questionnaire Form")
    y -= 30  # Adjust spacing after title

    for index, row in data.iterrows():
        question = clean_question_text(row['question'])
        q_type = row['type']
        choices = row['choice'] if 'choice' in row and not pd.isna(row['choice']) else None

        if y < margin + 50:  # Check if we need a new page
            c.showPage()
            y = height - margin

        # Wrap question text
        c.setFont("Helvetica", 12)
        remaining_y = wrap_text(c, f"{index + 1}. {question}", width, margin, y)
        y = remaining_y - 10  # Adjust spacing after wrapped question

        # Add input field or choices
        if q_type == "text":
            if y < margin + 40:
                c.showPage()
                y = height - margin
            c.rect(margin, y - 15, width - 2 * margin, 20)
            y -= 40
        elif q_type == "notes":
            for _ in range(5):
                if y < margin + 25:
                    c.showPage()
                    y = height - margin
                c.rect(margin, y - 15, width - 2 * margin, 20)
                y -= 25
        elif q_type in ["radio", "checkbox"] and choices:
            options = [opt.strip() for opt in choices.split('|')]
            for option in options:
                if y < margin + 20:
                    c.showPage()
                    y = height - margin
                value, label = option.split(',', 1)
                c.circle(margin + 10, y - 5, 5) if q_type == "radio" else c.rect(margin + 5, y - 10, 10, 10)
                remaining_y = wrap_text(c, label.strip(), width - 40, margin + 20, y)
                y = remaining_y - 10
        else:
            y -= 10  # Adjust spacing for unknown types or blank

        y -= 10  # Extra spacing after each question

    # Save the PDF
    c.save()
    print(f"PDF saved to {output_pdf}")

# Example usage
csv_file = "test.csv"
output_pdf = "questionnaire_form_v2.pdf"
create_pdf_from_csv(csv_file, output_pdf)
