# FixKaohsiung

An automated utility for reporting traffic violations in Kaohsiung City, Taiwan.

## Description

FixKaohsiung is a Python-based automation tool designed to simplify the process of reporting illegal parking and traffic violations to local authorities in Kaohsiung. The project uses computer vision, optical character recognition (OCR), and web automation to streamline the reporting process.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Directory Structure](#directory-structure)
- [License](#license)

## Features

- **Automated Image Processing**: Automatically processes and timestamps images of traffic violations
- **License Plate Recognition**: Uses AI to detect and read vehicle license plates
- **Location Extraction**: Extracts GPS coordinates from image EXIF data and converts to addresses
- **Form Automation**: Automatically fills and submits violation reports
- **Email Verification**: Handles the verification emails after submission

## Prerequisites

- Python 3.8+
- Chrome browser (for Selenium automation)
- Google Maps API key (for location services)
- Valid email account (for verification handling)

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/FixKaohsiung.git
   cd FixKaohsiung
   ```

2. Create a virtual environment:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (or update `src/config.py`):
   ```
   export IMAP_HOST="your-email-host.com"
   export IMAP_PORT="993"
   export IMAP_USER="your-email@example.com"
   export IMAP_PASSWORD="your-email-password"
   ```

## Configuration

Important configuration files:

- `src/config.py`: Main configuration file with constants and settings
- Email settings: Set your email credentials for verification handling
- Personal information: Update the `personal_info` object in `src/data_handling/schemas.py`

## Usage

1. Place violation photo(s) in the `data/original` directory

2. Run the program:

   ```
   python -m src.main
   ```

3. Follow the interactive prompts:
   - Confirm or enter license plate information
   - Review and confirm the report details
   - The program will automatically submit the report and handle email verification

## How It Works

The reporting process follows these steps:

1. **Image Processing**: Photos are converted to JPEG format and timestamped
2. **Data Collection**:
   - Extract time from image metadata
   - Detect license plate using YOLO model
   - Extract location from image EXIF data (if available)
3. **Report Submission**:
   - Automatically fill forms on the reporting website
   - Upload processed images
   - Solve CAPTCHA using OCR
   - Submit the report
4. **Email Verification**:
   - Monitor the inbox for verification emails
   - Automatically click verification links
   - Clean up processed emails

## Directory Structure

```
FixKaohsiung/
├── assets/                  # Static assets
│   ├── fonts/               # Fonts for image processing
│   ├── models/              # ML models for license plate detection
│   └── chromedriver-mac-x64/ # WebDriver for Selenium
├── data/                    # Data directories
│   ├── original/            # Input photos placed here
│   └── processed/           # Processed images
├── src/
│   ├── core/                # Core functionality
│   ├── data_handling/       # Image and data processing
│   └── utils/               # Utility functions
├── LICENSE                  # GNU GPL v3 license
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
