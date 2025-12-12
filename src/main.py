from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

def parse_mus(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Parser simple: detecta título, secciones y acordes
    title = "Sin título"
    sections = []
    current_section = {"type": "verse", "lines": []}
    
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            title = line[2:]
        elif line.startswith("Verse"):
            if current_section["lines"]:
                sections.append(current_section)
            current_section = {"type": "verse", "lines": []}
        elif line.startswith("Chorus"):
            if current_section["lines"]:
                sections.append(current_section)
            current_section = {"type": "chorus", "lines": []}
        elif line:
            # Línea de acordes o letra
            current_section["lines"].append(line)
    
    if current_section["lines"]:
        sections.append(current_section)
    
    return {"title": title, "sections": sections}

def generate_html(data, css_custom=None):
    # Template HTML básico
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{{ title }}</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: {{ bg_color }}; color: {{ text_color }}; }
            h1 { text-align: center; color: {{ title_color }}; }
            .section { margin-bottom: 30px; }
            .chorus { background: {{ chorus_bg }}; padding: 10px; border-left: 5px solid {{ chorus_border }}; }
            .chords { font-weight: bold; color: {{ chord_color }}; font-size: 1.2em; }
            .lyrics { margin-left: 20px; color: {{ lyric_color }}; }
            pre { white-space: pre-wrap; font-family: monospace; line-height: 2; }
        </style>
        {% if css_custom %}
        <style>{{ css_custom }}</style>
        {% endif %}
    </head>
    <body>
        <h1>{{ title }}</h1>
        {% for sec in sections %}
        <div class="section {{ sec.type }}">
            {% for line in sec.lines %}
            <pre>
                {% if '[' in line %}
                <span class="chords">{{ line }}</span>
                {% else %}
                <span class="lyrics">{{ line }}</span>
                {% endif %}
            </pre>
            {% endfor %}
        </div>
        {% endfor %}
    </body>
    </html>
    """
    
    env = Environment()
    template = env.from_string(html_template)
    
    # Colores personalizados (puedes pasar un dict o leer de config)
    colors = {
        "bg_color": "#ffffff",
        "text_color": "#000000",
        "title_color": "#3333ff",
        "chord_color": "#ff0000",   # Acordes en rojo
        "lyric_color": "#000000",
        "chorus_bg": "#f0f0f0",
        "chorus_border": "#0066cc"
    }
    
    return template.render(title=data["title"], sections=data["sections"], **colors)

def mus_to_pdf(mus_path, pdf_path, css_custom=None):
    data = parse_mus(mus_path)
    html_content = generate_html(data, css_custom)
    
    # Opcional: guardar HTML para debug
    with open("temp.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    HTML(string=html_content).write_pdf(pdf_path)

# Uso
mus_to_pdf("mi_cancion.mus", "mi_cancion.pdf")