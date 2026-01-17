# Program Evaluation Database System

## 🚀 Overview
This project is a comprehensive database solution designed to manage and evaluate academic degree programs. It enables university departments to track learning objectives, course sections, and instructor evaluations through a structured relational backend.

**Key Technical Highlight:
* Relational Schema Design: Engineered an 11-table schema to handle complex "diamond" relationships between Degrees, Courses, and Objectives.
* Soft Delete Strategy: Implemented a non-destructive data archiving system using status columns (Active/Inactive) to preserve historical reporting integrity for retired courses or faculty.
* Automated DDL Pipeline: Created a Python automation script that programmatically builds the entire relational structure, ensuring consistent deployment across environments.
* Data Integrity Validation: Developed server-side logic to ensure grade distributions (A, B, C, F) precisely match official enrollment figures.

## 🛠️ Tech Stack
* **Language:** Python 3.x [cite: 259]
* **Framework:** Flask (Web GUI) [cite: 283, 292]
* **Database:** MySQL / MariaDB [cite: 258]
* **Connector:** mysql-connector-python 

## 📊 Database Architecture
The system utilizes a complex relational schema consisting of **11 tables** designed to handle many-to-many relationships, such as courses satisfying different objectives across multiple degrees. 

### Core Schema Components:
* **Degree & Course Management:** Uniquely identifies programs by name and level (BS, MS, etc.). 
* **Learning Objectives:** Maps specific goals to courses and degrees via "diamond" relationships. 
* **Evaluation Engine:** Tracks aggregated student performance (Grades A-F) and correlates them to specific assessment methods like "Quizzes" or "Final Exams." 
* **Data Integrity:** Employs `ON DELETE CASCADE` and status-based "Soft Deletes" to maintain historical report accuracy. 

## 🛠️ Tech Stack

* Database: MySQL / MariaDB.
* Backend: Python 3.x.
* Web Framework: Flask.
* Interface: Browser-based GUI.

## ⚙️ Installation & Setup

1. Prerequisites 
Before setting up the project, ensure your computer has the following installed: 
* MySQL Server: The database engine where data will be stored. (Download the "MySQL Community Server" version). 
* Python 3.x: The programming language used for the application. 
* MySQL Workbench: (Optional) A visual tool to verify your database exists. 

2. Installation Steps 
Step A: Create the Database Shell 
   1. Open MySQL Workbench (or your command line interface). 
   2. Connect to your local MySQL instance. 
   3. Open a new query tab and run this single command to create the empty container for 
   our system: 
      CREATE DATABASE program_eval; 
      Note: You do not need to create tables manually. We have a Python automation script for that.
      
Step B: Configure the Project 
   1. Open the project folder called GradGroup20_Project. 
   2. Locate the file named config.ini in the root folder. 
   3. Open it with a text editor (Notepad, VS Code) and update the settings to match your 
      MySQL credentials: 
      [mysql] 
      host = localhost 
      user = root <-- Your MySQL username (usually 'root') 
      password = yourpassword <-- The password you created during MySQL installation 
      database = program_eval <-- The exact name you used in Step A
      
Step C: Install Python Libraries 
   1. Open your terminal (Command Prompt or PowerShell). 
   2. Navigate to the project folder: 
   cd path/to/project_folder 
   3. Install the required connectors using pip: 
   pip install flask mysql-connector-python

Step D: Initialize the Database (Automation) 
   1. This project uses a dedicated Python script to build the entire database schema 
   automatically. 
   2. In your terminal, run: 
   python Create_Tables.py 
   3. Success Check: Watch the terminal output. You should see the message: Tables 
   checked/created. 
      * What just happened? This script connected to your database and ran the CREATE 
      TABLE IF NOT EXISTS commands for all 11 tables (Degree, Course, Instructor, etc.) 
      defined in our schema.

Step E: Launch the Application 
   1. Start the web server by running the main application file: 
   python app.py 
   2. You will see a confirmation message indicating the server is active (usually Running on 
   http://127.0.0.1:5000). 
   3. Open your web browser (Chrome, Firefox, etc.) and type that URL into the address bar to 
   access the system.

1. **Database Creation:**
   Connect to your MySQL instance and run:
   ```sql
   CREATE DATABASE program_eval;
   ``` [cite: 266]

2. **Configuration:**
   [cite_start]Update the `config.ini` file in the root directory with your MySQL credentials (host, user, password). [cite: 270, 271, 272]

3. **Dependency Installation:**
   ```bash
   pip install -r requirements.txt
   [cite_start]``` 

4. **Schema Initialization:**
   Run the automation script to build all 11 tables:
   ```bash
   python Create_Tables.py
   [cite_start]``` [cite: 287, 289]

5. **Launch:**
   ```bash
   python app.py
