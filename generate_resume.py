import json
import os
from jinja2 import Environment, FileSystemLoader
import subprocess

def generate_resume(json_file_path):
    # Load JSON data
    with open(json_file_path, 'r') as f:
        resume_data = json.load(f)
    
    # Set up Jinja environment
    env = Environment(
        loader=FileSystemLoader('templates'),
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
    )
    
    # Load template
    template = env.get_template('resume.tex.jinja')
    
    # Render template with data
    output_tex = template.render(**resume_data)
    
    # Write TEX file
    output_filename = os.path.splitext(os.path.basename(json_file_path))[0]
    tex_path = f'output/{output_filename}.tex'
    pdf_path = f'output/{output_filename}.pdf'
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Copy resume.cls to output directory
    cls_source = os.path.join('templates', 'resume.cls')
    cls_dest = os.path.join('output', 'resume.cls')
    with open(cls_source, 'r') as source, open(cls_dest, 'w') as dest:
        dest.write(source.read())
    
    # Write TEX file
    with open(tex_path, 'w') as f:
        f.write(output_tex)
    
    # Compile TEX to PDF
    try:
        # Change to output directory before running pdflatex
        current_dir = os.getcwd()
        os.chdir('output')
        
        # Run pdflatex twice to ensure proper rendering of all elements
        subprocess.run(['pdflatex', os.path.basename(tex_path)], check=True)
        subprocess.run(['pdflatex', os.path.basename(tex_path)], check=True)
        
        # Change back to original directory
        os.chdir(current_dir)
        
        # Clean up auxiliary files
        for ext in ['.aux', '.log', '.out']:
            aux_file = f'output/{output_filename}{ext}'
            if os.path.exists(aux_file):
                os.remove(aux_file)
        
        print(f"PDF generated successfully: {pdf_path}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating PDF: {e}")
        os.chdir(current_dir)  # Ensure we return to original directory even if error occurs
        
if __name__ == "__main__":
    generate_resume('Staff Machine Learning Engineer, Gen AI_2024-10-28.json')
