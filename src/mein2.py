import os
from jinja2 import Environment
from weasyprint import HTML

# Ruta absoluta a la carpeta de imágenes (sube un nivel desde src/)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER_ABS = os.path.join(SCRIPT_DIR, "..", "imagenes")
IMAGES_FOLDER_REL = "imagenes"  # para usar en HTML (WeasyPrint lo resolverá con base_url)

def parse_mus(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = [line.strip() for line in content.splitlines() if line.strip()]

    title = "Sin título"
    estructura = []
    definiciones = {}
    mode = None

    for line in lines:
        if line.startswith("Título:"):
            title = line[len("Título:"):].strip()
        elif line == "Estructura:":
            mode = "estructura"
        elif line == "Definiciones:":
            mode = "definiciones"
        elif mode == "estructura" and line:
            estructura = [sec.strip() for sec in line.split()]
        elif mode == "definiciones" and "=" in line:
            key, prog = line.split("=", 1)
            grados = [g.strip() for g in prog.split()]
            definiciones[key.strip()] = grados

    return {
        "title": title,
        "estructura": estructura,
        "definiciones": definiciones
    }

def expand_progression(estructura, definiciones):
    expanded = []
    for sec in estructura:
        chords = definiciones.get(sec, [])
        expanded.append({"type": sec, "chords": chords})
    return expanded

def generate_html(data):
    template_str = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <title>{{ title }}</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                margin: 40px auto;
                max-width: 900px;
                background: #fffff0;
                padding: 20px;
            }
            h1 {
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 60px;
                color: #333;
            }
            .sections {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 50px;
            }
            .section {
                text-align: center;
                min-width: 200px;
            }
            .section-label {
                font-size: 2.2em;
                font-weight: bold;
                margin-bottom: 25px;
                color: #d32f2f;
                height: 60px; /* reserva espacio para futuro SVG de sección */
            }
            .chord-line {
                display: flex;
                justify-content: center;
                align-items: center;
                flex-wrap: wrap;
                gap: 30px;
            }
            .chord-svg {
                width: 70px;
                height: 90px;
            }
            .separator-svg {
                width: 25px;
                height: 80px;
                opacity: 0.7;
            }
        </style>
    </head>
    <body>
        <h1>{{ title }}</h1>
        <div class="sections">
            {% for sec in progression %}
            <div class="section">
                <div class="section-label">{{ sec.type }}</div>
                <div class="chord-line">
                    {% for i in range(sec.chords|length) %}
                        {% set chord = sec.chords[i] %}
                        <img src="{{ images_folder }}/{{ chord }}.svg" class="chord-svg" alt="{{ chord }}">
                        {% if i < sec.chords|length - 1 %}
                        <img src="{{ images_folder }}/palos.svg" class="separator-svg" alt="|">
                        {% endif %}
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
    </body>
    </html>
    """

    env = Environment()
    template = env.from_string(template_str)

    return template.render(
        title=data["title"],
        progression=expand_progression(data["estructura"], data["definiciones"]),
        images_folder=IMAGES_FOLDER_REL
    )

def mus_to_pdf(mus_path, pdf_path):
    data = parse_mus(mus_path)
    html_content = generate_html(data)

    # Guardar HTML temporal para debug (opcional)
    debug_html = os.path.join(os.path.dirname(mus_path), "debug.html")
    with open(debug_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    # IMPORTANTE: base_url apunta a la carpeta raíz del proyecto para resolver rutas relativas
    base_url = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

    HTML(string=html_content, base_url=base_url).write_pdf(pdf_path)
    print(f"¡PDF generado correctamente: {pdf_path}")

# ======================
if __name__ == "__main__":
    # Ajusta estas rutas según donde tengas el .mus
    mus_file = "mi_cancion.mus"  # o la ruta que uses
    # Si lo tienes en otro sitio, cámbialo directamente:
    # mus_file = r"C:\ruta\completa\mi_cancion.mus"

    output_pdf = os.path.join(SCRIPT_DIR, "..", "output", "Mi_Cancion_Bonita.pdf")
    os.makedirs(os.path.dirname(output_pdf), exist_ok=True)

    mus_to_pdf(mus_file, output_pdf)