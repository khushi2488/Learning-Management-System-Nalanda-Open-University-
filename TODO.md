# Assignment Submission System Implementation

## Models
- [x] Add Assignment model to adminapp/models.py
- [x] Add Submission model to studentapp/models.py

## Forms
- [x] Create AssignmentForm in adminapp/forms.py
- [x] Create SubmissionForm in studentapp/forms.py

## Views
- [x] Add admin views in adminapp/views.py: create_assignment, list_assignments, view_submissions, grade_submission
- [x] Add student views in studentapp/views.py: list_assignments, submit_assignment, view_submission_status

## URLs
- [x] Update adminapp/adminappurls.py with assignment URLs
- [x] Update studentapp/studentappurls.py with assignment URLs

## Templates
- [x] Create admin templates: assignment_list.html, create_assignment.html, view_submissions.html, grade_submission.html
- [x] Create student templates: assignment_list.html, submit_assignment.html, submission_status.html

## Database
- [x] Run makemigrations and migrate

## Testing
- [x] Test assignment creation
- [x] Test submission upload
- [x] Test grading functionality
