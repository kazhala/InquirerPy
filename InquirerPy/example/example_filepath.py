from InquirerPy.resolver import prompt

questions = [{"type": "filepath", "question": "hello"}]

result = prompt(questions)
print(result)
