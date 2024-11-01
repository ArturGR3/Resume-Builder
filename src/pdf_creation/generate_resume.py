import json
import os
from jinja2 import Environment, FileSystemLoader
import subprocess
import argparse


def json_preparation_for_latex(data):
    """
    This function prepares the JSON data for LaTeX by escaping special characters and ensuring that the data is properly structured.
    """
    if isinstance(data, dict):
        new_data = {}
        for key in data.keys():
            new_data[key] = json_preparation_for_latex(data[key])
        return new_data
    elif isinstance(data, list):
        return [json_preparation_for_latex(item) for item in data]
    elif isinstance(data, str):
        latex_special_chars = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\^{}",
            "\\": r"\textbackslash{}",
            "\n": "\\newline%\n",
            "-": r"{-}",
            "\xA0": "~",  # Non-breaking space
            "[": r"{[}",
            "]": r"{]}",
        }
        return "".join([latex_special_chars.get(c, c) for c in data])

    return data

# os.getcwd()
# # example usage:
# path_json ="tailored_resume.json"
# with open(path_json, 'r') as f:
#     resume_data = json.load(f)

# test = escape_for_latex(resume_data)

def generate_resume(json_file_path, output_name=None):
    """
    This function generates a PDF resume from a JSON data file.
    """
    # Load JSON data
    with open(json_file_path, 'r') as f:
        resume_data = json.load(f)
    
    # Get the directory path from json_file_path
    result_dir = os.path.dirname(json_file_path)
    
    # Extract last name from contact info and use it for output_name if not provided
    if output_name is None:
        full_name = resume_data.get('contact_info', {}).get('name', '')
        last_name = full_name.split()[-1] if full_name else 'resume'
        output_name = f'resume_{last_name}'
    
    # Set up Jinja environment
    env = Environment(
        loader=FileSystemLoader('src/pdf_creation/resume_templates'),
        block_start_string='\\BLOCK{',  # Fixed escape sequence
        block_end_string='}',
        variable_start_string='\\VAR{',  # Fixed escape sequence
        variable_end_string='}',
        comment_start_string='\\#{',     # Fixed escape sequence
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
    ) # This environment is used to render the LaTeX template with the JSON data.
    
    # Load template
    template = env.get_template('resume.tex.jinja')
    
    # Render template with data
    output_tex = template.render(**json_preparation_for_latex(resume_data))
    
    # Write TEX file
    tex_path = f'{result_dir}/{output_name}.tex' 
    pdf_path = f'{result_dir}/{output_name}.pdf'
    
    # Copy resume.cls to result directory
    cls_source = os.path.join('src/pdf_creation/resume_templates', 'resume.cls')
    cls_dest = os.path.join(result_dir, 'resume.cls')
    with open(cls_source, 'r') as source, open(cls_dest, 'w') as dest:
        dest.write(source.read())
    
    # Write TEX file
    with open(tex_path, 'w') as f:
        f.write(output_tex)
    
    # Compile TEX to PDF
    try:
        # Change to result directory before running pdflatex
        current_dir = os.getcwd()
        os.chdir(result_dir)
        
        # Run pdflatex twice to ensure proper rendering of all elements
        subprocess.run(['pdflatex', f'{output_name}.tex'], check=True)
        subprocess.run(['pdflatex', f'{output_name}.tex'], check=True)
        
        # Change back to original directory
        os.chdir(current_dir)
        
        # Clean up auxiliary files
        for ext in ['.aux', '.log', '.out', '.cls', '.tex']:
            aux_file = os.path.join(result_dir, f'{output_name}{ext}')
            if os.path.exists(aux_file):
                os.remove(aux_file)
        
        print(f"PDF generated successfully: {pdf_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating PDF: {e}")
        os.chdir(current_dir)  # Ensure we return to original directory even if error occurs
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a PDF resume from JSON data')
    parser.add_argument('json_path', help='Path to the JSON resume data file')
    parser.add_argument('--output', '-o', help='Output filename (without extension)')
    
    args = parser.parse_args()
    generate_resume(args.json_path, args.output)