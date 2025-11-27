import os
from pathlib import Path
from pypdf import PdfReader, PdfWriter, PaperSize, Transformation

# --- Configuration (Adjust these paths) ---
INPUT_FOLDER = "D:/src/loy/python/pdf-6-per-page-converter/input"
OUTPUT_FOLDER = "D:/src/loy/python/pdf-6-per-page-converter/output"
PAGES_PER_SHEET = 6
COLUMNS = 3
ROWS = 2

def convert_pdf_to_nup(input_file_path: Path, output_file_path: Path, pages_per_sheet: int, columns: int, rows: int):
    if columns * rows != pages_per_sheet:
        raise ValueError("Columns * Rows must equal Pages_Per_Sheet")

    try:
        reader = PdfReader(input_file_path)
        writer = PdfWriter()
        
        page_width, page_height = PaperSize.A4
        new_page_width, new_page_height = page_height, page_width 
        
        scale_x = new_page_width / columns 
        scale_y = new_page_height / rows
        
        original_width = reader.pages[0].cropbox.width
        original_height = reader.pages[0].cropbox.height

        scale_factor_x = (scale_x / original_width)
        scale_factor_y = (scale_y / original_height)
        
        final_scale_factor = min(scale_factor_x, scale_factor_y) 
        
        scaled_width = original_width * final_scale_factor
        scaled_height = original_height * final_scale_factor

        print(f"Processing: {len(reader.pages)} pages. Scaling factor: {final_scale_factor:.3f}")

        for i in range(0, len(reader.pages), pages_per_sheet):
            nup_page = writer.add_blank_page(width=new_page_width, height=new_page_height)
            
            for j in range(pages_per_sheet):
                page_index = i + j
                if page_index < len(reader.pages):
                    original_page = reader.pages[page_index]
                    
                    col = j % columns
                    row = j // columns
                    
                    cell_x_start = col * (new_page_width / columns)
                    cell_y_start = (rows - 1 - row) * (new_page_height / rows)

                    x_offset = cell_x_start + (new_page_width / columns - scaled_width) / 2
                    y_offset = cell_y_start + (new_page_height / rows - scaled_height) / 2
                    
                    transform = Transformation().scale(final_scale_factor).translate(x_offset, y_offset)
                    
                    nup_page.merge_transformed_page(
                        original_page, 
                        transform
                    )

            with open(output_file_path, "wb") as output_stream:
                writer.write(output_stream)
                
        print(f"Successfully converted to: {output_file_path.name}")
        
    except Exception as e:
        print(f"An error occurred processing {input_file_path.name}: {e}")

def process_folder(input_dir: str, output_dir: str):
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Output folder '{output_dir}' is ready.")

    pdf_files = list(input_path.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in '{input_dir}'.")
        return

    print(f"Found {len(pdf_files)} PDF files to process.")
    print("-" * 30)

    for pdf_file in pdf_files:
        output_file = output_path / f"{pdf_file.stem}_6up.pdf"
        print(f"Processing file: {pdf_file.name}")
        convert_pdf_to_nup(pdf_file, output_file, PAGES_PER_SHEET, COLUMNS, ROWS)

    print("-" * 30)
    print("Conversion complete!")

if __name__ == "__main__":
    try:
        from fpdf import FPDF
        input_dir = Path(INPUT_FOLDER)
        input_dir.mkdir(parents=True, exist_ok=True)
        for i in range(1, 3):
            pdf = FPDF()
            pdf.set_font("Arial", size=12)
            for page_num in range(1, 13):
                pdf.add_page()
                pdf.text(10, 10, f"Document {i} - Original Page {page_num}")
            dummy_file_path = input_dir / f"document_{i}.pdf"
            pdf.output(dummy_file_path)
    except ImportError:
        pass
    
    process_folder(INPUT_FOLDER, OUTPUT_FOLDER)