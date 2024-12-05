import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfMerger

version_number = "v1.36"  # Define version number here for easy updates

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
    formatted_form_name = form_name.replace("_", " ").upper()

    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter
    margin = 50
    text_width = width - 2 * margin
    y = height - 70
    page_number = 1

    def draw_header():
        c.setFont("Helvetica", 10)
        header_text = f"{formatted_form_name} - Page {page_number}"
        header_width = c.stringWidth(header_text, "Helvetica", 10)
        c.drawString(width - margin - header_width, height - 30, header_text)

    draw_header()

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, formatted_form_name)
    y -= 40

    for index, row in data.iterrows():
        question = row['question'].replace("<div style=\"padding-left: 3em\">", "").replace("</div>", "")
        wrapped_lines = wrap_text(question, c, text_width)

        if y - (15 * len(wrapped_lines)) < margin + 50:
            c.showPage()
            page_number += 1
            y = height - 70
            draw_header()

        c.setFont("Helvetica", 10)
        for line in wrapped_lines:
            c.drawString(margin, y, line)
            y -= 12

        q_type = row['type']
        choices = row.get('choice')
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

        y -= 10

    c.save()

def create_pdfs_from_csv(csv_file):
    data = pd.read_csv(csv_file)
    data.rename(columns={  # Update this mapping according to your CSV structure
        'Variable / Field Name': 'variable_name',
        'Form Name': 'form',
        'Section Header': 'section_header',
        'Field Type': 'type',
        'Field Label': 'question',
        'Choices, Calculations, OR Slider Labels': 'choice',
        'Field Note': 'field_note',
        'Text Validation Type OR Show Slider Number': 'validation_type',
        'Text Validation Min': 'validation_min',
        'Text Validation Max': 'validation_max',
        'Identifier?': 'identifier',
        'Branching Logic (Show field only if...)': 'branching_logic',
        'Required Field?': 'required_field',
        'Custom Alignment': 'custom_alignment',
        'Question Number (surveys only)': 'question_number',
        'Matrix Group Name': 'matrix_name',
        'Matrix Ranking?': 'matrix_ranking',
        'Field Annotation': 'field_annotation'
    }, inplace=True)

    forms = data.groupby('form')
    pdf_files = []

    for form_name, form_data in forms:
        output_pdf = f"{form_name}_{version_number}.pdf"
        pdf_files.append(output_pdf)
        create_pdf_for_form(form_data, form_name, output_pdf)
        print(f"PDF for form '{form_name}' saved to {output_pdf}")

    combined_pdf = f"combined_forms_{version_number}.pdf"
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
