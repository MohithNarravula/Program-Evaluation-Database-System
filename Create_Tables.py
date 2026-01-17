import configparser
import mysql.connector
import csv
import os
from datetime import datetime, timedelta

config = configparser.ConfigParser()
config.read('config.ini')

db = mysql.connector.connect(
    host=config['mysql']['host'],
    user=config['mysql']['user'],
    password=config['mysql']['password'],
    database=config['mysql']['database']
)

cursor = db.cursor()

# -------------------------
# Data Definition Commands
# --------------------------

# --- Create tables if they do not exist in the database
def Create_tables(cursor):
        """
            Checks if tables exist and creates them if they don't,
            including all constraints.
        """

        # 1. Create  Degree Table
        create_degree_sql = """
            CREATE TABLE IF NOT EXISTS Degree (
                  degree_name  VARCHAR(100) NOT NULL,
                  degree_level ENUM('BA','BS','MS','PhD','Cert') NOT NULL,
                  description  TEXT,
              PRIMARY KEY (degree_name, degree_level)
            )
            """

        # 2. Create Course Table
        create_course_sql = """
                      CREATE TABLE IF NOT EXISTS Course (
                      course_code  VARCHAR(10) NOT NULL,
                      course_name  VARCHAR(200) NOT NULL,
                  PRIMARY KEY (course_code),
                  UNIQUE KEY uk_course_name (course_name)
                  )
                """

        # 3. Create  Degree_Course Table(degree ↔ course, with core flag)
        create_degree_course_sql = """
                    CREATE TABLE IF NOT EXISTS Degree_Course (
                          degree_name  VARCHAR(100) NOT NULL,
                          degree_level ENUM('BA','BS','MS','PhD','Cert') NOT NULL,
                          course_code  VARCHAR(10) NOT NULL,
                          is_core      BOOLEAN NOT NULL DEFAULT 0,
                      PRIMARY KEY (degree_name, degree_level, course_code),
                      CONSTRAINT fk_dc_degree FOREIGN KEY (degree_name, degree_level)
                        REFERENCES Degree(degree_name, degree_level)
                        ON DELETE CASCADE ON UPDATE CASCADE,
                      CONSTRAINT fk_dc_course FOREIGN KEY (course_code)
                        REFERENCES Course(course_code)
                        ON DELETE CASCADE ON UPDATE CASCADE
                    )
                    """

        # 4. Create Instructor Table
        create_instructor_sql = """
                    CREATE TABLE IF NOT EXISTS Instructor (
                      instructor_id VARCHAR(10) NOT NULL,
                      first_name    VARCHAR(50) NOT NULL,
                      middle_name   VARCHAR(50),
                      last_name     VARCHAR(50) NOT NULL,
                      email_id      VARCHAR(150) NOT NULL,
                      phone_number  VARCHAR(30),
                      PRIMARY KEY (instructor_id),
                      UNIQUE KEY uk_instructor_email (email_id)
                    ) 
                    """

        # 5. Create Section Table
        create_section_sql = """
                    CREATE TABLE IF NOT EXISTS Section (
                      course_code     VARCHAR(10) NOT NULL,
                      section_num     SMALLINT NOT NULL, -- 3-digit number like 1, 2, ...
                      semester        ENUM('Spring','Summer','Fall') NOT NULL,
                      year_offered    SMALLINT NOT NULL,
                      num_enrollments INT NOT NULL DEFAULT 0,
                      PRIMARY KEY (course_code, section_num, semester, year_offered),
                      CONSTRAINT fk_section_course FOREIGN KEY (course_code)
                        REFERENCES Course(course_code)
                        ON DELETE CASCADE ON UPDATE CASCADE
                    )
                    """

        # 6. Create Teaches Table
        create_teaches_sql = """
                            CREATE TABLE IF NOT EXISTS Teaches (
                              course_code     VARCHAR(10) NOT NULL,
                              section_num     SMALLINT NOT NULL,
                              semester        ENUM('Spring','Summer','Fall') NOT NULL,
                              year_offered    SMALLINT NOT NULL,
                              instructor_id   VARCHAR(10) NOT NULL,
                              PRIMARY KEY (course_code, section_num, semester, year_offered),
                              CONSTRAINT fk_teaches_section FOREIGN KEY (course_code, section_num, semester, year_offered)
                                REFERENCES Section(course_code, section_num, semester, year_offered)
                                ON DELETE CASCADE ON UPDATE CASCADE,
                              CONSTRAINT fk_teaches_instructor FOREIGN KEY (instructor_id)
                                REFERENCES Instructor(instructor_id)
                                ON DELETE CASCADE ON UPDATE CASCADE
                            ) 
                            """

        # 7. Create Objective Table(global catalog)
        create_objective_sql = """
                            CREATE TABLE IF NOT EXISTS Objective (
                              obj_code    VARCHAR(20) NOT NULL,
                              title       VARCHAR(120) NOT NULL,
                              description TEXT NOT NULL,
                              PRIMARY KEY (obj_code),
                              UNIQUE KEY uk_obj_title (title)
                            )
                            """

        # 8. Create  Degree_Objective Table (objectives per degree)
        create_degree_objective_sql = """
                            CREATE TABLE IF NOT EXISTS Degree_Objective (
                              degree_name  VARCHAR(100) NOT NULL,
                              degree_level ENUM('BA','BS','MS','PhD','Cert') NOT NULL,
                              obj_code     VARCHAR(20) NOT NULL,
                              PRIMARY KEY (degree_name, degree_level, obj_code),
                              CONSTRAINT fk_do_degree FOREIGN KEY (degree_name, degree_level)
                                REFERENCES Degree(degree_name, degree_level)
                                ON DELETE CASCADE ON UPDATE CASCADE,
                              CONSTRAINT fk_do_obj FOREIGN KEY (obj_code)
                                REFERENCES Objective(obj_code)
                                ON DELETE CASCADE ON UPDATE CASCADE
                            )
                            """

        # 9. Create  Course_Objective Table (degree-specific mapping: degree + course + objective)
        create_course_objective_sql = """
                            CREATE TABLE IF NOT EXISTS Course_Objective (
                              degree_name  VARCHAR(100) NOT NULL,
                              degree_level ENUM('BA','BS','MS','PhD','Cert') NOT NULL,
                              course_code  VARCHAR(10) NOT NULL,
                              obj_code     VARCHAR(20) NOT NULL,
                              PRIMARY KEY (degree_name, degree_level, course_code, obj_code),
                              CONSTRAINT fk_co_degree_course FOREIGN KEY (degree_name, degree_level, course_code)
                                REFERENCES Degree_Course(degree_name, degree_level, course_code)
                                ON DELETE CASCADE ON UPDATE CASCADE,
                              CONSTRAINT fk_co_degree_obj FOREIGN KEY (degree_name, degree_level, obj_code)
                                REFERENCES Degree_Objective(degree_name, degree_level, obj_code)
                                ON DELETE CASCADE ON UPDATE CASCADE
                            )
                            """

        # 10. Create  Evaluation Table(per section + degree + course + objective)
        create_evaluation_sql = """
                           CREATE TABLE IF NOT EXISTS Evaluation (
                              course_code    VARCHAR(10) NOT NULL,
                              section_num    SMALLINT NOT NULL,
                              semester       ENUM('Spring','Summer','Fall') NOT NULL,
                              year_offered   SMALLINT NOT NULL,
                            
                              degree_name    VARCHAR(100) NOT NULL,
                              degree_level   ENUM('BA','BS','MS','PhD','Cert') NOT NULL,
                              obj_code       VARCHAR(20) NOT NULL,
                            
                              count_A        INT NOT NULL DEFAULT 0,
                              count_B        INT NOT NULL DEFAULT 0,
                              count_C        INT NOT NULL DEFAULT 0,
                              count_F        INT NOT NULL DEFAULT 0,
                              improvement    TEXT,
                            
                              PRIMARY KEY (
                                course_code, section_num, semester, year_offered,
                                degree_name, degree_level, obj_code
                              ),
                            
                              -- Tie to Section (which implies the specific offering)
                              CONSTRAINT fk_eval_section FOREIGN KEY (course_code, section_num, semester, year_offered)
                                REFERENCES Section(course_code, section_num, semester, year_offered)
                                ON DELETE CASCADE ON UPDATE CASCADE,
                            
                              -- Enforce that (degree, course, obj) is valid per Course_Objective
                              CONSTRAINT fk_eval_co FOREIGN KEY (degree_name, degree_level, course_code, obj_code)
                                REFERENCES Course_Objective(degree_name, degree_level, course_code, obj_code)
                                ON DELETE CASCADE ON UPDATE CASCADE
                            )
                           """

        # 11. Create Evaluation_Method Table (multiple methods per evaluation, free-text)
        create_evaluation_method_sql = """
                            CREATE TABLE IF NOT EXISTS Evaluation_Method (
                                  course_code    VARCHAR(10) NOT NULL,
                                  section_num    SMALLINT NOT NULL,
                                  semester       ENUM('Spring','Summer','Fall') NOT NULL,
                                  year_offered   SMALLINT NOT NULL,
                                
                                  degree_name    VARCHAR(100) NOT NULL,
                                  degree_level   ENUM('BA','BS','MS','PhD','Cert') NOT NULL,
                                  obj_code       VARCHAR(20) NOT NULL,
                                
                                  method_name    VARCHAR(150) NOT NULL,
                                
                                  PRIMARY KEY (
                                    course_code, section_num, semester, year_offered,
                                    degree_name, degree_level, obj_code, method_name
                                  ),
                                
                                  CONSTRAINT fk_em_eval FOREIGN KEY (
                                    course_code, section_num, semester, year_offered,
                                    degree_name, degree_level, obj_code
                                  )
                                    REFERENCES Evaluation(
                                      course_code, section_num, semester, year_offered,
                                      degree_name, degree_level, obj_code
                                    )
                                    ON DELETE CASCADE ON UPDATE CASCADE
                                ) 
                            """

        try:
            cursor.execute(create_degree_sql)
            cursor.execute(create_course_sql)
            cursor.execute(create_degree_course_sql)
            cursor.execute(create_instructor_sql)
            cursor.execute(create_section_sql)
            cursor.execute(create_teaches_sql)
            cursor.execute(create_objective_sql)
            cursor.execute(create_degree_objective_sql)
            cursor.execute(create_course_objective_sql)
            cursor.execute(create_evaluation_sql)
            cursor.execute(create_evaluation_method_sql)
            print("Tables checked/created.")
        except mysql.connector.Error as err:
            print(f"Error creating tables: {err}")

Create_tables(cursor)
cursor.close()
db.close()