# Program Evaluation Database System

## 🚀 Overview
This project is a comprehensive database solution designed to manage and evaluate academic degree programs. It enables university departments to track learning objectives, course sections, and instructor evaluations through a structured relational backend.

[cite_start]**Key Technical Highlight:** Implemented a **Soft Delete** strategy to preserve historical academic data integrity even when courses or instructors are discontinued. [cite: 92, 247]

## 🛠️ Tech Stack
* [cite_start]**Language:** Python 3.x [cite: 259]
* [cite_start]**Framework:** Flask (Web GUI) [cite: 283, 292]
* [cite_start]**Database:** MySQL / MariaDB [cite: 258]
* [cite_start]**Connector:** mysql-connector-python 

## 📊 Database Architecture
[cite_start]The system utilizes a complex relational schema consisting of **11 tables** designed to handle many-to-many relationships, such as courses satisfying different objectives across multiple degrees. [cite: 92, 189, 289]

### Core Schema Components:
* [cite_start]**Degree & Course Management:** Uniquely identifies programs by name and level (BS, MS, etc.). [cite: 96, 104]
* [cite_start]**Learning Objectives:** Maps specific goals to courses and degrees via "diamond" relationships. [cite: 184, 189]
* [cite_start]**Evaluation Engine:** Tracks aggregated student performance (Grades A-F) and correlates them to specific assessment methods like "Quizzes" or "Final Exams." [cite: 207, 229]
* [cite_start]**Data Integrity:** Employs `ON DELETE CASCADE` and status-based "Soft Deletes" to maintain historical report accuracy. [cite: 152, 247, 252]


## ⚙️ Installation & Setup
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