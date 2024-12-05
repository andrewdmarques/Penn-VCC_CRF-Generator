import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Frame, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
    style_title = styles['Heading1']

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

        if y < margin:  # Check if we need a new page
            c.showPage()
            y = height - margin

        # Add question
        c.setFont("Helvetica", 12)
        c.drawString(margin, y, f"{index + 1}. {question}")
        y -= 20  # Space after question

        # Add input field or choices
        if q_type == "text":
            c.rect(margin, y - 15, width - 2 * margin, 20)
            y -= 40
        elif q_type == "notes":
            for _ in range(5):
                c.rect(margin, y - 15, width - 2 * margin, 20)
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

    # Save the PDF
    c.save()
    print(f"PDF saved to {output_pdf}")

# Example usage
csv_file = "test.csv"
output_pdf = "questionnaire_form.pdf"
create_pdf_from_csv(csv_file, output_pdf)