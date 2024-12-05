import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfMerger

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
    # Format form name for the header
    formatted_form_name = form_name.replace("_", " ").upper()

    # Initialize PDF canvas
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter
    margin = 50
    text_width = width - 2 * margin
    y = height - margin
    page_number = 1

    def draw_header():
        """Draws the page number and form name at the top of each page."""
        c.setFont("Helvetica", 10)
        header_text = f"Page {page_number} - {formatted_form_name}"
        c.drawString(margin, height - 30, header_text)  # Place near the top

    draw_header()  # Draw header for the first page

    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y - 50, formatted_form_name)
    y -= 80  # Adjust y-position for the title

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
            c.showPage()
            page_number += 1
            y = height - margin
            draw_header()  # Draw header for the new page

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

    # Save the PDF
    c.save()

def create_pdfs_from_csv(csv_file):
    # Load CSV data
    data = pd.read_csv(csv_file)

    # Group data by 'form'
    forms = data.groupby('form')

    pdf_files = []

    # Generate a PDF for each form
    for form_name, form_data in forms:
        # Create output filename with "_v1.00"
        output_pdf = f"{form_name}_v1.06.pdf"
        pdf_files.append(output_pdf)

        # Generate the form PDF
        create_pdf_for_form(form_data, form_name, output_pdf)
        print(f"PDF for form '{form_name}' saved to {output_pdf}")

    # Merge all individual PDFs into one combined PDF
    combined_pdf = "combined_forms_v1.06.pdf"
    merge_pdfs(pdf_files, combined_pdf)
    print(f"Combined PDF saved to {combined_pdf}")

def merge_pdfs(pdf_files, output_pdf):
    merger = PdfMerger()
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(output_pdf)
    merger.close()

# Example usage
csv_file = "test.csv"
create_pdfs_from_csv(csv_file)
