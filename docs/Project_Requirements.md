🎓 University Program Evaluation Database System
📌 Project Overview
The goal of this project is to implement a robust database solution for university degree program reviews. This system facilitates the correction, storage, and analysis of data regarding faculty, courses, and student performance against specific learning objectives.

Backend: MySQL / MariaDB

🏗️ Data Models
1. Degrees, Faculty & Courses
Degrees: Defined by a Name and Level (BA, BS, MS, Ph.D., Cert). The combination of Name + Level is unique.

Courses: Each has a unique Course Number (e.g., CS-101) and a unique Name.

Core Courses: Every degree must have at least one designated core course.

Semesters: Tracking occurs across three terms: Spring, Summer, and Fall.

Sections: Courses are offered in sections (3-digit codes). We track student enrollment counts per section.

Instructors: Each section is taught by an instructor with a unique ID and Name.

2. Learning Objectives & Evaluation
Objectives: Identified by a unique code, a title (max 120 chars), and an arbitrary-length description.

Mapping: * Each core course must map to at least one objective.

Each objective must map to at least one core course.

Evaluations: At the end of each semester, instructors enter data for each objective:

Method: (e.g., Homework, Project, Quiz, Exam, etc.).

Performance: Count of students achieving grades A, B, C, or F.

Feedback: An optional paragraph for suggested improvements.

Note: Evaluations for the same section/objective can vary across different degrees.

💻 Application Requirements
📥 Data Entry Module
The application must support the creation and management of:

Core entities: Degrees, Courses, Instructors, Sections, and Objectives.

Associations: Mapping courses to specific learning objectives.

Scheduling: Assigning courses and sections to specific semesters.

📊 Evaluation Entry Interface
A specialized workflow for instructors:

Search by Degree, Semester, and Instructor.

Display taught sections and their current data entry status (Complete/Incomplete).

Provide options to Enter, Edit, or Duplicate evaluation data across multiple degrees.

🔍 Querying Capabilities
The system must answer the following:

Degree-Based Queries
List all associated courses (identifying core vs. elective).

List all sections offered within a user-defined chronological range.

List all learning objectives and their associated courses.

Course & Instructor Queries
Course: List all sections within a specific semester range.

Instructor: List all sections taught within a specific semester range.

Evaluation Analysis
Status Report: For a given semester, list sections and whether evaluation data (and the optional improvement paragraph) is fully, partially, or not yet entered.

Performance Thresholds: Find sections where the percentage of students passing (non-'F' grades) meets a user-provided threshold.