from flask import Flask, request, render_template, redirect, url_for, flash
import random
from typing import Dict, List, Set, Tuple
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Required for flashing messages

class TimeTableGenerator:
    def __init__(self):
        self.class_subjects: Dict[str, Dict[str, int]] = {}
        self.teachers: Dict[str, List[str]] = {}
        self.periods_per_day: int = 6
        self.days: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.class_teacher_assignments: Dict[str, Dict[str, str]] = {}
        self.is_lab_subject: Dict[str, bool] = {}
        self.count_subject_hours: Dict[str, int] = {}
    
    def generate_timetable(self) -> Dict[str, Dict[str, List[str]]]:
        timetables = {}
        for class_name, subjects in self.class_subjects.items():
            timetable = {day: ["" for _ in range(self.periods_per_day)] for day in self.days}
            subject_list = [subject for subject, hours in subjects.items() for _ in range(hours)]
            random.shuffle(subject_list)
            
            period = 0
            for day in self.days:
                for p in range(self.periods_per_day):
                    if subject_list:
                        subject = subject_list.pop()
                        timetable[day][p] = subject
            
            timetables[class_name] = timetable
        return timetables

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup', methods=['GET'])
def setup():
    return render_template('setup.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        classes = request.form.get('classes', '').split(',')
        classes = [class_name.strip() for class_name in classes if class_name.strip()]
        
        default_subjects = request.form.get('default_subjects', '')
        periods_per_day = int(request.form.get('periods_per_day', 6))
        days = request.form.getlist('days') or ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        subject_hours = {
            subject.split(':')[0].strip(): int(subject.split(':')[1].strip())
            for subject in default_subjects.split(',') if ':' in subject
        }
        
        lab_subjects = request.form.getlist('lab_subjects[]')
        lab_hours = request.form.getlist('lab_hours[]')
        lab_consecutive = request.form.getlist('lab_consecutive[]')
        
        teacher_names = request.form.getlist('teacher_names[]')
        teacher_subjects = request.form.getlist('teacher_subjects[]')
        
        generator = TimeTableGenerator()
        generator.periods_per_day = periods_per_day
        generator.days = days
        
        for class_name in classes:
            generator.class_subjects[class_name] = subject_hours.copy()
            for i in range(len(lab_subjects)):
                if lab_subjects[i].strip():
                    generator.class_subjects[class_name][lab_subjects[i].strip()] = {
                        "hours": int(lab_hours[i]),
                        "consecutive": int(lab_consecutive[i])
                    }
        
        generator.teachers = {
            teacher_names[i].strip(): [s.strip() for s in teacher_subjects[i].split(',') if s.strip()]
            for i in range(len(teacher_names)) if teacher_names[i].strip()
        }
        
        timetables = generator.generate_timetable()
        
        return render_template(
            'results.html', 
            timetables=timetables,
            class_subjects=generator.class_subjects,
            class_teacher_assignments=generator.class_teacher_assignments,
            days=generator.days,
            periods_per_day=generator.periods_per_day,
            is_lab_subject=generator.is_lab_subject,
            count_subject_hours=generator.count_subject_hours
        )
    except Exception as e:
        flash(f"Error generating timetable: {str(e)}", "error")
        return redirect(url_for('setup'))

if __name__ == '__main__':
    app.run(debug=True)
