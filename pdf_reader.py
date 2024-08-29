import os
import re
import shutil
from pdfminer.high_level import extract_text

# Configuration and path settings
staged_folder = 'staged_files'  # Folder where files are staged for processing
completed_folder = 'staged_files_completed'  # Folder to move processed files
output_folder_txt = 'output_text_files'  # Folder to store extracted text files (not used in code)
output_folder_data = 'data'  # Folder to store chunked files
old_data_folder = 'old_data'  # Folder to store old data for backup

def extract_text_from_pdfs(stage_folder, completed_folder):
    for pdf_file in os.listdir(stage_folder):
        try:
            if pdf_file.endswith(".pdf"):
                print(f"Processing file: {pdf_file}")  # Debug: File being processed
                
                output_file_name = os.path.splitext(pdf_file)[0] + ".txt"
                output_path = os.path.join(staged_folder, output_file_name)
                pdf_path = os.path.join(stage_folder, pdf_file)
                
                # Extracting text
                text = extract_text(pdf_path)
                print(f"Text extracted from {pdf_file}, length: {len(text)}")  # Debug: Length of extracted text
                
                # Adding space at the end of each line
                text = "\n".join([line.strip() + " " for line in text.splitlines()])
                
                # Writing extracted text to a file
                with open(output_path, "w", encoding="utf-8") as out:
                    out.write(text)
                print(f"Written text to {output_file_name}")  # Debug: Text written to file
                
                # Moving the processed PDF to the completed folder
                if not os.path.exists(completed_folder):
                    os.makedirs(completed_folder)
                shutil.move(pdf_path, os.path.join(completed_folder, pdf_file))
                print(f"Moved {pdf_file} to {completed_folder}")  # Debug: File moved to completed folder
            
        except Exception as e:
            print(f"Error processing file {pdf_file}: {e}")  # Debug: Error encountered
            continue  # Continue with the next file if an error occurs


def process_text(text):
    # Clean up text by removing non-ASCII characters and unwanted symbols
    text = text.encode('ascii', errors='ignore').decode('ascii')
    text = re.sub(r'[^A-Za-z0-9 .,?!]+', '', text)  # Remove unwanted characters
    return text

def chunk_file_and_save(filename, doc_number):
    # Split the text into chunks of 500 words and save each chunk as a new file
    with open(filename, 'r') as f:
        content = f.read()

    content = process_text(content)  # Clean up the text
    word_list = content.split()  # Split text into words
    start_idx = 0

    # Loop through the text and chunk it
    while start_idx < len(word_list):
        end_idx = start_idx + 500
        # Ensure that the chunk ends on a punctuation mark
        while end_idx < len(word_list) and word_list[end_idx][-1] not in ['.', '!', '?']:
            end_idx -= 1
        end_idx += 1

        # Create the chunk and save it as a new file
        chunk = ' '.join(word_list[start_idx:end_idx])
        with open(os.path.join(output_folder_data, f'doc_{doc_number}.txt'), 'w') as output_file:
            output_file.write(chunk)
            print('writing', output_file)

        start_idx = end_idx  # Move the start index for the next chunk
        doc_number += 1  # Increment document number
        print(doc_number)
    return doc_number

def delete_old_data():
    # Delete old data files and directories in the old_data_folder
    for filename in os.listdir(old_data_folder):
        file_path = os.path.join(old_data_folder, filename)

        if os.path.isfile(file_path):
            os.remove(file_path)  # Remove the file
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  # Remove the directory and all its contents

if __name__ == '__main__':
    # Main processing logic

    # Ensure the completed folder exists
    if not os.path.exists(completed_folder):
        print("Trying to create:", completed_folder)
        os.makedirs(completed_folder)
    extract_text_from_pdfs(staged_folder, completed_folder)  # Extract text from PDFs

    # Ensure output and old data folders exist
    for dir_name in [output_folder_data, old_data_folder]:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    # Delete old data if any exists in the old_data_folder
    if os.listdir(old_data_folder):
        delete_old_data()

    # Move existing files in the output folder to old data folder
    if os.listdir(output_folder_data):
        for filename in os.listdir(output_folder_data):
            dst_path = os.path.join(old_data_folder, filename)
            if os.path.exists(dst_path):
                os.remove(dst_path)
            shutil.move(os.path.join(output_folder_data, filename), dst_path)

    # Check if the staged folder exists
    if not os.path.exists(staged_folder):
        raise FileNotFoundError("The 'staged_files' directory does not exist.")

    # Get a list of .txt files in the staged folder
    txt_files = [f for f in os.listdir(staged_folder) if f.endswith('.txt')]

    # If no .txt files found, raise an error
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the 'staged_files' directory.")

    # Process each .txt file by chunking it into smaller files
    doc_num = 1
    for file in txt_files:
        print(file)
        doc_num = chunk_file_and_save(os.path.join(staged_folder, file), doc_num)
        os.remove(os.path.join(staged_folder, file))  # Remove the processed .txt file