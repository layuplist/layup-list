GRADE_MAPPINGS = {
    'A': 12.0,
    'A-': 11.0,
    'B+': 10.0,
    'B': 9.0,
    'B-': 8.0,
    'C+': 7.0,
    'C': 6.0,
    'C-': 5.0,
    'D': 3.0,
    'E': 0.0
}

def numeric_value_for_grade(grade):
    """
    Based on excerpt from GPA calculation:
    an A counts as 12 points, A- as 11, B+ as 10, B as 9, B- as 8, C+ as 7, C as 6, C- as 5, D as 3, and E as 0.
    Sometimes grades can come like this: A /A-
    """
    letter_grades = [g.strip() for g in grade.split("/")]
    return sum([GRADE_MAPPINGS[g] for g in letter_grades]) / len(letter_grades)
