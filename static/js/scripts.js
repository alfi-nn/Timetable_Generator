// Tab navigation for the setup form
function showTab(tabId) {
    // Hide all tabs
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.classList.remove('active');
    });
    
    // Show the selected tab
    document.getElementById(tabId + '-tab').classList.add('active');
    
    // Add active class to the clicked button
    document.querySelector(`.tab-btn[onclick="showTab('${tabId}')"]`).classList.add('active');
}

// Add another lab subject input
document.addEventListener('DOMContentLoaded', function() {
    const addLabBtn = document.getElementById('add-lab');
    if (addLabBtn) {
        addLabBtn.addEventListener('click', function() {
            const labSubjectInputs = document.querySelector('.lab-subject-inputs');
            const newLabSubject = document.createElement('div');
            newLabSubject.className = 'lab-subject';
            newLabSubject.innerHTML = `
                <input type="text" name="lab_subjects[]" placeholder="Subject name" class="lab-name">
                <input type="number" name="lab_hours[]" placeholder="Hours" min="1" max="10" class="lab-hours">
                <select name="lab_consecutive[]" class="lab-consecutive">
                    <option value="2">2 consecutive periods</option>
                    <option value="3">3 consecutive periods</option>
                </select>
                <button type="button" class="remove-btn">Remove</button>
            `;
            labSubjectInputs.appendChild(newLabSubject);
            
            // Add event listener to the new remove button
            newLabSubject.querySelector('.remove-btn').addEventListener('click', function() {
                labSubjectInputs.removeChild(newLabSubject);
            });
        });
    }
    
    // Add event listeners to existing remove buttons
    const removeButtons = document.querySelectorAll('.remove-btn');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const parent = this.parentElement;
            parent.parentElement.removeChild(parent);
        });
    });
    
    // Add another teacher input
    const addTeacherBtn = document.getElementById('add-teacher');
    if (addTeacherBtn) {
        addTeacherBtn.addEventListener('click', function() {
            const teachersContainer = document.getElementById('teachers-container');
            const teacherCount = teachersContainer.children.length + 1;
            
            const newTeacher = document.createElement('div');
            newTeacher.className = 'teacher-input';
            newTeacher.innerHTML = `
                <div class="form-group">
                    <label for="teacher-${teacherCount}">Teacher Name:</label>
                    <input type="text" id="teacher-${teacherCount}" name="teacher_names[]" required>
                </div>
                <div class="form-group">
                    <label for="teacher-subjects-${teacherCount}">Subjects (comma separated):</label>
                    <input type="text" id="teacher-subjects-${teacherCount}" name="teacher_subjects[]" required>
                </div>
                <button type="button" class="remove-btn">Remove</button>
            `;
            teachersContainer.appendChild(newTeacher);
            
            // Add event listener to the new remove button
            newTeacher.querySelector('.remove-btn').addEventListener('click', function() {
                teachersContainer.removeChild(newTeacher);
            });
        });
    }
});

// Function to show the selected timetable
function showTimetable() {
    const selectedClass = document.getElementById('class-select').value;
    const timetables = document.querySelectorAll('.timetable-container');
    
    timetables.forEach(timetable => {
        timetable.style.display = 'none';
    });
    
    document.getElementById('timetable-' + selectedClass).style.display = 'block';
}

// Function to print the timetable
function printTimetable() {
    const selectedClass = document.getElementById('class-select').value;
    const timetableElement = document.getElementById('timetable-' + selectedClass);
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write('<html><head><title>Print Timetable</title>');
    printWindow.document.write('<link rel="stylesheet" href="/static/css/styles.css">');
    printWindow.document.write('</head><body>');
    printWindow.document.write('<div class="print-container">');
    printWindow.document.write(timetableElement.innerHTML);
    printWindow.document.write('</div></body></html>');
    printWindow.document.close();
    
    printWindow.onload = function() {
        printWindow.print();
        printWindow.close();
    };
}

// Function to export to PDF (this would typically use a library like jsPDF)
// For a beginner implementation, we'll just alert the user
function exportToPDF() {
    alert("This feature would require a PDF generation library like jsPDF. For a full implementation, you would integrate such a library to convert the table to PDF format.");
}