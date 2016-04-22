import zipfile, os
import epub
from bs4 import BeautifulSoup

import epub

class QuestionItem:
    def __init__(self, question, answerid, choices):
        self.question = question
        self.answer = answerid
        self.choice = choices

soup = BeautifulSoup(open('exam.xml'), 'lxml')
soup = soup.find('quiz')
items = soup.find_all('item')
print soup

exam = []
for i in items:
    q = i.question.string
    choices = i.find_alSSSl('choice')
    c = []
    for j in choices:
        c.append(j.string)

    exam.append(QuestionItem(q, int(i['answerid']) - 1, c))

for i in exam:
    print "Question: %s" % i.question
    for j in i.choice:
        print j
    print "Answer: %s" % i.answer