from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import errorcode
import configparser
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Load Configuration
config = configparser.ConfigParser()
config.read('config.ini')


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=config['mysql']['host'],
            user=config['mysql']['user'],
            password=config['mysql']['password'],
            database=config['mysql']['database']
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to DB: {err}")
        return None


def safe_int(value, default):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')


# --- MANAGE DATA ---
@app.route('/manage_data')
def manage_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Degree")
    degrees = cursor.fetchall()
    cursor.execute("SELECT * FROM Course")
    courses = cursor.fetchall()
    cursor.execute("SELECT * FROM Instructor")
    instructors = cursor.fetchall()
    cursor.execute("SELECT * FROM Section ORDER BY year_offered DESC, semester")
    sections = cursor.fetchall()
    conn.close()
    return render_template('manage_data.html', degrees=degrees, courses=courses, instructors=instructors,
                           sections=sections)


@app.route('/delete_item/<item_type>/<id>')
def delete_item(item_type, id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if item_type == 'instructor':
            cursor.execute("SELECT COUNT(*) FROM Teaches WHERE instructor_id = %s", (id,))
            if cursor.fetchone()[0] > 0:
                cursor.execute("UPDATE Instructor SET status = 'Inactive' WHERE instructor_id = %s", (id,))
                flash(f'Instructor {id} archived (History preserved).', 'info')
            else:
                cursor.execute("DELETE FROM Instructor WHERE instructor_id = %s", (id,))
                flash(f'Instructor {id} permanently deleted.', 'warning')

        elif item_type == 'degree':
            name, level = id.split('|')
            cursor.execute("""SELECT (SELECT COUNT(*) FROM Degree_Course WHERE degree_name=%s AND degree_level=%s) + 
                                     (SELECT COUNT(*) FROM Degree_Objective WHERE degree_name=%s AND degree_level=%s)""",
                           (name, level, name, level))
            if cursor.fetchone()[0] > 0:
                cursor.execute("UPDATE Degree SET status = 'Inactive' WHERE degree_name=%s AND degree_level=%s",
                               (name, level))
                flash(f'Degree {name} archived.', 'info')
            else:
                cursor.execute("DELETE FROM Degree WHERE degree_name=%s AND degree_level=%s", (name, level))
                flash(f'Degree {name} permanently deleted.', 'warning')

        elif item_type == 'course':
            cursor.execute("""SELECT (SELECT COUNT(*) FROM Section WHERE course_code=%s) + 
                                     (SELECT COUNT(*) FROM Degree_Course WHERE course_code=%s)""", (id, id))
            if cursor.fetchone()[0] > 0:
                cursor.execute("UPDATE Course SET status = 'Inactive' WHERE course_code=%s", (id,))
                flash(f'Course {id} archived.', 'info')
            else:
                cursor.execute("DELETE FROM Course WHERE course_code=%s", (id,))
                flash(f'Course {id} permanently deleted.', 'warning')
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f'Database Error: {err.msg}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('manage_data'))


@app.route('/reactivate_item/<item_type>/<id>')
def reactivate_item(item_type, id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        if item_type == 'instructor':
            cursor.execute("UPDATE Instructor SET status = 'Active' WHERE instructor_id = %s", (id,))
        elif item_type == 'degree':
            name, level = id.split('|')
            cursor.execute("UPDATE Degree SET status = 'Active' WHERE degree_name=%s AND degree_level=%s",
                           (name, level))
        elif item_type == 'course':
            cursor.execute("UPDATE Course SET status = 'Active' WHERE course_code=%s", (id,))
        conn.commit()
        flash(f'{item_type.capitalize()} restored to Active status.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err.msg}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('manage_data'))


@app.route('/delete_section/<c_code>/<sec_num>/<sem>/<year>')
def delete_section(c_code, sec_num, sem, year):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM Evaluation WHERE course_code=%s AND section_num=%s AND semester=%s AND year_offered=%s",
            (c_code, sec_num, sem, year))
        cursor.execute(
            "DELETE FROM Evaluation_Method WHERE course_code=%s AND section_num=%s AND semester=%s AND year_offered=%s",
            (c_code, sec_num, sem, year))
        cursor.execute(
            "DELETE FROM Teaches WHERE course_code=%s AND section_num=%s AND semester=%s AND year_offered=%s",
            (c_code, sec_num, sem, year))
        cursor.execute(
            "DELETE FROM Section WHERE course_code=%s AND section_num=%s AND semester=%s AND year_offered=%s",
            (c_code, sec_num, sem, year))
        conn.commit()
        flash('Section deleted.', 'warning')
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f'Error: {err.msg}', 'danger')
    finally:
        conn.close()
    return redirect(url_for('manage_data'))


@app.route('/edit_instructor/<id>', methods=['GET', 'POST'])
def edit_instructor(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute(
                "UPDATE Instructor SET first_name=%s, last_name=%s, email_id=%s, phone_number=%s WHERE instructor_id=%s",
                (request.form['first_name'], request.form['last_name'], request.form['email'], request.form['phone'],
                 id))
            conn.commit()
            flash('Instructor updated!', 'success')
            return redirect(url_for('manage_data'))
        except mysql.connector.Error as err:
            flash(f'Error: {err.msg}', 'danger')
    cursor.execute("SELECT * FROM Instructor WHERE instructor_id=%s", (id,))
    instructor = cursor.fetchone()
    conn.close()
    return render_template('edit_instructor.html', i=instructor)


@app.route('/edit_section/<c_code>/<sec_num>/<sem>/<year>', methods=['GET', 'POST'])
def edit_section(c_code, sec_num, sem, year):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute(
                "UPDATE Section SET num_enrollments=%s WHERE course_code=%s AND section_num=%s AND semester=%s AND year_offered=%s",
                (request.form['enrollments'], c_code, sec_num, sem, year))
            conn.commit()
            flash('Section updated!', 'success')
            return redirect(url_for('manage_data'))
        except mysql.connector.Error as err:
            flash(f'Error: {err.msg}', 'danger')
    cursor.execute("SELECT * FROM Section WHERE course_code=%s AND section_num=%s AND semester=%s AND year_offered=%s",
                   (c_code, sec_num, sem, year))
    section = cursor.fetchone()
    conn.close()
    return render_template('edit_section.html', s=section)


# --- DATA ENTRY ---

@app.route('/add_degree', methods=['GET', 'POST'])
def add_degree():
    if request.method == 'POST':
        name = request.form['degree_name']
        level = request.form['degree_level']
        desc = request.form['description']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT * FROM Degree WHERE degree_name = %s AND degree_level = %s", (name, level))
                if cursor.fetchone():
                    flash(f'Error: Degree "{name} ({level})" already exists!', 'danger')
                else:
                    cursor.execute(
                        "INSERT INTO Degree (degree_name, degree_level, description, status) VALUES (%s, %s, %s, 'Active')",
                        (name, level, desc))
                    conn.commit()
                    flash('Degree added!', 'success')
                    return redirect(url_for('index'))
            except mysql.connector.Error as err:
                flash(f'Database Error: {err.msg}', 'danger')
            finally:
                conn.close()
    return render_template('add_degree.html')


@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        c_code, c_name = request.form['course_code'], request.form['course_name']
        d_str = request.form['degree_selection']
        deg_name, deg_level = d_str.split('|')
        is_core = 1 if request.form.get('is_core') else 0
        try:
            try:
                cursor.execute("INSERT INTO Course (course_code, course_name, status) VALUES (%s, %s, 'Active')",
                               (c_code, c_name))
            except mysql.connector.Error as err:
                if err.errno != errorcode.ER_DUP_ENTRY: raise err

            cursor.execute(
                "INSERT INTO Degree_Course (degree_name, degree_level, course_code, is_core) VALUES (%s, %s, %s, %s)",
                (deg_name, deg_level, c_code, is_core))
            conn.commit()
            flash(f'Course {c_code} linked to {deg_name}!', 'success')
            return redirect(url_for('index'))
        except mysql.connector.Error as err:
            conn.rollback()
            if err.errno == errorcode.ER_DUP_ENTRY:
                flash(f'Error: Course {c_code} is ALREADY linked to {deg_name}.', 'danger')
            else:
                flash(f'Error: {err.msg}', 'danger')

    cursor.execute("SELECT degree_name, degree_level FROM Degree WHERE status = 'Active'")
    degrees = cursor.fetchall()
    conn.close()
    return render_template('add_course.html', degrees=degrees)


@app.route('/add_instructor', methods=['GET', 'POST'])
def add_instructor():
    if request.method == 'POST':
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO Instructor (instructor_id, first_name, middle_name, last_name, email_id, phone_number, status) VALUES (%s, %s, %s, %s, %s, %s, 'Active')",
                    (request.form['instructor_id'], request.form['first_name'], request.form['middle_name'],
                     request.form['last_name'], request.form['email'], request.form['phone']))
                conn.commit()
                flash(f'Instructor added!', 'success')
                return redirect(url_for('index'))
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_DUP_ENTRY:
                    flash(f'Error: Instructor ID "{request.form["instructor_id"]}" is already assigned.', 'danger')
                else:
                    flash(f'Error: {err.msg}', 'danger')
            finally:
                conn.close()
    return render_template('add_instructor.html')


@app.route('/add_section', methods=['GET', 'POST'])
def add_section():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        c_code = request.form['course_code']
        raw_sec_num = request.form['section_num']
        sem = request.form['semester']
        year_str = request.form['year']
        inst_id = request.form['instructor_id']

        try:
            enroll = int(request.form['enrollments'])
            sec_int = int(raw_sec_num)
            year = int(year_str)

            if enroll <= 0:
                flash('Error: Enrollment must be greater than 0.', 'danger')
                return redirect(url_for('add_section'))
            if sec_int == 0:
                flash('Error: Section number cannot be 000.', 'danger')
                return redirect(url_for('add_section'))

            sec_num = f"{sec_int:03d}"

        except ValueError:
            flash('Error: Numeric fields must be valid.', 'danger')
            return redirect(url_for('add_section'))

        cursor.execute("SELECT status, last_name FROM Instructor WHERE instructor_id = %s", (inst_id,))
        instructor_data = cursor.fetchone()

        current_year = datetime.now().year

        if instructor_data and instructor_data['status'] == 'Inactive':
            if year >= current_year:
                flash(
                    f"Error: {instructor_data['last_name']} is Archived and cannot teach future classes ({year}). Only historical data allowed.",
                    'danger')
                conn.close()
                return redirect(url_for('add_section'))

        try:
            cursor.execute(
                "INSERT INTO Section (course_code, section_num, semester, year_offered, num_enrollments) VALUES (%s, %s, %s, %s, %s)",
                (c_code, sec_num, sem, year, enroll))
            cursor.execute(
                "INSERT INTO Teaches (course_code, section_num, semester, year_offered, instructor_id) VALUES (%s, %s, %s, %s, %s)",
                (c_code, sec_num, sem, year, inst_id))
            conn.commit()
            flash(f'Section {sec_num} added successfully!', 'success')
            return redirect(url_for('index'))
        except mysql.connector.Error as err:
            conn.rollback()
            if err.errno == errorcode.ER_DUP_ENTRY:
                flash(f'Error: Section {sec_num} for {c_code} in {sem} {year} already exists!', 'danger')
            else:
                flash(f'Error: {err.msg}', 'danger')

    cursor.execute("SELECT course_code, course_name, status FROM Course ORDER BY course_code")
    courses = cursor.fetchall()
    cursor.execute("SELECT instructor_id, first_name, last_name, status FROM Instructor ORDER BY last_name")
    instructors = cursor.fetchall()
    conn.close()
    return render_template('add_section.html', courses=courses, instructors=instructors)


# --- MAPPING & EVALUATION ---
@app.route('/manage_objectives', methods=['GET', 'POST'])
def manage_objectives():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create_obj':
            try:
                cursor.execute("INSERT INTO Objective (obj_code, title, description) VALUES (%s, %s, %s)",
                               (request.form['obj_code'], request.form['title'], request.form['description']))
                conn.commit()
                flash('Objective created!', 'success')
            except mysql.connector.Error as err:
                flash(f'Error: {err.msg}', 'danger')
        elif action == 'link_obj_degree':
            d_data = request.form['degree_selection'].split('|')
            try:
                cursor.execute("INSERT INTO Degree_Objective (degree_name, degree_level, obj_code) VALUES (%s, %s, %s)",
                               (d_data[0], d_data[1], request.form['obj_code_selection']))
                conn.commit()
                flash('Linked Objective!', 'success')
            except mysql.connector.Error as err:
                flash(f'Error: {err.msg}', 'danger')
    cursor.execute("SELECT * FROM Degree WHERE status='Active'")
    degrees = cursor.fetchall()
    cursor.execute("SELECT * FROM Objective")
    objectives = cursor.fetchall()
    conn.close()
    return render_template('manage_objectives.html', degrees=degrees, objectives=objectives)


@app.route('/map_course_objective', methods=['GET', 'POST'])
def map_course_objective():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        d_str = request.form['degree_str']
        d_name, d_level = d_str.split('|')
        try:
            cursor.execute(
                "INSERT INTO Course_Objective (degree_name, degree_level, course_code, obj_code) VALUES (%s, %s, %s, %s)",
                (d_name, d_level, request.form['course_code'], request.form['obj_code']))
            conn.commit()
            flash('Mapped successfully!', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err.msg}', 'danger')
        return redirect(url_for('map_course_objective', degree=d_str))
    selected_degree = request.args.get('degree')
    degree_courses, degree_objs = [], []
    if selected_degree:
        d_name, d_level = selected_degree.split('|')
        cursor.execute(
            "SELECT C.course_code, C.course_name FROM Degree_Course DC JOIN Course C ON DC.course_code=C.course_code WHERE DC.degree_name=%s AND DC.degree_level=%s ORDER BY C.course_code",
            (d_name, d_level))
        degree_courses = cursor.fetchall()
        cursor.execute(
            "SELECT O.obj_code, O.title FROM Degree_Objective DO JOIN Objective O ON DO.obj_code=O.obj_code WHERE DO.degree_name=%s AND DO.degree_level=%s",
            (d_name, d_level))
        degree_objs = cursor.fetchall()
    cursor.execute("SELECT degree_name, degree_level FROM Degree WHERE status='Active'")
    all_degrees = cursor.fetchall()
    conn.close()
    return render_template('map_course_objective.html', all_degrees=all_degrees, selected_degree=selected_degree,
                           courses=degree_courses, objectives=degree_objs)


@app.route('/evaluation_selection', methods=['GET', 'POST'])
def evaluation_selection():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    sections_found, context = [], {}
    if request.method == 'POST':
        d_str, sem, yr, inst_id = request.form['degree_selection'], request.form['semester'], request.form['year'], \
        request.form['instructor_id']
        d_name, d_level = d_str.split('|')
        context = {'degree_str': d_str, 'semester': sem, 'year': yr, 'instructor_id': inst_id}
        sql = """SELECT S.course_code, S.section_num, C.course_name, (SELECT COUNT(*) FROM Evaluation E WHERE E.course_code = S.course_code AND E.section_num = S.section_num AND E.semester = S.semester AND E.year_offered = S.year_offered AND E.degree_name = %s AND E.degree_level = %s) as eval_count FROM Teaches T JOIN Section S ON T.course_code=S.course_code AND T.section_num=S.section_num AND T.semester=S.semester AND T.year_offered=S.year_offered JOIN Course C ON S.course_code=C.course_code WHERE T.instructor_id=%s AND S.semester=%s AND S.year_offered=%s"""
        cursor.execute(sql, (d_name, d_level, inst_id, sem, yr))
        sections_found = cursor.fetchall()
    cursor.execute("SELECT * FROM Degree WHERE status='Active'")
    degrees = cursor.fetchall()
    cursor.execute("SELECT * FROM Instructor WHERE status='Active'")
    instructors = cursor.fetchall()
    conn.close()
    return render_template('evaluation_selection.html', degrees=degrees, instructors=instructors,
                           sections=sections_found, context=context)


@app.route('/enter_evaluation_form', methods=['GET', 'POST'])
def enter_evaluation_form():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    d_str = request.args.get('degree_str') or request.form.get('degree_str')
    c_code = request.args.get('course_code') or request.form.get('course_code')
    sec_num = request.args.get('section_num') or request.form.get('section_num')
    sem = request.args.get('semester') or request.form.get('semester')
    yr = request.args.get('year') or request.form.get('year')

    if d_str:
        d_name, d_level = d_str.split('|')
    else:
        return redirect(url_for('index'))

    if request.method == 'POST':
        duplicate = request.form.get('duplicate_to_others')
        try:
            cursor.execute(
                "SELECT num_enrollments FROM Section WHERE course_code=%s AND section_num=%s AND semester=%s AND year_offered=%s",
                (c_code, sec_num, sem, yr))
            section_data = cursor.fetchone()
            if not section_data:
                flash("Error: Section not found.", "danger")
                return redirect(url_for('index'))
            limit = section_data['num_enrollments']

            objectives_submitted = set(
                [key.replace('count_A_', '') for key in request.form if key.startswith('count_A_')])

            # --- MODIFIED ERROR MESSAGE HERE ---
            for obj_code in objectives_submitted:
                total = int(request.form.get(f'count_A_{obj_code}') or 0) + \
                        int(request.form.get(f'count_B_{obj_code}') or 0) + \
                        int(request.form.get(f'count_C_{obj_code}') or 0) + \
                        int(request.form.get(f'count_F_{obj_code}') or 0)

                # Logic: Allow 0 (partial) or match limit (complete). Block otherwise.
                if total != 0 and total != limit:
                    # Message Updated: Removed "OR empty (0)"
                    flash(f"Error for {obj_code}: Total ({total}) must be exactly {limit}.", "danger")
                    conn.close()
                    return redirect(
                        url_for('enter_evaluation_form', degree_str=d_str, course_code=c_code, section_num=sec_num,
                                semester=sem, year=yr))

            for obj_code in objectives_submitted:
                cA, cB, cC, cF = request.form[f'count_A_{obj_code}'], request.form[f'count_B_{obj_code}'], request.form[
                    f'count_C_{obj_code}'], request.form[f'count_F_{obj_code}']
                impr = request.form[f'improvement_{obj_code}']
                selected_methods = request.form.getlist(f'methods_{obj_code}')
                other_text = request.form.get(f'method_other_{obj_code}')
                if other_text: selected_methods.extend([m.strip() for m in other_text.split(',') if m.strip()])

                target_degrees = [(d_name, d_level)]
                if duplicate:
                    cursor.execute(
                        "SELECT degree_name, degree_level FROM Course_Objective WHERE course_code=%s AND obj_code=%s",
                        (c_code, obj_code))
                    for o in cursor.fetchall():
                        if (o['degree_name'], o['degree_level']) not in target_degrees: target_degrees.append(
                            (o['degree_name'], o['degree_level']))

                for (t_name, t_level) in target_degrees:
                    cursor.execute(
                        "REPLACE INTO Evaluation (course_code, section_num, semester, year_offered, degree_name, degree_level, obj_code, count_A, count_B, count_C, count_F, improvement) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (c_code, sec_num, sem, yr, t_name, t_level, obj_code, cA, cB, cC, cF, impr))
                    cursor.execute(
                        "DELETE FROM Evaluation_Method WHERE course_code=%s AND section_num=%s AND semester=%s AND year_offered=%s AND degree_name=%s AND degree_level=%s AND obj_code=%s",
                        (c_code, sec_num, sem, yr, t_name, t_level, obj_code))
                    for m in selected_methods:
                        cursor.execute("INSERT INTO Evaluation_Method VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                       (c_code, sec_num, sem, yr, t_name, t_level, obj_code, m))
            conn.commit()
            flash('Evaluation saved!', 'success')
            return redirect(url_for('index'))
        except mysql.connector.Error as err:
            flash(f'Database Error: {err.msg}', 'danger')
        except ValueError:
            flash('Error: Grades must be numbers.', 'danger')

    cursor.execute(
        "SELECT O.obj_code, O.title, O.description FROM Course_Objective CO JOIN Objective O ON CO.obj_code=O.obj_code WHERE CO.degree_name=%s AND CO.degree_level=%s AND CO.course_code=%s",
        (d_name, d_level, c_code))
    objectives = cursor.fetchall()
    cursor.execute(
        "SELECT * FROM Evaluation WHERE course_code=%s AND section_num=%s AND semester=%s AND year_offered=%s AND degree_name=%s AND degree_level=%s",
        (c_code, sec_num, sem, yr, d_name, d_level))
    data_map = {row['obj_code']: row for row in cursor.fetchall()}
    cursor.execute(
        "SELECT * FROM Evaluation_Method WHERE course_code=%s AND section_num=%s AND semester=%s AND year_offered=%s AND degree_name=%s AND degree_level=%s",
        (c_code, sec_num, sem, yr, d_name, d_level))
    method_map = {}
    for row in cursor.fetchall():
        if row['obj_code'] not in method_map: method_map[row['obj_code']] = []
        method_map[row['obj_code']].append(row['method_name'])
    conn.close()
    return render_template('enter_evaluation_form.html', objs=objectives, data_map=data_map, method_map=method_map,
                           info={'d_str': d_str, 'c_code': c_code, 'sec': sec_num, 'sem': sem, 'yr': yr})


# --- REPORTS ---
@app.route('/reports', methods=['GET', 'POST'])
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    results, report_type, search_term = [], None, ""

    if request.method == 'POST':
        report_type = request.form.get('report_type')

        if report_type == 'degree_details':
            d_name, d_level = request.form.get('degree_selection').split('|')
            start_year, end_year = safe_int(request.form.get('start_year'), 2020), safe_int(
                request.form.get('end_year'), 2030)
            search_term = f"{d_name} ({d_level})"
            cursor.execute(
                "SELECT C.course_code, C.course_name, DC.is_core FROM Degree_Course DC JOIN Course C ON DC.course_code=C.course_code WHERE DC.degree_name=%s AND DC.degree_level=%s ORDER BY DC.is_core DESC, C.course_code ASC",
                (d_name, d_level))
            courses = cursor.fetchall()
            cursor.execute(
                "SELECT DO.obj_code, O.title FROM Degree_Objective DO JOIN Objective O ON DO.obj_code=O.obj_code WHERE DO.degree_name=%s AND DO.degree_level=%s",
                (d_name, d_level))
            objs = cursor.fetchall()
            cursor.execute(
                "SELECT S.year_offered, S.semester, S.course_code, S.section_num, C.course_name FROM Degree_Course DC JOIN Section S ON DC.course_code=S.course_code JOIN Course C ON S.course_code=C.course_code WHERE DC.degree_name=%s AND DC.degree_level=%s AND S.year_offered BETWEEN %s AND %s ORDER BY S.year_offered DESC, CASE S.semester WHEN 'Fall' THEN 3 WHEN 'Summer' THEN 2 WHEN 'Spring' THEN 1 END DESC",
                (d_name, d_level, start_year, end_year))
            sections = cursor.fetchall()
            cursor.execute(
                "SELECT CO.obj_code, O.title, CO.course_code, C.course_name FROM Course_Objective CO JOIN Objective O ON CO.obj_code=O.obj_code JOIN Course C ON CO.course_code=C.course_code WHERE CO.degree_name=%s AND CO.degree_level=%s ORDER BY CO.obj_code",
                (d_name, d_level))
            results = {'courses': courses, 'objectives': objs, 'sections': sections, 'obj_map': cursor.fetchall()}

        elif report_type == 'passing_rate':
            semester, year, threshold = request.form.get('semester'), request.form.get('year'), float(
                request.form.get('percentage', 0))
            search_term = f"{semester} {year} (> {threshold}%)"
            sql_pass = """SELECT E.degree_name, E.degree_level, E.course_code, E.section_num, E.obj_code, 
                          (E.count_A+E.count_B+E.count_C) as passed, (E.count_A+E.count_B+E.count_C+E.count_F) as total, 
                          ((E.count_A+E.count_B+E.count_C)/NULLIF((E.count_A+E.count_B+E.count_C+E.count_F),0))*100 as pass_rate,
                          (SELECT GROUP_CONCAT(method_name SEPARATOR ', ') FROM Evaluation_Method EM WHERE EM.course_code=E.course_code AND EM.section_num=E.section_num AND EM.semester=E.semester AND EM.year_offered=E.year_offered AND EM.degree_name=E.degree_name AND EM.degree_level=E.degree_level AND EM.obj_code=E.obj_code) as methods
                          FROM Evaluation E WHERE E.semester=%s AND E.year_offered=%s HAVING pass_rate >= %s"""
            cursor.execute(sql_pass, (semester, year, threshold))
            results = cursor.fetchall()

        elif report_type == 'course_sections':
            c_code = request.form.get('course_code')
            start_sem, start_year = request.form.get('start_sem'), safe_int(request.form.get('start_year'), 2020)
            end_sem, end_year = request.form.get('end_sem'), safe_int(request.form.get('end_year'), 2030)
            term_map = {'Spring': 1, 'Summer': 2, 'Fall': 3}
            start_val, end_val = start_year * 10 + term_map.get(start_sem, 1), end_year * 10 + term_map.get(end_sem, 3)
            search_term = f"Course {c_code} ({start_sem} {start_year} - {end_sem} {end_year})"
            cursor.execute(
                "SELECT S.course_code, S.section_num, S.semester, S.year_offered, S.num_enrollments, I.last_name, I.first_name FROM Section S LEFT JOIN Teaches T ON S.course_code=T.course_code AND S.section_num=T.section_num AND S.semester=T.semester AND S.year_offered=T.year_offered LEFT JOIN Instructor I ON T.instructor_id=I.instructor_id WHERE S.course_code=%s AND (S.year_offered * 10 + CASE S.semester WHEN 'Spring' THEN 1 WHEN 'Summer' THEN 2 WHEN 'Fall' THEN 3 END) >= %s AND (S.year_offered * 10 + CASE S.semester WHEN 'Spring' THEN 1 WHEN 'Summer' THEN 2 WHEN 'Fall' THEN 3 END) <= %s ORDER BY S.year_offered DESC, CASE S.semester WHEN 'Fall' THEN 3 WHEN 'Summer' THEN 2 WHEN 'Spring' THEN 1 END DESC",
                (c_code, start_val, end_val))
            results = cursor.fetchall()

        elif report_type == 'instructor_sections':
            inst_id = request.form.get('instructor_id')
            start_sem, start_year = request.form.get('start_sem'), safe_int(request.form.get('start_year'), 2020)
            end_sem, end_year = request.form.get('end_sem'), safe_int(request.form.get('end_year'), 2030)
            term_map = {'Spring': 1, 'Summer': 2, 'Fall': 3}
            start_val, end_val = start_year * 10 + term_map.get(start_sem, 1), end_year * 10 + term_map.get(end_sem, 3)
            cursor.execute("SELECT first_name, last_name FROM Instructor WHERE instructor_id=%s", (inst_id,))
            inst_data = cursor.fetchone()
            search_term = f"Instructor {inst_data['first_name']} {inst_data['last_name']} ({start_sem} {start_year} - {end_sem} {end_year})" if inst_data else "History"
            cursor.execute(
                "SELECT S.year_offered, S.semester, S.course_code, S.section_num, S.num_enrollments, C.course_name FROM Teaches T JOIN Section S ON T.course_code=S.course_code AND T.section_num=S.section_num AND T.semester=S.semester AND T.year_offered=S.year_offered JOIN Course C ON S.course_code=C.course_code WHERE T.instructor_id=%s AND (S.year_offered * 10 + CASE S.semester WHEN 'Spring' THEN 1 WHEN 'Summer' THEN 2 WHEN 'Fall' THEN 3 END) >= %s AND (S.year_offered * 10 + CASE S.semester WHEN 'Spring' THEN 1 WHEN 'Summer' THEN 2 WHEN 'Fall' THEN 3 END) <= %s ORDER BY S.year_offered DESC, CASE S.semester WHEN 'Fall' THEN 3 WHEN 'Summer' THEN 2 WHEN 'Spring' THEN 1 END DESC",
                (inst_id, start_val, end_val))
            results = cursor.fetchall()

        elif report_type == 'eval_status':
            semester, year = request.form.get('semester'), request.form.get('year')
            search_term = f"Evaluation Status: {semester} {year}"
            cursor.execute("""SELECT S.course_code, S.section_num, C.course_name, 
                              (SELECT COUNT(*) FROM Evaluation E 
                               WHERE E.course_code = S.course_code 
                               AND E.section_num = S.section_num 
                               AND E.semester = S.semester 
                               AND E.year_offered = S.year_offered 
                               AND (E.count_A + E.count_B + E.count_C + E.count_F) > 0) as actual_evals, 
                              (SELECT COUNT(*) FROM Course_Objective CO 
                               WHERE CO.course_code = S.course_code) as expected_evals, 
                              (SELECT COUNT(*) FROM Evaluation E 
                               WHERE E.course_code = S.course_code 
                               AND E.section_num = S.section_num 
                               AND E.semester = S.semester 
                               AND E.year_offered = S.year_offered 
                               AND E.improvement IS NOT NULL AND E.improvement <> '') as impr_count 
                              FROM Section S JOIN Course C ON S.course_code = C.course_code 
                              WHERE S.semester = %s AND S.year_offered = %s 
                              ORDER BY S.course_code, S.section_num""", (semester, year))
            results = cursor.fetchall()

    cursor.execute("SELECT * FROM Degree WHERE status='Active'")
    degrees = cursor.fetchall()
    cursor.execute("SELECT course_code, course_name FROM Course ORDER BY course_code")
    all_courses = cursor.fetchall()
    cursor.execute("SELECT instructor_id, first_name, last_name FROM Instructor ORDER BY last_name")
    all_instructors = cursor.fetchall()
    conn.close()
    return render_template('reports.html', degrees=degrees, all_courses=all_courses, all_instructors=all_instructors,
                           results=results, report_type=report_type, search_term=search_term)


if __name__ == '__main__':
    app.run(debug=True)