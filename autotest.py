import syntax
import csv
import pandas as pd
import lexer
import openpyxl
from openpyxl.styles import PatternFill

# exception si 252
# if want niyo try, download https://docs.google.com/spreadsheets/d/1xzn_b8FHk7-cKC7gAeeUlDnoTKlbY8DXVyR3XfJoj6o/edit#gid=1770890317 as csv
# then rename it to aeyetest.csv and put it in A-EYE folder (bali marereplace niya ung current)
# run this and check results.xlsx for results
df = pd.read_csv('A-EYE\\aeyetest.csv')

def analyze_syntax(code):
    result, errors = lexer.analyze_text(code)
    if not errors:
        syntax_result = syntax.analyze_syntax(result)

    if errors:
        for error in errors:
            return error.as_string()
    else:
        return syntax_result


string = df['test_item'][0]
with open('A-EYE\\file.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Test Item', 'Expected', 'Detail', 'Remarks', 'Result'])
    for index, row in df.iterrows():
        string = row['test_item']
        expected = row['expected']
        delims = ['\n', '\r', '\t']
        for delimiter in delims:
            string = " ".join(string.split(delimiter))
        result = analyze_syntax(string)
        if result != 'Syntax analysis successful':
            detail = 'Syntax Error'
        else:
            detail = 'No Syntax Error'
        
        remarks = 'Pass' if detail == expected else 'Fail'
        writer.writerow([string, str(expected).strip(), detail, remarks, result ])

file = pd.read_csv('A-EYE\\file.csv', encoding='unicode_escape')
results = pd.ExcelWriter('A-EYE\\results.xlsx')
file.to_excel(results, index=False)
results.save()
wb = openpyxl.load_workbook('A-EYE\\results.xlsx')
ws = wb['Sheet1']

passed = PatternFill(patternType='solid', fgColor='32a862')
fail = PatternFill(patternType='solid', fgColor='ff0000')
for i in range(2, len(df) + 2):
    if ws[F'D{i}'].value == 'Pass':
        ws[F'D{i}'].fill = passed
    else:
        ws[F'D{i}'].fill = fail

wb.save('A-EYE\\results.xlsx')

number_of_passed = file.value_counts('Remarks')['Pass']
print(f'Passing Rate: {round(number_of_passed/len(file)*100,2)}%')

