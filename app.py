from flask import Flask, request, render_template, redirect, url_for
import random
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import os
from flask import flash

app = Flask(__name__)

class TimeTableGenerator:
    def __init__(self):
        self.periods_per_day = 6
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        self.class_subjects = {}
        self.teachers = {}
        self.teacher_schedule = defaultdict(lambda: defaultdict(set))
        self.class_teacher_assignments = defaultdict(dict)

    def initialize_empty_timetables(self) -> Dict:
        return {
            class_name: {day: ["Unassigned" for _ in range(self.periods_per_day)]
                        for day in self.days}
            for class_name in self.class_subjects.keys()
        }

    def is_lab_subject(self, subject: str, class_name: str = None) -> bool:
        if class_name:
            subject_info = self.class_subjects[class_name].get(subject)
        else:
            subject_info = self.class_subjects[list(self.class_subjects.keys())[0]].get(subject)
        return isinstance(subject_info, dict) and "consecutive" in subject_info

    def get_subject_hours(self, subject: str, class_name: str) -> int:
        subject_info = self.class_subjects[class_name].get(subject)
        if isinstance(subject_info, dict):
            return subject_info["hours"]
        return subject_info

    def get_consecutive_periods(self, subject: str, class_name: str) -> int:
        subject_info = self.class_subjects[class_name].get(subject)
        if isinstance(subject_info, dict):
            return subject_info.get("consecutive", 1)
        return 1

    def get_available_teachers(self, subject: str, day: str, period: int,
                             class_name: str) -> List[str]:
        available_teachers = []
        for teacher, subjects in self.teachers.items():
            if subject in subjects:
                if (class_name in self.class_teacher_assignments and
                    subject in self.class_teacher_assignments[class_name] and
                    self.class_teacher_assignments[class_name][subject] != teacher):
                    continue
                is_available = True
                if teacher in self.teacher_schedule[day][period]:
                    is_available = False
                if is_available:
                    available_teachers.append(teacher)
        return available_teachers

    def assign_teacher(self, teacher: str, day: str, period: int,
                      class_name: str, subject: str):
        self.teacher_schedule[day][period].add(teacher)
        self.class_teacher_assignments[class_name][subject] = teacher

    def can_schedule_subject(self, subject: str, day: str, timetable: Dict) -> bool:
        return subject not in timetable[day]

    def count_subject_hours(self, subject: str, timetable: Dict) -> int:
        return sum(day.count(subject) for day in timetable.values())

    def find_consecutive_slots(self, timetable: Dict, day: str,
                             required_slots: int) -> List[int]:
        if required_slots == 3:
            possible_starts = [0, 3]
            available_slots = []
            for start in possible_starts:
                slots = range(start, start + required_slots)
                if all(timetable[day][slot] == "Unassigned" for slot in slots):
                    available_slots.append(start)
            return available_slots
        else:
            available_slots = []
            for i in range(self.periods_per_day - required_slots + 1):
                slots = range(i, i + required_slots)
                if all(timetable[day][slot] == "Unassigned" for slot in slots):
                    available_slots.append(i)
            return available_slots

    def schedule_lab_session(self, timetable: Dict, class_name: str,
                           lab_subject: str) -> Tuple[bool, Dict]:
        consecutive_periods = self.get_consecutive_periods(lab_subject, class_name)
        total_hours = self.get_subject_hours(lab_subject, class_name)
        sessions_needed = total_hours // consecutive_periods

        for _ in range(sessions_needed):
            session_scheduled = False
            available_days = random.sample(self.days, len(self.days))

            for day in available_days:
                if session_scheduled:
                    break

                available_slots = self.find_consecutive_slots(timetable, day, consecutive_periods)
                if not available_slots:
                    continue

                start_period = random.choice(available_slots)
                available_teachers = self.get_available_teachers(
                    lab_subject, day, start_period, class_name)

                valid_teachers = []
                for teacher in available_teachers:
                    teacher_available = True
                    for period in range(start_period, start_period + consecutive_periods):
                        if teacher in self.teacher_schedule[day][period]:
                            teacher_available = False
                            break
                    if teacher_available:
                        valid_teachers.append(teacher)

                if valid_teachers:
                    teacher = random.choice(valid_teachers)
                    for period in range(start_period, start_period + consecutive_periods):
                        timetable[day][period] = lab_subject
                        self.assign_teacher(teacher, day, period, class_name, lab_subject)
                    session_scheduled = True

            if not session_scheduled:
                return False, timetable

        return True, timetable

    def generate_timetable(self) -> Dict:
        max_attempts = 100
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            timetables = self.initialize_empty_timetables()
            self.teacher_schedule.clear()
            self.class_teacher_assignments.clear()

            scheduling_successful = True

            for class_name in self.class_subjects.keys():
                lab_subjects = [subject for subject in self.class_subjects[class_name].keys()
                              if self.is_lab_subject(subject, class_name)]

                for lab_subject in lab_subjects:
                    success, timetables[class_name] = self.schedule_lab_session(
                        timetables[class_name], class_name, lab_subject)
                    if not success:
                        scheduling_successful = False
                        break

                if not scheduling_successful:
                    break

            if not scheduling_successful:
                continue

            for class_name in self.class_subjects.keys():
                regular_subjects = [(subject, hours)
                                  for subject, hours in self.class_subjects[class_name].items()
                                  if not self.is_lab_subject(subject, class_name)]

                subjects_to_schedule = []
                for subject, hours in regular_subjects:
                    subjects_to_schedule.extend([subject] * hours)
                random.shuffle(subjects_to_schedule)

                for subject in subjects_to_schedule:
                    placed = False
                    for day in random.sample(self.days, len(self.days)):
                        if placed:
                            break
                        if not self.can_schedule_subject(subject, day, timetables[class_name]):
                            continue

                        available_slots = [i for i, s in enumerate(timetables[class_name][day])
                                         if s == "Unassigned"]
                        random.shuffle(available_slots)

                        for period in available_slots:
                            available_teachers = self.get_available_teachers(
                                subject, day, period, class_name)
                            if available_teachers:
                                teacher = random.choice(available_teachers)
                                timetables[class_name][day][period] = subject
                                self.assign_teacher(teacher, day, period,
                                                 class_name, subject)
                                placed = True
                                break

                    if not placed:
                        scheduling_successful = False
                        break

                if not scheduling_successful:
                    break

            if scheduling_successful:
                for class_name in timetables:
                    for day in self.days:
                        for period in range(self.periods_per_day):
                            if timetables[class_name][day][period] == "Unassigned":
                                timetables[class_name][day][period] = "Free"
                return timetables

        raise Exception("Could not generate valid timetables after maximum attempts")

    def print_timetables(self, timetables: Dict) -> str:
        output = ""
        for class_name in timetables.keys():
            output += f"\nTime Table for {class_name}\n"
            output += "-" * 100 + "\n"
            output += f"{'Day':<12}"
            for i in range(self.periods_per_day):
                output += f"Period {i+1:<14}"
            output += "\n" + "-" * 100 + "\n"

            for day in self.days:
                output += f"{day:<12}"
                for subject in timetables[class_name][day]:
                    if self.is_lab_subject(subject, class_name):
                        output += f"*{subject:<13}"
                    else:
                        output += f"{subject:<14}"
                output += "\n"
            output += "-" * 100 + "\n"

            output += f"\nSubject Hours Distribution for {class_name}:\n"
            total_free = sum(day.count("Free") for day in timetables[class_name].values())

            for subject in self.class_subjects[class_name]:
                scheduled = self.count_subject_hours(subject, timetables[class_name])
                required = self.get_subject_hours(subject, class_name)
                teacher = self.class_teacher_assignments[class_name].get(subject, "None")
                output += f"{subject}: Scheduled - {scheduled}, Required - {required}, Teacher - {teacher}\n"
            output += f"Total Free Periods: {total_free}\n"
            output += "-" * 100 + "\n"
        return output


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
        # Get form data
        classes = request.form.get('classes', '').split(',')
        classes = [class_name.strip() for class_name in classes if class_name.strip()]
        
        default_subjects = request.form.get('default_subjects', '')
        periods_per_day = int(request.form.get('periods_per_day', 6))
        
        days = request.form.getlist('days')
        if not days:
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        # Parse default subjects
        subject_hours = {}
        for subject in default_subjects.split(','):
            subject = subject.strip()
            if ':' in subject:
                name, hours = subject.split(':')
                subject_hours[name.strip()] = int(hours.strip())
        
        # Parse lab subjects
        lab_subjects = request.form.getlist('lab_subjects[]')
        lab_hours = request.form.getlist('lab_hours[]')
        lab_consecutive = request.form.getlist('lab_consecutive[]')
        
        # Parse teachers
        teacher_names = request.form.getlist('teacher_names[]')
        teacher_subjects = request.form.getlist('teacher_subjects[]')
        
        # Create a TimeTableGenerator instance
        generator = TimeTableGenerator()
        generator.periods_per_day = periods_per_day
        generator.days = days
        
        # Configure class subjects
        generator.class_subjects = {}
        for class_name in classes:
            generator.class_subjects[class_name] = {}
            
            # Add regular subjects
            for subject, hours in subject_hours.items():
                generator.class_subjects[class_name][subject] = hours
            
            # Add lab subjects
            for i in range(len(lab_subjects)):
                if lab_subjects[i].strip():
                    generator.class_subjects[class_name][lab_subjects[i].strip()] = {
                        "hours": int(lab_hours[i]),
                        "consecutive": int(lab_consecutive[i])
                    }
        
        # Configure teachers
        generator.teachers = {}
        for i in range(len(teacher_names)):
            if teacher_names[i].strip():
                subjects = [s.strip() for s in teacher_subjects[i].split(',') if s.strip()]
                generator.teachers[teacher_names[i].strip()] = subjects
        
        # Generate timetables
        timetables = generator.generate_timetable()
        
        # Pass all necessary data to the template
        return render_template('results.html', 
                              timetables=timetables,
                              class_subjects=generator.class_subjects,
                              class_teacher_assignments=generator.class_teacher_assignments,
                              days=generator.days,
                              periods_per_day=generator.periods_per_day,
                              is_lab_subject=generator.is_lab_subject,
                              count_subject_hours=generator.count_subject_hours)
    
    except Exception as e:
        # Make sure flash message category matches your CSS classes
        flash(str(e), 'error')
        return redirect(url_for('setup'))
app.secret_key = os.urandom(24)
if __name__ == '__main__':
    app.run(debug=True)
