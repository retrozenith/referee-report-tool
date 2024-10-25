import os
from flask import Flask, render_template, request, send_file
from io import BytesIO
from pdfrw import PdfFileReader, PdfFileWriter, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = './reports'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

pdfmetrics.registerFont(TTFont('Roboto-Medium', './fonts/Roboto-Medium.ttf'))

# Render the form where the user can fill out referee information
@app.route('/')
def index():
    return render_template('index.html')

# Handle the form submission
@app.route('/generate_report', methods=['POST'])
def generate_report():
    # Get form data
    referee_name_1 = request.form['referee_name_1']
    referee_name_2 = request.form['referee_name_2']
    match_date = request.form['match_date']
    starting_hour = request.form['starting_hour']
    team_1 = request.form['team_1']
    team_2 = request.form['team_2']
    competition = request.form['competition']
    assistant_referee_1 = request.form['assistant_referee_1']
    assistant_referee_2 = request.form['assistant_referee_2']
    fourth_official = request.form['fourth_official']
    age_category = request.form['age_category']
    stadium_name = request.form.get('stadium_name')  # Este opțional
    stadium_locality = request.form.get('stadium_locality')  # Este opțional

    # Determine the template based on age category
    if age_category == 'U9':
        template_filename = 'referee_template_u9.pdf'  # Template for U9
    elif age_category == 'U11':
        template_filename = 'referee_template_u11.pdf'  # Template for U11
    elif age_category == 'U13':
        template_filename = 'referee_template_u13.pdf'  # Template for U13
    elif age_category == 'U15':
        template_filename = 'referee_template_u15.pdf'  # Template for U15
    else:
        return "Invalid age category", 400  # Error handling for unsupported categories

    template_path = os.path.join(app.config['UPLOAD_FOLDER'], template_filename)

    # Generate the filled PDF
    output_pdf = fill_pdf(template_path, referee_name_1, referee_name_2, match_date, 
                          starting_hour, team_1, team_2, competition,
                          assistant_referee_1, assistant_referee_2, fourth_official, age_category, stadium_locality, stadium_name)
    
    # Return the PDF as a download
    return send_file(output_pdf, as_attachment=True, download_name="referee_report.pdf")

