import io
from fitz import fitz


def split_and_create_pdf(input_file, page_index_list, output_file=None):
    # Open the PDF file from buffer
    if type(input_file) == bytes:
        pdf_document = fitz.open("pdf", input_file)
    elif type(input_file) == str:
        # Open the PDF file
        pdf_document = fitz.open(input_file)

    # Create a new PDF document
    output_pdf = fitz.open()

    # Iterate through the pages and copy the required pages to the new PDF document
    for page_index in page_index_list:
        if page_index:
            page = pdf_document.load_page(page_index - 1)
            rect = page.rect  # Page size
            new_pdf_page = output_pdf.new_page(width=rect.width, height=rect.height)
            new_pdf_page.show_pdf_page(rect, pdf_document, page_index - 1)

    if output_file:
        # Save the new PDF file
        output_pdf.save(output_file)
        # Close the PDF documents
        output_pdf.close()
        pdf_document.close()
    else:
        output_pdf_buffer = io.BytesIO()
        output_pdf.save(output_pdf_buffer)
        output_pdf_bytes = output_pdf_buffer.getvalue()
        # Close the PDF documents
        output_pdf.close()
        pdf_document.close()
        return output_pdf_bytes

# with open("claim_merged.pdf", "rb") as input_file:
#     input_file = input_file.read()

# Example usage
# input_file = "claim_merged.pdf"
# page_index_list = [1, 2, 5, 8]
# output_file = "output_file_CF.pdf"

# Call the function
# print(split_and_create_pdf(input_file, page_index_list))
