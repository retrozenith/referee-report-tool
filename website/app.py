import os
from flask import Flask, render_template, request, send_file
from io import BytesIO
from pdfrw import PdfFileReader, PdfFileWriter, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime

# ---------- Configurare aplicație Flask ----------
app = Flask(__name__)

UPLOAD_FOLDER = './reports'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Înregistrare font personalizat
pdfmetrics.registerFont(TTFont('Roboto-Medium', './fonts/Roboto-Medium.ttf'))


# ---------- Rute ----------

@app.route('/')
def index():
    """Afișează formularul în care utilizatorul poate completa informațiile despre arbitri."""
    return render_template('index.html')


@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Gestionează trimiterea formularului și generează raportul PDF."""
    # Extrage datele din formular
    form_data = extract_form_data(request)

    # Determină șablonul pe baza categoriei de vârstă
    template_filename = determine_template(form_data['age_category'])
    if not template_filename:
        return "Categorie de vârstă invalidă", 400

    template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_filename)

    # Generează PDF-ul completat
    output_pdf = fill_pdf(template_path, **form_data)

    # Trimite PDF-ul ca fișier descărcabil
    return send_file(output_pdf, as_attachment=True, download_name="referee_report.pdf")


# ---------- Funcții Ajutătoare ----------

def extract_form_data(request):
    """Extrage datele din formular."""
    return {
        'referee_name_1': request.form['referee_name_1'],
        'referee_name_2': request.form['referee_name_2'],
        'match_date': request.form['match_date'],
        'starting_hour': request.form['starting_hour'],
        'team_1': request.form['team_1'],
        'team_2': request.form['team_2'],
        'competition': request.form['competition'],
        'assistant_referee_1': request.form['assistant_referee_1'],
        'assistant_referee_2': request.form['assistant_referee_2'],
        'fourth_official': request.form['fourth_official'],
        'age_category': request.form['age_category'],
        'stadium_name': request.form.get('stadium_name', ''),
        'stadium_locality': request.form.get('stadium_locality', '')
    }


def determine_template(age_category):
    """Determină fișierul șablon pe baza categoriei de vârstă."""
    templates = {
        'U9': 'referee_template_u9.pdf',
        'U11': 'referee_template_u11.pdf',
        'U13': 'referee_template_u13.pdf',
        'U15': 'referee_template_u15.pdf'
    }
    return templates.get(age_category)


def format_date_dm(date_str):
    """Formatează o dată ca 'zi lună'."""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%d %m')


def format_date_dmy(date_str):
    """Formatează o dată ca 'zi.lună.an'."""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%d.%m.%Y')


def fill_pdf(template_path, **kwargs):
    """Completează șablonul PDF cu datele furnizate."""
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont('Roboto-Medium', 13)

    # Adaugă conținut în PDF-ul de suprapunere
    fill_pdf_content(can, **kwargs)
    can.save()

    packet.seek(0)
    overlay_pdf = PdfFileReader(packet)
    existing_pdf = PdfFileReader(template_path)

    output = BytesIO()
    writer = PdfFileWriter()

    # Suprapune paginile specifice
    for page_num, page in enumerate(existing_pdf.pages):
        if page_num == 0:  # Prima pagină: Adaugă suprapunerea principală
            overlay_page = overlay_pdf.pages[0]
            PageMerge(page).add(overlay_page).render()

        elif page_num == 4:  # Pagina 4: Adaugă suprapunerea personalizată pentru dată
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFont('Roboto-Medium', 13)
            formatted_date = format_date_dm(kwargs['match_date'])
            can.drawString(90, 78, f"{formatted_date}")  # Ajustează coordonatele pentru Pagina 4
            can.save()
            packet.seek(0)
            custom_overlay_pdf = PdfFileReader(packet)
            overlay_page = custom_overlay_pdf.pages[0]
            PageMerge(page).add(overlay_page).render()

        elif page_num == 5:  # Pagina 5: Suprapunere doar pentru TEAM1
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFont('Roboto-Medium', 13)
            can.drawString(150, 783, f"{kwargs['team_1']}")  # Ajustează coordonatele pentru Pagina 5
            can.save()
            packet.seek(0)
            team1_overlay_pdf = PdfFileReader(packet)
            overlay_page = team1_overlay_pdf.pages[0]
            PageMerge(page).add(overlay_page).render()

        elif page_num == 6:  # Pagina 6: Suprapunere doar pentru TEAM2
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFont('Roboto-Medium', 13)
            can.drawString(160, 783, f"{kwargs['team_2']}")  # Ajustează coordonatele pentru Pagina 6
            can.save()
            packet.seek(0)
            team2_overlay_pdf = PdfFileReader(packet)
            overlay_page = team2_overlay_pdf.pages[0]
            PageMerge(page).add(overlay_page).render()

        # Adaugă pagina actualizată în writer
        writer.addpage(page)

    # Scrie PDF-ul final
    writer.write(output)
    output.seek(0)

    return output


def fill_pdf_content(can, **kwargs):
    """Adaugă conținut specific în PDF pe baza categoriei de vârstă."""
    age_category = kwargs['age_category']
    match_date = kwargs['match_date']
    team_1 = kwargs['team_1']
    team_2 = kwargs['team_2']
    starting_hour = kwargs['starting_hour']
    referee_name_1 = kwargs['referee_name_1']
    referee_name_2 = kwargs['referee_name_2']
    competition = kwargs['competition']
    assistant_referee_1 = kwargs['assistant_referee_1']
    assistant_referee_2 = kwargs['assistant_referee_2']
    fourth_official = kwargs['fourth_official']
    stadium_name = kwargs['stadium_name']
    stadium_locality = kwargs['stadium_locality']

    if age_category == 'U9':
        # Formatează data în format "zi lună"
        formatted_date = format_date_dm(match_date)
        # Pentru U9, adaugă Arbitrul 1, Data meciului, Echipele și Competiția
        can.drawString(101, 687, f"{referee_name_1}")  # Arbitrul 1
        can.drawString(346, 686, f"{formatted_date}")
        can.drawString(101, 712, f"{team_1} - {team_2}")
        can.drawString(355, 636, f"{team_2}")
        can.drawString(101, 636, f"{team_1}")

    elif age_category in ['U11', 'U13']:
        # Formatează data în format "zi lună"
        formatted_date = format_date_dm(match_date)
        # Pentru U11 și U13, adaugă Arbitrul 1, Arbitrul 2, Data meciului, Ora de începere, Echipele și Competiția
        can.drawString(101, 687, f"{referee_name_1}")  # Arbitrul 1
        can.drawString(101, 662, f"{referee_name_2}")  # Arbitrul 2
        can.drawString(346, 686, f"{formatted_date}")
        can.drawString(335, 660, f"{starting_hour}")
        can.drawString(101, 712, f"{team_1} - {team_2}")
        can.drawString(355, 636, f"{team_2}")
        can.drawString(101, 636, f"{team_1}")

    else:  # U15
        # Formatează data în format "zi.lună.an"
        formatted_date = format_date_dmy(match_date)
        # Pentru U15, adaugă toate detaliile, inclusiv competiția și oficialii
        can.drawString(163, 353, f"{referee_name_1}")  # Arbitrul 1
        can.drawString(390, 425, f"{formatted_date}")
        can.drawString(510, 425, f"{starting_hour}")
        can.drawString(110, 515, f"{team_1} - {team_2}")
        can.drawString(110, 455, f"{competition}")  # Câmpul pentru competiție
        can.drawString(163, 338, f"{assistant_referee_1}")  # Arbitrul asistent 1
        can.drawString(163, 321, f"{assistant_referee_2}")  # Arbitrul asistent 2
        can.drawString(163, 306, f"{fourth_official}")  # Al 4-lea oficial de meci

        can.drawString(163, 426, f"{stadium_locality}")
        can.drawString(159, 399, f"{stadium_name}")

        # Adaugă text fix pentru toate rapoartele (ex.: locația)
        can.drawString(490, 353, f"Ilfov")
        can.drawString(490, 337, f"Ilfov")
        can.drawString(490, 322, f"Ilfov")
        can.drawString(490, 306, f"Ilfov")


# ---------- Punctul Principal de Intrare ----------

if __name__ == '__main__':
    # Asigură-te că folderul de upload există
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Rulează aplicația Flask
    app.run(debug=True)