# Function to format date as 'day month'
def format_date_dm(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Convert the input date string to a datetime object
    return date_obj.strftime('%d %m')  # Format it as "day.month"

# Function to format date as 'day.month.year'
def format_date_dmy(date_str):
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')  # Convert the input date string to a datetime object
    return date_obj.strftime('%d.%m.%Y')  # Format it as "day.month.year"

# Function to fill the PDF using pdfrw and ReportLab
def fill_pdf(template_path, referee_name_1, referee_name_2, match_date, starting_hour, team_1, team_2, 
             competition, assistant_referee_1, assistant_referee_2, fourth_official, age_category, stadium_locality, stadium_name):

    # Create an overlay PDF with the text to be placed on the template
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Set Text font to Roboto (Roboto-Medium)
    can.setFont('Roboto-Medium', 13)

    # Fill in the referee and match details based on age category
    if age_category == 'U9':
        # Format the date to "day month"
        formatted_date = format_date_dm(match_date)
        # For U9, only add Referee 1, Match Date, and Teams
        can.drawString(101, 687, f"{referee_name_1}")  # Referee 1
        can.drawString(346, 686, f"{formatted_date}")
        can.drawString(101, 712, f"{team_1} - {team_2}")
        can.drawString(355, 636, f"{team_2}")
        can.drawString(101, 636, f"{team_1}")

    elif age_category == 'U11' or age_category == 'U13':
        
        # Format the date to "day month"
        formatted_date = format_date_dm(match_date)
        # For U11 and U13, only add Referee 1, Referee 2, Match Date, Starting Hour, and Teams
        can.drawString(101, 687, f"{referee_name_1}")  # Referee 1
        can.drawString(101, 662, f"{referee_name_2}")  # Referee 2
        can.drawString(346, 686, f"{formatted_date}")
        can.drawString(335, 660, f"{starting_hour}")
        can.drawString(101, 712, f"{team_1} - {team_2}")
        can.drawString(355, 636, f"{team_2}")
        can.drawString(101, 636, f"{team_1}")

    #elif age_category == 'U15':
    else:

        # Format the date to "day month"
        formatted_date = format_date_dmy(match_date)
        # For U15, add all details including competition and officials
        can.drawString(163, 353, f"{referee_name_1}")  # Referee 1
        can.drawString(390, 425, f"{formatted_date}")
        can.drawString(510, 425, f"{starting_hour}")
        can.drawString(110, 515, f"{team_1} - {team_2}")
        can.drawString(110, 455, f"{competition}")  # Competition field
        can.drawString(163, 338, f"{assistant_referee_1}")  # Assistant Referee 1
        can.drawString(163, 321, f"{assistant_referee_2}")  # Assistant Referee 2
        can.drawString(163, 306, f"{fourth_official}")  # 4th Match Official

        can.drawString(163, 426, f"{stadium_locality}")
        can.drawString(159, 399, f"{stadium_name}")

        # Add fixed location text for all reports (e.g., location)
        can.drawString(490, 353, f"Ilfov")
        can.drawString(490, 337, f"Ilfov")
        can.drawString(490, 322, f"Ilfov")
        can.drawString(490, 306, f"Ilfov")

    can.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)

    # Read the existing PDF
    existing_pdf = PdfFileReader(template_path)
    overlay_pdf = PdfFileReader(packet)

    # Create a writer for the output PDF
    output = BytesIO()
    writer = PdfFileWriter()

    # Merge the overlay only on specific pages
    for page_num, page in enumerate(existing_pdf.pages):\
        # For the first page, apply the original overlay with referee and match info
        if page_num == 0:  # Page 1
            overlay_page = overlay_pdf.pages[0]  # First page of overlay (already created)
            PageMerge(page).add(overlay_page).render()

        elif page_num == 4:  # Page 4 (page_num starts from 0)
            pdfmetrics.registerFont(TTFont('Roboto-Medium', './fonts/Roboto-Medium.ttf'))
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFont('Roboto-Medium', 13)
            can.drawString(90, 78, f"{formatted_date}")  # Adjust coordinates for Page 5
            can.save()
            packet.seek(0)
            team1_overlay_pdf = PdfFileReader(packet)
            overlay_page = team1_overlay_pdf.pages[0]
            PageMerge(page).add(overlay_page).render()

        # For page 5, overlay only TEAM1
        elif page_num == 5:  # Page 5 (page_num starts from 0)
            pdfmetrics.registerFont(TTFont('Roboto-Medium', './fonts/Roboto-Medium.ttf'))
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFont('Roboto-Medium', 13)
            can.drawString(150, 783, f"{team_1}")  # Adjust coordinates for Page 5
            can.save()
            packet.seek(0)
            team1_overlay_pdf = PdfFileReader(packet)
            overlay_page = team1_overlay_pdf.pages[0]
            PageMerge(page).add(overlay_page).render()

        # For page 6, overlay only TEAM2
        elif page_num == 6:  # Page 6
            pdfmetrics.registerFont(TTFont('Roboto-Medium', './fonts/Roboto-Medium.ttf'))
            packet = BytesIO()
            can = canvas.Canvas(packet, pagesize=letter)
            can.setFont('Roboto-Medium', 13)
            can.drawString(160, 783, f"{team_2}")  # Adjust coordinates for Page 6
            can.save()
            packet.seek(0)
            team2_overlay_pdf = PdfFileReader(packet)
            overlay_page = team2_overlay_pdf.pages[0]
            PageMerge(page).add(overlay_page).render() 

        # Add the page (with or without overlay) to the writer
        writer.addpage(page)

    # Write the output to a new PDF
    writer.write(output)
    output.seek(0)

    return output

if __name__ == '__main__':
    app.run(debug=True)
