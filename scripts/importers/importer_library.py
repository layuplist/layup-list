import HTMLParser
html_parser = HTMLParser.HTMLParser()

DEPARTMENT_CORRECTIONS = {
    "M&SS": "QSS",
    "WGST": "WGSS"
}

def clean_department_code(department):
    department = html_parser.unescape(department.strip()).upper()
    return DEPARTMENT_CORRECTIONS[department] if department in DEPARTMENT_CORRECTIONS else department
