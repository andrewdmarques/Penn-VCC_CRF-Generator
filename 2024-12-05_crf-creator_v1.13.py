import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfMerger

version_number = "v0.41"  # Define version number here for easy updates

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
            line.pop()
            lines.append(' '.join(line))
            line = [word]
    if line:
        lines.append(' '.join(line))
    return lines

def create_pdf_for_form(data, form_name, output_pdf):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter
    margin = 50
    text_width = width - 2 * margin
    y = height - 70

    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, form_name.replace("_", " ").upper())
    y -= 40

    matrix_data = data.dropna(subset=['matrix_name'])
    normal_data = data[data['matrix_name'].isna()]

    if not matrix_data.empty:
        grouped_matrix = matrix_data.groupby('matrix_name')
        for matrix_name, group in grouped_matrix:
            choices = group['choice'].iloc[0].split('|')
            choice_labels = [ch.split(',')[1] for ch in choices]
            c.setFont("Helvetica", 12)
            c.drawString(margin, y, matrix_name)
            y -= 20
            c.setFont("Helvetica", 10)
            c.drawString(margin, y, "Question")
            x = margin + 150
            for label in choice_labels:
                c.drawString(x, y, label)
                x += 70
            y -= 20

            for index, row in group.iterrows():
                question = wrap_text(row['question'], c, 140)
                x = margin
                c.drawString(x, y, question[0])  # Assuming first line is the summarized question
                x += 150
                for _ in choice_labels:
                    c.rect(x, y - 10, 60, 15)
                    x += 70
                y -= 20
                if y < margin:
                    c.showPage()
                    y = height - 70

    # Process normal questions
    for index, row in normal_data.iterrows():
        if y < margin + 50:
            c.showPage()
            y = height - 70
        question = wrap_text(row['question'], c, text_width)
        c.setFont("Helvetica", 12)
        for line in question:
            c.drawString(margin, y, line)
            y -= 14
        c.setFont("Helvetica", 10)
        if row['type'] == "text":
            c.rect(margin, y - 15, text_width, 18)
            y -= 25
        elif row['type'] == "notes":
            for _ in range(5):
                c.rect(margin, y - 15, text_width, 18)
                y -= 22
        elif row['type'] in ["radio", "checkbox"]:
            options = [opt.strip() for opt in row['choice'].split('|')]
            for option in options:
                value, label = option.split(',', 1)
                if row['type'] == "radio":
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
