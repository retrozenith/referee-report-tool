# Referee Report Generator Tool

This project is a web-based tool designed for generating and managing referee reports for football matches. It allows users to enter relevant match data, referee details, and team information to generate a detailed report based on the specific match age category (U9, U11, U13, U15, etc.). The tool is specifically built for referees working with AJF Ilfov.

---

## Features
- Supports multiple age categories (U9, U11, U13, U15+)
- Customizable report forms based on the age category
- Fields for referee names, match details, team names, competition, and more
- Dynamically hides or displays specific form fields based on the age category
- Responsive web design for mobile and desktop views
- Easy-to-use interface for quick report generation
- Multi-language support (Romanian and English)

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/glikched/referee-report-tool.git
   cd referee-report-tool
   ```
2. **Set up the environment:**
   - Make sure you have Python 3.12+ and a package manager like pip installed.
     
3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the web app locally:**
   ```bash
   gunicorn app:app
   ```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
