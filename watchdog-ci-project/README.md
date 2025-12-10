# Watchdog CI Project

## Overview
The Watchdog CI Project is designed to monitor and automatically restart FastAPI and Streamlit services in case they crash, hang, or respond slowly. This project utilizes a watchdog script that checks the health of the services, manages their lifecycle, and logs activities for troubleshooting.

## Project Structure
```
watchdog-ci-project
├── .github
│   └── workflows
│       └── watchdog.yml        # CI/CD configuration for GitHub Actions
├── scripts
│   └── watchdog.sh              # Watchdog script for monitoring services
├── logs
│   └── .gitkeep                 # Keeps the logs directory tracked by Git
├── src
│   ├── main.py                  # FastAPI application code
│   └── streamlit_app.py         # Streamlit application code
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

## Setup Instructions
1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd watchdog-ci-project
   ```

2. **Install Dependencies**
   Ensure you have Python and pip installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Watchdog Script**
   The watchdog script can be executed to start monitoring the services:
   ```bash
   bash scripts/watchdog.sh
   ```

## Usage
- The watchdog script will automatically restart the FastAPI and Streamlit services if they are unresponsive or exceed memory usage thresholds.
- Logs of the watchdog activities can be found in the `logs/watchdog.log` file.

## CI/CD Integration
The project includes a GitHub Actions workflow defined in `.github/workflows/watchdog.yml` that automates the monitoring process. This ensures that the watchdog script runs on specified triggers, maintaining the availability of the services.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.