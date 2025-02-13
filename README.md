
# Win Wise- Wise insights for matches and league standings

## Overview
**WinWise** is a football league standings prediction system that uses machine learning (Poisson Regression) to simulate match results and predict final standings. The system consists of:
- **Backend**: Spring Boot (Handles file uploads and serves results)
- **Frontend**: React (Single-page form for uploading files and viewing results)
- **Machine Learning Microservice**: Python (Flask-based API for model training and predictions)

---

## Features
- ✅ Upload CSV/Excel files containing historical match data, current standings, and remaining fixtures.
- ✅ Runs a Poisson Regression model to predict match results.
- ✅ Generates a predicted league table based on simulated results.
- ✅ Simple frontend UI for file upload and viewing results.

---

## Tech Stack

### Backend (Spring Boot)
- Java + Spring Boot
- REST API for file upload and processing
- Handles communication between frontend and Python microservice

### Frontend (React.js)
- Single-page React app (all functionality in \`App.js\`)
- Axios for API communication
- Displays prediction results and visualizations

### Machine Learning (Python Flask)
- Poisson Regression for match predictions
- Uses Pandas, NumPy, SciPy, and Statsmodels
- Flask API to serve predictions

---

## Setup Guide

### 1. Backend (Spring Boot)

#### Prerequisites
- Java 17+
- Maven

#### Steps
1. Navigate to the Spring Boot directory:
 ```bash
   cd spring-boot-service
 ```
2. Build and run the Spring Boot server:
```bash
   mvn clean install
   mvn spring-boot:run
```
3. The backend will start at [http://localhost:8080](http://localhost:8080).

---

### 2. Frontend (React.js)

#### Prerequisites
- Node.js (Latest LTS version recommended)

#### Steps
1. Navigate to the React frontend directory:
```bash
   cd react-frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ````
3. Start the React app:
   ```bash
   npm start
    ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

### 3. Python Microservice (Flask)

#### Prerequisites
- Python 3.8+
- Virtualenv (Recommended)

#### Steps
1. Navigate to the Python microservice directory:
```bash
   cd python-ml-service
```
2. Create a virtual environment and activate it:
  ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
3. Install dependencies:
  ```bash
   pip install -r requirements.txt
 ```
4. Run the Flask server:
   ```bash
   python app.py
    ```
5. The Flask API will run at [http://localhost:5000](http://localhost:5000).

---

## API Endpoints

### Backend (Spring Boot)
| Method | Endpoint         | Description                          |
|--------|------------------|--------------------------------------|
| POST   | \`/api/upload\`    | Accepts CSV/XLSX file uploads        |

### Python (Flask)
| Method | Endpoint  | Description                                |
|--------|-----------|--------------------------------------------|
| POST   | \`/train\`  | Receives files and runs the Poisson model  |

---

## Usage

1. Open the **frontend** at [http://localhost:3000](http://localhost:3000).
2. Upload the required files:
   - **File 1:** Historical match data (e.g., \`results.csv\`) with columns like \`HomeTeam\`, \`AwayTeam\`, \`FTHG\`, and \`FTAG\`.
   - **File 2:** Current standings (e.g., \`Points_table_2025.xlsx\`) with columns \`Team\`, \`P\`, \`W\`, \`D\`, \`L\`, \`F\`, \`A\`, \`GD\`, and \`Points\`.
   - **File 3:** Remaining fixtures (e.g., \`Matches_left.xlsx\` or CSV) with columns \`HomeTeam\` and \`AwayTeam\`.
3. Click **Submit** to start processing.
4. View the predicted standings and visualizations on the same page.

---

## Future Enhancements
- Improve model accuracy with additional features.
- Add user authentication for file uploads.
- Enhance the frontend UI with more advanced visualizations.
- Deploy the system to cloud platforms for broader access.

---

## License
This project is licensed under the MIT License.

---

Enjoy using **WinWise**! ⚽🔥

