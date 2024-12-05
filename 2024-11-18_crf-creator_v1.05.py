import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

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

def create_pdf_for_form(data, form_name, output_pdf):
    # Initialize PDF canvas
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter
    margin = 50
    text_width = width - 2 * margin
    y = height - margin
    page_number = 1

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, f"Form: {form_name}")
    y -= 30

    # Loop through questions and render them
    for index, row in data.iterrows():
        question = row['question']
        q_type = row['type']
        choices = row['choice'] if 'choice' in row and not pd.isna(row['choice']) else None

        # Clean HTML tags if present
        question = question.replace("<div style=\"padding-left: 3em\">", "").replace("</div>", "")

        # Wrap long question text
        wrapped_lines = wrap_text(question, c, text_width)

        if y - (15 * len(wrapped_lines)) < margin + 50:  # Check if space is sufficient
            # Add footer before starting a new page
            c.setFont("Helvetica", 10)
            c.drawString(margin, margin, f"Page {page_number} - Form: {form_name}")
            c.showPage()
            page_number += 1
            y = height - margin

        # Add question
        c.setFont("Helvetica", 10)
        for line in wrapped_lines:
            c.drawString(margin, y, line)
            y -= 12

        # Add input field or choices
        if q_type == "text":
            c.rect(margin, y - 15, text_width, 18)
            y -= 25
        elif q_type == "notes":
            for _ in range(5):
                c.rect(margin, y - 15, text_width, 18)
                y -= 22
        elif q_type in ["radio", "checkbox"] and choices:
            options = [opt.strip() for opt in choices.split('|')]
            for option in options:
                value, label = option.split(',', 1)
                if q_type == "radio":
                    c.circle(margin + 10, y - 5, 4)
                else:
                    c.rect(margin + 5, y - 10, 10, 10)
                c.drawString(margin + 20, y - 10, label.strip())
                y -= 15
        else:
            y -= 10

        y -= 10

    # Add footer to the last page
    c.setFont("Helvetica", 10)
    c.drawString(margin, margin, f"Page {page_number} - Form: {form_name}")
    c.save()

def create_pdfs_from_csv(csv_file):
    # Load CSV data
    data = pd.read_csv(csv_file)

    # Group data by 'form'
    forms = data.groupby('form')

    # Generate a PDF for each form
    for form_name, form_data in forms:
        output_pdf = f"{form_name.replace(' ', '_')}_form.pdf"
        create_pdf_for_form(form_data, form_name, output_pdf)
        print(f"PDF for form '{form_name}' saved to {output_pdf}")

# Example usage
csv_file = "test.csv"
create_pdfs_from_csv(csv_file)
