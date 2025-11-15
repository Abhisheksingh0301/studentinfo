from flask import Blueprint, render_template, Flask, request, send_file
from io import BytesIO
from db import get_db
import pandas as pd
import pyodbc

main = Blueprint('main', __name__)

def rows_to_dict_list(cursor):
    """Convert pyodbc cursor results to list of dicts."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

@main.route('/', methods=['GET', 'POST'])
def index():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT DISTINCT SESS FROM STUDENT_MASTER ORDER BY SESS DESC")
    Sessn = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT DEPARTMENT FROM STUDENT_MASTER ORDER BY DEPARTMENT")
    Dept = [row[0] for row in cursor.fetchall()]

    # Initialize variables so they're always defined
    records = []
    name = []
    regdno = []
    yr = []
    full_mks=[]
    per_mks=[]
    Pass_count=[]
    Arr_count=[]
    Total_records=[]
    Total_mks=[]
    selected_sessn = None
    selected_dept = None
    selected_roll = None

    # Handle POST (form submission)
    if request.method == 'POST':
        selected_sessn = request.form.get('sessn')
        selected_dept = request.form.get('dept')
        selected_roll = request.form.get('roll')

        if selected_sessn and selected_dept and selected_roll:
            # Fetch Name, Year, RegNo
            cursor.execute('''
                SELECT DISTINCT NAME FROM STUDENT_MASTER 
                WHERE DEPARTMENT=? AND SESS=? AND ROLL=?
            ''', (selected_dept, selected_sessn, selected_roll))
            #name = [row[0] for row in cursor.fetchall()]  #name = [row[0] for row in cursor.fetchall()]
            row = cursor.fetchone()
            name = row[0] if row else ""



            cursor.execute('''
                SELECT DISTINCT REGISTRATIONNO FROM STUDENT_MASTER 
                WHERE DEPARTMENT=? AND SESS=? AND ROLL=?
            ''', (selected_dept, selected_sessn, selected_roll))
            row = cursor.fetchone()
            regdno = row[0] if row else ""


            cursor.execute('''
                SELECT DISTINCT Current_Year FROM STUDENT_MASTER 
                WHERE DEPARTMENT=? AND SESS=? AND ROLL=?
            ''', (selected_dept, selected_sessn, selected_roll))
            row = cursor.fetchone()
            yr = row[0] if row else ""

           
            cursor.execute('''
                SELECT  COUNT(*)
                FROM  EXAM_MARKS_ACTUAL INNER JOIN
                STUDENT_MASTER ON EXAM_MARKS_ACTUAL.Student_id = STUDENT_MASTER.Student_id AND EXAM_MARKS_ACTUAL.RegNo = STUDENT_MASTER.RegistrationNo 
                AND EXAM_MARKS_ACTUAL.Current_Year = STUDENT_MASTER.Current_Year AND EXAM_MARKS_ACTUAL.Department = STUDENT_MASTER.Department 
                AND EXAM_MARKS_ACTUAL.Roll = STUDENT_MASTER.Roll WHERE        (STUDENT_MASTER.Sess = ?) AND 
                (STUDENT_MASTER.Department = ?) AND (STUDENT_MASTER.Roll =? AND PASS='ARREAR') 
            ''', (selected_sessn, selected_dept, selected_roll))
            row = cursor.fetchone()
            Arr_count = row[0] if row else 0

            cursor.execute('''
                SELECT  COUNT(*)
                FROM  EXAM_MARKS_ACTUAL INNER JOIN
                STUDENT_MASTER ON EXAM_MARKS_ACTUAL.Student_id = STUDENT_MASTER.Student_id AND EXAM_MARKS_ACTUAL.RegNo = STUDENT_MASTER.RegistrationNo 
                AND EXAM_MARKS_ACTUAL.Current_Year = STUDENT_MASTER.Current_Year AND EXAM_MARKS_ACTUAL.Department = STUDENT_MASTER.Department 
                AND EXAM_MARKS_ACTUAL.Roll = STUDENT_MASTER.Roll WHERE        (STUDENT_MASTER.Sess = ?) AND 
                (STUDENT_MASTER.Department = ?) AND (STUDENT_MASTER.Roll =? AND PASS='PASS') 
            ''', (selected_sessn, selected_dept, selected_roll))
            row = cursor.fetchone()
            Pass_count = row[0] if row else 0
            
            cursor.execute('''
                SELECT  SUM(TOTAL)
                FROM  EXAM_MARKS_ACTUAL INNER JOIN
                STUDENT_MASTER ON EXAM_MARKS_ACTUAL.Student_id = STUDENT_MASTER.Student_id AND EXAM_MARKS_ACTUAL.RegNo = STUDENT_MASTER.RegistrationNo 
                AND EXAM_MARKS_ACTUAL.Current_Year = STUDENT_MASTER.Current_Year AND EXAM_MARKS_ACTUAL.Department = STUDENT_MASTER.Department 
                AND EXAM_MARKS_ACTUAL.Roll = STUDENT_MASTER.Roll WHERE        (STUDENT_MASTER.Sess = ?) AND 
                (STUDENT_MASTER.Department = ?) AND (STUDENT_MASTER.Roll =?) 
            ''', (selected_sessn, selected_dept, selected_roll))
            row = cursor.fetchone()
            Total_mks = row[0] if row else 0

            cursor.execute('''
                SELECT   sum(TOTAL)*100/SUM(FULLMARKS)
                FROM  EXAM_MARKS_ACTUAL INNER JOIN
                STUDENT_MASTER ON EXAM_MARKS_ACTUAL.Student_id = STUDENT_MASTER.Student_id AND EXAM_MARKS_ACTUAL.RegNo = STUDENT_MASTER.RegistrationNo 
                AND EXAM_MARKS_ACTUAL.Current_Year = STUDENT_MASTER.Current_Year AND EXAM_MARKS_ACTUAL.Department = STUDENT_MASTER.Department
                AND EXAM_MARKS_ACTUAL.Roll = STUDENT_MASTER.Roll INNER JOIN
                        MARKS_SETUP ON STUDENT_MASTER.Sess = MARKS_SETUP.Sess AND STUDENT_MASTER.Current_Year = MARKS_SETUP.Current_Year 
                        AND EXAM_MARKS_ACTUAL.Sess = MARKS_SETUP.Sess AND 
                        EXAM_MARKS_ACTUAL.Current_Year = MARKS_SETUP.Current_Year AND EXAM_MARKS_ACTUAL.Department = MARKS_SETUP.Department 
                        AND STUDENT_MASTER.Department = MARKS_SETUP.Department AND EXAM_MARKS_ACTUAL.Subject = MARKS_SETUP.Subject_Code
                        WHERE (STUDENT_MASTER.Sess = ?) AND (STUDENT_MASTER.Department = ?) AND (STUDENT_MASTER.Roll =?) 
            ''', (selected_sessn, selected_dept, selected_roll))
            row = cursor.fetchone()
            per_mks = round(row[0], 2) if row and row[0] is not None else 0

            cursor.execute('''
                SELECT   SUM(FULLMARKS)
                FROM  EXAM_MARKS_ACTUAL INNER JOIN
                STUDENT_MASTER ON EXAM_MARKS_ACTUAL.Student_id = STUDENT_MASTER.Student_id AND EXAM_MARKS_ACTUAL.RegNo = STUDENT_MASTER.RegistrationNo 
                AND EXAM_MARKS_ACTUAL.Current_Year = STUDENT_MASTER.Current_Year AND EXAM_MARKS_ACTUAL.Department = STUDENT_MASTER.Department
                AND EXAM_MARKS_ACTUAL.Roll = STUDENT_MASTER.Roll INNER JOIN
                        MARKS_SETUP ON STUDENT_MASTER.Sess = MARKS_SETUP.Sess AND STUDENT_MASTER.Current_Year = MARKS_SETUP.Current_Year 
                        AND EXAM_MARKS_ACTUAL.Sess = MARKS_SETUP.Sess AND 
                        EXAM_MARKS_ACTUAL.Current_Year = MARKS_SETUP.Current_Year AND EXAM_MARKS_ACTUAL.Department = MARKS_SETUP.Department 
                        AND STUDENT_MASTER.Department = MARKS_SETUP.Department AND EXAM_MARKS_ACTUAL.Subject = MARKS_SETUP.Subject_Code
                        WHERE (STUDENT_MASTER.Sess = ?) AND (STUDENT_MASTER.Department = ?) AND (STUDENT_MASTER.Roll =?) 
            ''', (selected_sessn, selected_dept, selected_roll))
            row = cursor.fetchone()
            full_mks = row[0] if row else 0


            print(name, regdno, yr,Arr_count, Pass_count, Total_mks,per_mks, full_mks)

            # Fetch exam records
            cursor.execute('''
                SELECT 
                    EXAM_MARKS_ACTUAL.SemCode AS Sem, 
                    EXAM_MARKS_ACTUAL.Subject, 
                    EXAM_MARKS_ACTUAL.CA, 
                    EXAM_MARKS_ACTUAL.WEIGHTAGE AS WTG, 
                    EXAM_MARKS_ACTUAL.PLUS AS Plus, 
                    EXAM_MARKS_ACTUAL.TOTAL AS Total, 
                    EXAM_MARKS_ACTUAL.PASS AS Result, 
                    EXAM_MARKS_ACTUAL.Remarks
                FROM EXAM_MARKS_ACTUAL 
                INNER JOIN STUDENT_MASTER 
                    ON EXAM_MARKS_ACTUAL.Student_id = STUDENT_MASTER.Student_id 
                    AND EXAM_MARKS_ACTUAL.RegNo = STUDENT_MASTER.RegistrationNo 
                    AND EXAM_MARKS_ACTUAL.Current_Year = STUDENT_MASTER.Current_Year 
                    AND EXAM_MARKS_ACTUAL.Department = STUDENT_MASTER.Department 
                    AND EXAM_MARKS_ACTUAL.Roll = STUDENT_MASTER.Roll 
                WHERE STUDENT_MASTER.Sess = ? 
                  AND STUDENT_MASTER.Department = ? 
                  AND STUDENT_MASTER.Roll = ?
                ORDER BY CAST(SUBSTRING(EXAM_MARKS_ACTUAL.SemCode, 4, LEN(EXAM_MARKS_ACTUAL.SemCode)-3) AS INT),
                EXAM_MARKS_ACTUAL.Subject;
            ''', (selected_sessn, selected_dept, selected_roll))

            records = rows_to_dict_list(cursor)

    return render_template(
        'home.html',
        Sessn=Sessn,
        Dept=Dept,
        records=records,
        name=name,
        regdno=regdno,
        yr=yr, full_mks=full_mks, per_mks=per_mks, Pass_count=Pass_count, Arr_count=Arr_count, Total_records=Pass_count+Arr_count,
        selected_sessn=selected_sessn, Total_mks=Total_mks,
        selected_dept=selected_dept,
        roll=selected_roll
    )

#Remove trailing zeros
@main.app_template_filter('fmt')
def format_number(value):
    """Format floats nicely: 47.0 → 47, 47.5 → 47.5"""
    try:
        f = float(value)
        if f.is_integer():
            return str(int(f))
        return f"{f:.2f}".rstrip('0').rstrip('.')  
    except (ValueError, TypeError):
        return value

#About page
@main.route('/about')
def about():
    return render_template('about.html')


#Pivot report
@main.route('/semwise', methods=['GET', 'POST'])
def semwise():
    # Get filters from POST or GET
    selected_sessn = request.form.get('sessn') or request.args.get('sessn')
    selected_dept = request.form.get('dept') or request.args.get('dept')

    db = get_db()
    cursor = db.cursor()

    # Load dropdowns
    cursor.execute("SELECT DISTINCT SESS FROM STUDENT_MASTER ORDER BY SESS DESC")
    Sessn = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT DEPARTMENT FROM STUDENT_MASTER ORDER BY DEPARTMENT")
    Dept = [row[0] for row in cursor.fetchall()]

    # Pagination
    page = int(request.args.get('page', 1))
    per_page = 50

    table = None
    columns = []
    total_rows = 0

    # Only fetch data if both filters are set
    if selected_sessn and selected_dept:
        cursor.execute('''
            SELECT Roll, SemCode, Total
            FROM [Exam].[dbo].[EXAM_MARKS_ACTUAL]
            WHERE Sess = ? AND Department = ?
            ORDER BY Roll
        ''', (selected_sessn, selected_dept))
        rows = cursor.fetchall()
        df = pd.DataFrame.from_records(rows, columns=[col[0] for col in cursor.description])

        if not df.empty:
            pivot_df = pd.pivot_table(df, values='Total', index='Roll', columns='SemCode', aggfunc='sum', fill_value=0).reset_index()
            pivot_df['Roll'] = pivot_df['Roll'].astype(int)  # convert Roll to numeric
            # ---- SORT SEMCODE COLUMNS (SEM2, SEM4, SEM10...) ----
            semester_cols = sorted(
            [col for col in pivot_df.columns if col != 'Roll'],
            key=lambda x: int(x.replace('SEM', ''))
            )
            pivot_df = pivot_df[['Roll'] + semester_cols]
            pivot_df["Total"] = pivot_df[semester_cols].sum(axis=1) # Add Total column
            # ------------------------------------------------------
            pivot_df = pivot_df.sort_values('Roll')  
            total_rows = len(pivot_df)
            start = (page-1)*per_page
            end = start + per_page
            paginated_df = pivot_df.iloc[start:end]

            table = paginated_df.to_dict(orient='records')
            columns = pivot_df.columns.tolist()

        cursor.close()

    return render_template(
        'semwise.html',
        table=table,
        columns=columns,
        Sessn=Sessn,
        Dept=Dept,
        selected_sessn=selected_sessn,
        selected_dept=selected_dept,
        page=page,
        per_page=per_page,
        total_rows=total_rows
    )
#Export csv file
@main.route("/export_csv")
def export_csv():
    sessn = request.args.get("sessn")
    dept = request.args.get("dept")

    db = get_db()
    cursor = db.cursor()

    # Get complete dataset (NOT paginated)
    cursor.execute('''
        SELECT Roll, SemCode, Total
        FROM [Exam].[dbo].[EXAM_MARKS_ACTUAL]
        WHERE Sess = ? AND Department = ?
        ORDER BY Roll
    ''', (sessn, dept))
    rows = cursor.fetchall()

    if not rows:
        return "No data to export", 404

    # Create DF
    df = pd.DataFrame.from_records(rows, columns=[col[0] for col in cursor.description])

    # ========= APPLY SAME PIVOT LOGIC USED IN PAGE =========
    pivot_df = pd.pivot_table(
        df,
        values='Total',
        index='Roll',
        columns='SemCode',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    pivot_df['Roll'] = pivot_df['Roll'].astype(int)

    # Sorting SEM columns numerically (SEM1 < SEM2 < SEM10)
    semester_cols = sorted(
        [col for col in pivot_df.columns if col != 'Roll'],
        key=lambda x: int(x.replace("SEM", "").replace("Sem", ""))
    )

    pivot_df = pivot_df[['Roll'] + semester_cols]

    pivot_df = pivot_df.sort_values('Roll')
    pivot_df["Total"] = pivot_df[semester_cols].sum(axis=1)
    # ========================================================

    # Convert to CSV
    csv_buffer = BytesIO()
    csv_bytes = pivot_df.to_csv(index=False).encode("utf-8")
    csv_buffer.write(csv_bytes)
    csv_buffer.seek(0)

    filename = f"exam_marks_{sessn}_{dept}.csv"

    return send_file(
        csv_buffer,
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename
    )