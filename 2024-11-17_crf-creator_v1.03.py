import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Frame, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def wrap_text(text, canvas, max_width):
    """
    Wraps text to fit within the specified max width of the canvas.
    """
    lines = []
    words = text.split()
    line = []
    for word in words:
        line.append(word)
        test_line = ' '.join(line)
        if canvas.stringWidth(test_line, "Helvetica", 12) > max_width:
            lines.append(' '.join(line[:-1]))
            line = [word]
    lines.append(' '.join(line))
    return lines

def create_pdf_from_csv(csv_file, output_pdf):
    # Load CSV data
    data = pd.read_csv(csv_file)
    
    # Initialize PDF canvas
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter
    margin = 50  # Margin for the page
    text_width = width - 2 * margin  # Width available for text

    # Set styles
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']

    # Start drawing content
    y = height - margin  # Starting position from the top

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Questionnaire Form")
    y -= 30  # Adjust spacing after title

    # Loop through questions and render them
    for index, row in data.iterrows():
        question = row['question']
        q_type = row['type']
        choices = row['choice'] if 'choice' in row and not pd.isna(row['choice']) else None

        # Clean HTML tags if present
        question = question.replace("<div style=\"padding-left: 3em\">", "").replace("</div>", "")

        # Wrap long question text
        wrapped_lines = wrap_text(question, c, text_width)

        if y - (20 * len(wrapped_lines)) < margin:  # Check if space is sufficient
            c.showPage()
            y = height - margin

        # Add question
        c.setFont("Helvetica", 12)
        for line in wrapped_lines:
            c.drawString(margin, y, line)
            y -= 15  # Adjust spacing for each line

        # Add input field or choices
        if q_type == "text":
            c.rect(margin, y - 15, text_width, 20)
            y -= 40
        elif q_type == "notes":
            for _ in range(5):
                c.rect(margin, y - 15, text_width, 20)
                y -= 25
        elif q_type in ["radio", "checkbox"] and choices:
            options = [opt.strip() for opt in choices.split('|')]
            for option in options:
                value, label = option.split(',', 1)
                c.circle(margin + 10, y - 5, 5) if q_type == "radio" else c.rect(margin + 5, y - 10, 10, 10)
                c.drawString(margin + 20, y - 10, label.strip())
                y -= 20
        else:
            y -= 10  # Adjust spacing for unknown types or blank

        y -= 10  # Extra spacing after each question

        # If space is insufficient for the next question, start a new page
        if y < margin:
            c.showPage()
            y = height - margin

    # Save the PDF
    c.save()
    print(f"PDF saved to {output_pdf}")

# Example usage
csv_file = "test.csv"
output_pdf = "questionnaire_form_v3.1.pdf"
create_pdf_from_csv(csv_file, output_pdf)
