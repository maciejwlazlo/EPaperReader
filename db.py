import sqlite3
import getpass
import hashlib
import time


class User:
    def __init__(self, idnum, fname, lname, mname, userType, year):
        self.uname = idnum
        self.fname = fname
        self.lname = lname
        self.mname = mname
        self.userType = userType
        self.year = year

class Book:
    def __init__(self, BookID, Title, Author, FilePath, Year):
        self.bid = BookID
        self.title = Title
        self.author = Author
        self.fpath = FilePath
        self.year = Year

class Bookmark:
    def  __init__(self, idnum, BookID, Chapter, Line, SampleText):
        self.idnum = idnum
        self.bid = BookID
        self.chapter = Chapter
        self.line = Line
        self.sampletext = SampleText


class Score:
    def __init__(self, BookID, Chapter, StudentID, ScoreValue, TotalScore):
        self.bookid = BookID
        self.chapter = Chapter
        self.studentid = StudentID
        self.score = ScoreValue
        self.total = TotalScore


class Question:
    def __init__(self, Chapter, Question, Choice1, Choice2, Choice3, Choice4, Answer):
    	self.chapter = Chapter
        self.question = Question
        self.choice1 = Choice1
        self.choice2 = Choice2
        self.choice3 = Choice3
        self.choice4 = Choice4
        self.answer = Answer



def Today():
    ''' Return the current date and time as string in the format mm/dd/yyyy hh:mm AM/PM '''
    dateandtime = time.strftime("%m/%d/%Y")
    return dateandtime


def LogIn(username):
    conn = sqlite3.connect('userAccounts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM userAccounts WHERE idnum=?", (username,))
    output = c.fetchone()
    if(output is None):
        c.close()
        return None
    else:
        c.execute("SELECT * FROM userAccounts WHERE idnum=?", (username,))
        output = c.fetchone()
        user = User(output[1],output[2],output[3],output[4],output[5],output[6])
        c.close()
        return user


def ListBooks(username):
    conn = sqlite3.connect('userAccounts.db')
    c = conn.cursor()
    c.execute('SELECT userType FROM userAccounts WHERE idnum=?', (username,))
    userType = c.fetchone()[0]
    if(userType=='student'):
        c.execute('SELECT year FROM userAccounts WHERE idnum=?', (username,))
        year = c.fetchone()[0]
        c.execute('SELECT * FROM Books WHERE year = ?', (year,))
    else:
        c.execute('SELECT * FROM Books')
    output = c.fetchall()

    books = []
    for i in output:
    	books.append(Book(i[0], i[1], i[2], i[3], i[4]))
    c.close()
    return books


def GetQuestions(filepath, chapter, username):
    conn = sqlite3.connect('sqlite\userAccounts.db')
    c = conn.cursor()
    c.execute("SELECT ID FROM Books WHERE FilePath = ?", (filepath,))
    BookID = c.fetchone()[0]
    questionsname = "Questions" + str(BookID)
    c.execute("SELECT * FROM "+questionsname+" WHERE Chapter=?", (chapter,))
    output = c.fetchall()
    questions = []
    for i in output:
    	questions.append(Question(i[7],i[1],i[2],i[3],i[4],i[5],i[6]))
    c.close()
    return questions


def CheckAnswer(choice, questionnumber, question):
    print 'Question num {0}, Choice {1}, Answer{2}'.format(questionnumber, choice, question[questionnumber][6])
    ans = question[questionnumber][6]
    if (ans==choice):
        return True
    else:
        return False


def StoreScores(filepath, chapter,idnum, score):
    conn = sqlite3.connect('userAccounts.db')
    c = conn.cursor()
    c.execute("SELECT ID FROM Books WHERE FilePath=?", (filepath,))
    x = c.fetchone()[0]
    c.execute("INSERT INTO Scores (BID, chapter, idnum, scores) VALUES (?,?,?,?)", (x,chapter,idnum,score))
    conn.commit()
    c.close()


def ShowScores():
    conn = sqlite3.connect('userAccounts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Scores ORDER BY idnum, Chapter")
    output = c.fetchall()
    scores=[]
    for i in output:
    	scores.append(Score(i[1],i[2],i[3],i[4]))
    c.close()
    return scores


def GetBookmarks(idnum):
    conn = sqlite3.connect('userAccounts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Bookmarks WHERE idnum=? ORDER BY ID desc", (idnum,))
    x = c.fetchall()
    bookmarks = []
    for i in x:
        bookmarks.append(Bookmark(i[1], i[2], i[3], i[4], i[5]))
    c.close()
    return bookmarks


def CreateBookmark(idnum, bid, chapter, linenum, sampletext):
    conn = sqlite3.connect('userAccounts.db')
    c = conn.cursor()
    c.execute("SELECT linenum FROM Bookmarks WHERE idnum=?", (idnum,))
    currpage = c.fetchone()
    if(currpage is None):
        c.execute("INSERT INTO Bookmarks (idnum, BID, Chapter, Linenum, SampleText) VALUES (?,?,?,?,?)", (idnum, bid,chapter,linenum,sampletext))
    else:
        c.execute("DELETE FROM Bookmarks WHERE idnum=? AND BID=?", (idnum, bid))
        c.execute("INSERT INTO Bookmarks (idnum, BID, Chapter, Linenum, SampleText) VALUES (?,?,?,?,?)", (idnum, bid,chapter,linenum,sampletext))
    conn.commit()
    c.close()


def DeleteBookmark(bid, idnum):
    conn = sqlite3.connect('userAccounts.db')
    c = conn.cursor()
    c.execute("DELETE FROM Bookmarks WHERE idnum=? AND BID=?",(idnum, bid))
    conn.commit()
    c.close()



def StudentViewScores(idnum):
    conn = sqlite3.connect('userAccounts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Scores WHERE idnum = ?", (idnum, ))
    x = c.fetchall()
    scores = []
    for i in x:
        scores.append(Score(i[1],i[2],i[3],i[4], i[5]))
    c.close()
    return scores


def StoreScore(bookid, chapter, idnum, score, total):
    conn = sqlite3.connect('userAccounts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Scores WHERE idnum=? AND Chapter=? AND BID=?", (idnum,chapter, bookid))
    if(c.fetchone() is None):
        c.execute("INSERT INTO Scores (BID, chapter, idnum, scores, total) VALUES (?,?,?,?,?)", (bookid, chapter, idnum, score, total))
        conn.commit()
    else:
        return None
    c.close()


def OpenBookmark(idnum):
    c.execute("SELECT page FROM Bookmarks WHERE idnum =?", (idnum, ))
    Page = c.fetchone()[0]
    return Page


def GetBookByBID(bid):
    conn = sqlite3.connect('userAccounts.db')
    c = conn.cursor()
    c.execute("SELECT * FROM Books WHERE id=?", (bid,))
    x = c.fetchone()
    if(x is None):
        return None
    else:
        book = Book(x[0], x[1], x[2], x[3], x[4])
        return book


def ScoreCheck(idnum, BID, chapter):
    conn = sqlite3.connect('userAccounts.db')
    c = conn.cursor()
    c.execute("SELECT scores FROM Scores WHERE idnum=? AND Chapter=? AND BID=?", (idnum,chapter, BID))
    if(c.fetchone() is None):
        return False
    else:
        return True


if __name__ == '__main__':
    print ScoreCheck(1, 1, 1)

