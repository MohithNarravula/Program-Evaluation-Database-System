# Program Evaluation Database System

## 🚀 Overview
This project is a comprehensive database solution designed to manage and evaluate academic degree programs. It enables university departments to track learning objectives, course sections, and instructor evaluations through a structured relational backend.

**Key Technical Highlight:
* Relational Schema Design: Engineered an 11-table schema to handle complex "diamond" relationships between Degrees, Courses, and Objectives.
* Soft Delete Strategy: 
   1. The Problem with Standard Deletion ("Hard Delete"): In a university context, permanently deleting records creates data integrity issues. For example, if a professor retires and their record is deleted, all        historical reports for courses they taught in previous years would break or show missing data. 
   2. The Solution: "Soft Delete" (Archiving) We implemented a Soft Delete strategy using a status column. 
      • Mechanism: Major tables (Instructor, Course, Degree) include a status column defaulting to 'Active'. 
      • Archiving: Clicking "Archive" runs an UPDATE command (setting status to 'Inactive') rather than a DELETE command. 
      • Benefits: 
         o Data Preservation: Historical reports remain accurate. 
         o User Interface: Dropdown menus filter out Inactive records for future assignments but allow them for historical data entry. 
         o Restoration: Records can be reactivated if needed.
* Automated DDL Pipeline: Created a Python automation script that programmatically builds the entire relational structure, ensuring consistent deployment across environments.
* Data Integrity Validation: Developed server-side logic to ensure grade distributions (A, B, C, F) precisely match official enrollment figures.

## 📊 Database Schema
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

##  User Manual (How to Use) 
   (This section explains the workflow for the user once the app is running). 
   1. Data Entry (Setup Phase) 
      • Navigate to the Data Entry menu. 
      • Order of Operations: You must create "Parent" records before "Child" records. 
         1. Add Degree: Define the program (e.g., "Computer Science - MS"). 
         2. Add Instructor: Enter faculty details. 
         3. Add Course: Define courses and link them to a Degree (mark them as Core or Elective). 
         4. Add Section: Schedule a course for a specific semester. Note: Enrollment must be > 0 and no negative numbers. 
   
   2. Objectives & Mapping 
      • Go to Objectives & Mapping. 
      • First, create Learning Objectives (e.g., "SQL Mastery"). 
      • Then, use Map Course Objective to link a specific Course to an Objective for a specific Degree. This step is required before evaluations can be entered. 
  
   3. Entering Evaluations 
      • Go to Enter Evaluation. 
      • Select the context: Degree Semester Instructor. 
      • Click the section you wish to grade. 
      • Input Data: 
         o Select evaluation methods (e.g., "Quiz", "Lab Demo"). 
         o Enter the count of students who received A, B, C, or F. 
         o Validation Rule: The total count of grades must match the official Enrolment number exactly (or be 0 if saving partial progress). 
   
   4. Running Reports 
      • Report 2 (Passing Rates): Select a semester and a target percentage (e.g., 80%). The system will show all courses where the passing rate (A+B+C) meets that threshold. 
      • Report 5 (Status): Use this to audit which professors have completed their data entry. Look for the Green "Entered" badge vs. the Yellow "Partially Entered" badge.
   

