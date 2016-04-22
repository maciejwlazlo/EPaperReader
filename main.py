# TODO:
# * Enable shutdown in epd.py

import argparse, db, PIL.ImageOps, textwrap, zipfile, epub, html2text, os
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from StringIO import StringIO

#Parse args
parser = argparse.ArgumentParser()
parser.add_argument("--pi", action="store_true",
                    help="Execute the script on the Raspberry Pi.")
parser.add_argument("--not-pi", action="store_true",
                    help="Please use this if you don't have a RaspPi")
args = parser.parse_args()
if not (args.pi or args.not_pi):
    parser.error('Please provide a parameter.')
    parser.print_help()

if args.not_pi:
    import os
    #pi_dir = 'D:\Documents\GitHub\EPaperReader'
    pi_dir = os.getenv("HOME") + '/Documents/Documents/GitHub/EPaperReader'

if args.pi:
    import epd
    pi_dir = '/home/pi/EPaperReader'


base = None
fnt_18px = ImageFont.truetype(pi_dir + '/resources/fonts/Charter_Regular.ttf', 18)
fnt_20px = ImageFont.truetype(pi_dir + '/resources/fonts/Charter_Regular.ttf', 20)
fnt_21px = ImageFont.truetype(pi_dir + '/resources/fonts/Charter_Regular.ttf', 21)
fnt_22px = ImageFont.truetype(pi_dir + '/resources/fonts/Charter_Regular.ttf', 22)
fnt_25px = ImageFont.truetype(pi_dir + '/resources/fonts/Charter_Bold.ttf', 25)
id_fnt   = ImageFont.truetype(pi_dir + '/resources/fonts/Inconsolata-Bold.ttf', 24)
textfnt  = ImageFont.truetype(pi_dir + '/resources/fonts/DejaVuSansMono.ttf', 15)


def Main():
    global base
    base = Image.open(pi_dir + '/resources/ui/epd.png').convert('RGB')
    
    if args.pi:
        epd.update_screen(base)

    LogInView()
    base.close()


def DisplayText(text, coordinates , fnt):
    ''' Write text to screen '''
    global base
    draw = ImageDraw.Draw(base)
    draw.text(coordinates, text, fill=(0,0,0), font=fnt)


def UpdateDisplay():
    ''' Update the EPD screen '''
    print 'Updating display'
    now = db.Today()
    # temp_im = Image.open(pi_dir + '/resources/ui/element_status_bar.png')
    # base.paste(temp_im, (0,0))
    # temp_im.close()
    DisplayText(now, (330, 2), fnt_18px)
    if args.not_pi:
        i = base.convert('1')
        i.save(pi_dir + '/screen.png', "PNG")
        i.show()
    
    if args.pi:
        epd.update_screen(base.convert('1'))


def GetInput():
    ''' Get input from keyboard or GPIO buttons '''
    if args.not_pi:
        inp = raw_input("Input: ")
        return inp.strip()
    
    if args.pi:
        inp = epd.button_press()
        return inp


def LogInView():
    global base
    print 'Log In View'

    invalid_id = False
    temp_im = Image.open(pi_dir + '/resources/ui/screen_login.png')
    while True:
        base.paste(temp_im, (0,0))

        if invalid_id: 
            DisplayText('The ID you entered is not valid.', (90, 440), fnt_22px)
        
        # TODO: 
        # idnum = NumberPad()
        # user = db.LogIn(idnum)

        user = db.LogIn(111)
        if user is not None:
            invalid_id = False
            print 'User'
            print 'ID: ' + user.uname
            print 'Name: ' + user.fname + " " + user.mname + ". " + user.lname
            print 'Type: ' + user.userType
            print 'Year Level: {0}'.format(user.year)
            MenuView(user)
            user = None
        else:
            invalid_id = True


def NumberPad():
    global base
    print 'Number Pad'

    text_buffer = ''
    crsr = [88, 375]
    keys = [['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['0',  0,   0]]
    numpad = Image.open(pi_dir + '/resources/ui/numpad.png').convert('RGB')
    cursor = Image.open(pi_dir + '/resources/ui/element_cursor.png').convert('RGB')
    eraser = ImageDraw.Draw(base)

    base.paste(numpad, (0, 520))
    base.paste(cursor, tuple(crsr))

    n = [0, 0]
    numbox = [170, 522, 214, 582]
    numregion = base.crop(tuple(numbox))
    base.paste(PIL.ImageOps.invert(numregion), numbox)
    UpdateDisplay()
    
    # Don't fuck with these numbers unless you know what you're doing!
    while True:
        inp = GetInput()
        if inp == 'w':
            base.paste(numregion, numbox)
            if cmp(n, [0, 0]) == 0:
                n[0] = 3
                numbox = [170, 729, 214, 789]
            elif cmp(n, [3, 1]) == 0 or cmp(n, [3, 2]) == 0:
                n = [2, 1]
                numbox = [225, 660, 269, 720]
            elif n[0] == 0:
                n = [3, 1]
                numbox = [225, 729, 324, 789]
            else:
                n[0] -= 1
                numbox[1] -= 69
                numbox[3] -= 69
            numregion = base.crop(tuple(numbox))
            base.paste(PIL.ImageOps.invert(numregion), numbox)
            print n
            print 'Number highlighted: {0}'.format(keys[n[0]][n[1]])
        elif inp == 'a':
            base.paste(numregion, numbox)
            if cmp(n, [3, 0]) == 0:
                n[1] = 1
                numbox = [225, 729, 324, 789]
            elif cmp(n, [3, 1]) == 0:
                n[1] = 0
                numbox = [170, 729, 214, 789]
            elif n[1] == 0:
                n[1] = 2
                numbox[0] = 280 # 170 + (55 * 2)
                numbox[2] = 324 # 214 + (55 * 2)
            else:
                n[1] -= 1
                numbox[0] -= 55
                numbox[2] -= 55
            numregion = base.crop(tuple(numbox))
            base.paste(PIL.ImageOps.invert(numregion), numbox)
            print n
            print 'Number highlighted: {0}'.format(keys[n[0]][n[1]])
        elif inp == 's':
            base.paste(numregion, numbox)
            if cmp(n, [3, 1]) == 0 or cmp(n, [3, 2]) == 0:
                n = [0, 1]
                numbox = [225, 522, 269, 582]
            elif cmp(n, [2, 1]) == 0 or cmp(n, [2, 2]) == 0:
                n = [3, 1]
                numbox = [225, 729, 324, 789]  
            elif cmp(n, [3, 0]) == 0:
                n = [0, 0]
                numbox = [170, 522, 214, 582]
            else:
                n[0] += 1
                numbox[1] += 69
                numbox[3] += 69
            numregion = base.crop(tuple(numbox))
            base.paste(PIL.ImageOps.invert(numregion), numbox)
            print n
            print 'Number highlighted: {0}'.format(keys[n[0]][n[1]])
        elif inp == 'd':
            base.paste(numregion, numbox)
            if n[1] == 2:
                n[1] = 0
                numbox[0] = 170
                numbox[2] = 214
            elif cmp(n, [3, 1]) == 0 or cmp(n, [3, 2]) == 0:
                n[1] = 0
                numbox = [170, 729, 214, 789]
            elif cmp(n, [3, 0]) == 0:
                n[1] = 1
                numbox = [225, 729, 324, 789]
            else:
                n[1] += 1
                numbox[0] += 55
                numbox[2] += 55
            numregion = base.crop(tuple(numbox))
            base.paste(PIL.ImageOps.invert(numregion), numbox)
            print n
            print 'Number highlighted: {0}'.format(keys[n[0]][n[1]])
        elif inp == 'j':
            p = keys[n[0]][n[1]]
            print 'Selected button: {0}'.format(p)
            if p == 0:
                numpad.close()
                cursor.close()
                return text_buffer
            else:
                if len(text_buffer) >= 9:
                    continue
                text_buffer += p
                eraser.rectangle(tuple(crsr) + (crsr[0] + 13, crsr[1] + 21), fill=(255,255,255))
                DisplayText(p, tuple(crsr), id_fnt)
                crsr[0] += 18
                base.paste(cursor, tuple(crsr))
        elif inp == 'k':
            if not text_buffer == '':
                text_buffer = text_buffer[:-1]
                eraser.rectangle(tuple(crsr) + (crsr[0] + 15, crsr[1] + 21), fill=(255,255,255))
                crsr[0] -= 18
                eraser.rectangle(tuple(crsr) + (crsr[0] + 15, crsr[1] + 21), fill=(255,255,255))
                base.paste(cursor, tuple(crsr))
                print 'Keyboard Buffer: {0}'.format(text_buffer)
        else:
            continue

        UpdateDisplay()


def MenuView(user):
    global base
    print 'Menu View'

    while True:
        update = True
        temp_im = Image.open(pi_dir + '/resources/ui/screen_studentmenu.png')
        name =  GetNameString(user)

        base.paste(temp_im, (0, 0))
        if user.userType == 'student':
            DisplayText(TruncateString(name, 20) + ', Grade {0}'.format(user.year), (84, 36), fnt_25px)
        elif user.userType == 'teacher':
            DisplayText('Teacher ' + TruncateString(name, 20).format(user.year), (84, 36), fnt_25px)

                    
        bookmarkerror = False
        choice = 0
        box = [64, 211, 416, 278]
        choices = ['Open Library', 'Bookmarks','View Scores', 'Log Out']
        print 'Selected Option: {0}'.format(choices[choice])
        boxregion = base.crop(tuple(box))
        base.paste(PIL.ImageOps.invert(boxregion), box)

        while True:
            if update:
                UpdateDisplay()

            update = True
            inp = GetInput()
            if inp == 'w':
                base.paste(boxregion, box)
                if choice > 0:
                    choice -= 1
                    box[1] -= 97
                    box[3] -= 97                
                else:
                    choice = len(choices) - 1
                    box = [64, 502, 416, 569]
                boxregion = base.crop(tuple(box))
                base.paste(PIL.ImageOps.invert(boxregion), box)
                print 'Selected Option: {0}'.format(choices[choice])
            elif inp == 'a':
                update = False
                continue
            elif inp == 's':
                base.paste(boxregion, box)
                if choice < len(choices) - 1:
                    choice += 1
                    box[1] += 97
                    box[3] += 97
                else:
                    choice = 0
                    box = [64, 211, 416, 278]
                boxregion = base.crop(tuple(box))
                base.paste(PIL.ImageOps.invert(boxregion), box)
                print 'Selected Option: {0}'.format(choices[choice])
            elif inp == 'd':
                update = False
                pass
            elif inp == 'j':
                if choices[choice] == 'Open Library':
                    book = LibraryView(user)
                    while book is not None:
                        print 'Opening book: {0}'.format(book.title)
                        if BookView(user, book) is None:
                            print "{0} was not found".format(book.title)
                        book = LibraryView(user)
                    break
                elif choices[choice] == 'View Scores':
                    if user.userType == 'student':
                        ScoresTableView(user)
                    elif user.userType == 'teacher':
                        student = EnterStudentIDView()
                        if student is not None:
                            ScoresTableView(student)
                            student = None
                    break
                elif choices[choice] == 'Bookmarks':
                    if BookmarksView(user) is None:
                        DisplayText("There are no bookmarks to show.", (100, 767), fnt_18px)
                        continue
                    else:
                        break
                elif choices[choice] == 'Log Out':
                    temp_im.close()
                    return
            elif inp == 'k':
                update = False
                pass
            else:
                pass


def EnterStudentIDView():
    global base
    print 'Enter Student ID' 


    temp_im = Image.open(pi_dir + '/resources/ui/screen_pickstudent.png')
    while True:
        base.paste(temp_im, (0,0))
        # TODO: 
        idnum = NumberPad()
        user = db.LogIn(idnum)

        if user is not None:
            print 'User'
            print 'ID: ' + user.uname
            print 'Name: ' + user.fname + " " + user.mname + ". " + user.lname
            print 'Type: ' + user.userType
            print 'Year Level: {0}'.format(user.year)
            return user
        else:
            return user


def LibraryView(user):
    global base
    print 'Library View'

    temp_im = Image.open(pi_dir + '/resources/ui/screen_library.png').convert('RGB')
    left = Image.open(pi_dir + '/resources/ui/arrow_left.png')
    right = Image.open(pi_dir + '/resources/ui/arrow_right.png')
    name =  GetNameString(user)
    update = True

    books = db.ListBooks(user.uname)
    print 'Number of books: %i' % len(books)
    i = 0
    while True:
        base.paste(temp_im, (0, 0))
        if user.userType == 'student':
            DisplayText(TruncateString(name, 20) + ', Grade {0}'.format(user.year), (84, 36), fnt_25px)
        elif user.userType == 'teacher':
            DisplayText('Teacher ' + TruncateString(name, 20).format(user.year), (84, 36), fnt_25px)

        if i > 0:
            base.paste(left, (162, 746), mask=left)

        if i < (len(books) - 1) / 10:
            base.paste(right, (289, 746), mask=right)

        # Display books 10 at a time
        j = 0
        while j < 10:
            k = i * 10 + j
            if k >= len(books):
                break
            DisplayText(TruncateString(books[k].title, 36), (42, 160 + (j * 58)), fnt_22px)
            DisplayText(TruncateString(books[k].author, 36), (42, 185 + (j * 58)), fnt_20px)
            j += 1
        
        selected = i * 10
        box = [32, 156, 448, 212]
        boxregion = base.crop(tuple(box))
        base.paste(PIL.ImageOps.invert(boxregion), box)

        while True:
            # print 'Selected book: {0}'.format(books[selected].title)
            if update:
                UpdateDisplay()
            
            update = True
            inp = GetInput()
            if inp == 'w':
                if selected == i * 10:
                    update = False
                else:
                    base.paste(boxregion, box)
                    selected -= 1
                    box[1] -= 58
                    box[3] -= 58
                    boxregion = base.crop(tuple(box))
                    base.paste(PIL.ImageOps.invert(boxregion), box)  
            elif inp == 'a':
                if i > 0:
                    i -= 1
                    break
                update = False
            elif inp == 's':
                if selected >= len(books) - 1 or selected == i * 10 + 9:
                    update = False
                else:
                    base.paste(boxregion, box)
                    selected += 1
                    box[1] += 58
                    box[3] += 58
                    boxregion = base.crop(tuple(box))
                    base.paste(PIL.ImageOps.invert(boxregion), box)
            elif inp == 'd':
                if i < (len(books) - 1) / 10:
                    i += 1
                    break
                update = False
            elif inp == 'j':
                if len(books) > 0:
                    return books[selected]
                update = False
            elif inp == 'k':
                temp_im.close()
                left.close()
                right.close()
                return None


def BookmarksView(user):
    global base
    print 'Bookmarks View'

    temp_im = Image.open(pi_dir + '/resources/ui/screen_bookmarks.png')
    left = Image.open(pi_dir + '/resources/ui/arrow_left.png')
    right = Image.open(pi_dir + '/resources/ui/arrow_right.png')
    name =  GetNameString(user)
    update = True

    # bookmarks = db.GetBookmarks(user.uname)
    # if not bookmarks:
    #     return None

    i = 0
    while True:
        bookmarks = db.GetBookmarks(user.uname)
        if not bookmarks:
            return None
        base.paste(temp_im, (0, 0))
        DisplayText(TruncateString(name, 20), (88, 35), fnt_25px)

        if i > 0:
            base.paste(left, (162, 746), mask=left)

        if i < (len(bookmarks) - 1) / 10:
            base.paste(right, (289, 746), mask=right)

        j = 0
        while j < 10:
            k = i * 10 + j
            if k >= len(bookmarks):
                break
            DisplayText(TruncateString(db.GetBookByBID(bookmarks[k].bid).title, 40), (42, 160 + (j * 58)), fnt_22px)
            DisplayText(TruncateString('Chapter {0}: {1}'.format(bookmarks[k].chapter, bookmarks[k].sampletext), 30), (42, 185 + (j * 58)), fnt_18px)
            j += 1
        
        selected = i * 10
        box = [32, 156, 448, 212]
        boxregion = base.crop(tuple(box))
        base.paste(PIL.ImageOps.invert(boxregion), box)

        while True:
            if update:
                UpdateDisplay()
            
            update = True
            inp = GetInput()
            if inp == 'w':
                if selected == i * 10:
                    update = False
                else:
                    base.paste(boxregion, box)
                    selected -= 1
                    box[1] -= 58
                    box[3] -= 58
                    boxregion = base.crop(tuple(box))
                    base.paste(PIL.ImageOps.invert(boxregion), box)  
            elif inp == 'a':
                if i > 0:
                    i -= 1
                    break
                update = False
            elif inp == 's':
                if selected >= len(bookmarks) - 1 or selected == i * 10 + 9:
                    update = False
                else:
                    base.paste(boxregion, box)
                    selected += 1
                    box[1] += 58
                    box[3] += 58
                    boxregion = base.crop(tuple(box))
                    base.paste(PIL.ImageOps.invert(boxregion), box)
            elif inp == 'd':
                if i < len(bookmarks) / 10:
                    i += 1
                    break
                update = False
            elif inp == 'j':
                book = db.GetBookByBID(bookmarks[selected].bid)
                BookView(user, book, bookmarks[selected])
                update = True
                bookmarks = db.GetBookmarks(user.uname)
                if not bookmarks:
                    return None
                break
            elif inp == 'k':
                temp_im.close()
                left.close()
                right.close()
                return "Success"


def BookView(user, book, bookmark=None):
    global base
    print 'Book View'

    temp_im = Image.open(pi_dir + '/resources/ui/screen_bookview.png').convert('RGB')
    pagewrap = textwrap.TextWrapper(width=858, break_long_words=False, replace_whitespace=False)
    linewrap = textwrap.TextWrapper(width=43, break_long_words=True, replace_whitespace=False)
    textregion = (45, 92, 437, 745)
    draw = ImageDraw.Draw(base)
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.body_width = 0
    h.single_line_break = True
    update = True

    ebook = epub.OpenEpub(book.fpath)
    if ebook is None:
        return

    contents = epub.GetTableOfContents(ebook)
    if bookmark is None:
        cons = TableOfContentsView(user, book, contents, -1)
    else:
        cons = bookmark.chapter

    if cons is None or cons < 0:
        return None

    while cons < len(contents):
        if cons < 0:
            break

        base.paste(temp_im, (0,0))
        DisplayText(TruncateString(book.title, 30), (104, 36), fnt_21px)
        DisplayText(TruncateString(contents[cons][0], 35), (40, 62), fnt_18px)

        print 'Loaded content: {0}'.format(contents[cons][1])

        soup = BeautifulSoup(ebook.read(contents[cons][1]), 'lxml')
        chaptertext = h.handle(soup.find('body').prettify())
        paragraphs = chaptertext.splitlines(True)

        print chaptertext
        # Get all image links
        images = soup.find_all('img')
        imagelinks = []
        imagemd = []
        for i in images:
            imagemd.append(h.handle(i.prettify()).strip())
            imagelinks.append(i['src'])

        # Find the paragraphs that contain links
        for n, i in enumerate(paragraphs):
            k = i.strip()
            if k in imagemd:
                paragraphs[n] = (imagelinks[imagemd.index(k)], )

        # Split paragraphs into lines
        lines = []
        for i in paragraphs:
            if isinstance(i, tuple):
                lines.append(i)
                continue

            x = linewrap.wrap(i)
            if x == []:
                lines.append('')
            else:
                lines.extend(x)

        # for x, y in enumerate(lines):
        #     print "Line: {0}, {1}".format(x, y.encode('utf-8'))
        print lines

        if bookmark is None:
            line = 0
        else:
            line = bookmark.line
        # print "Line: {0}, {1}".format(line, lines[line].encode('utf-8'))
        ctr = 0
        tempctr = 0
        imgflag = False
        textarea = list(textregion)
        draw.rectangle(textregion, fill=(255,255,255))
        while line <= len(lines):
            # print line
            if textarea[1] <= textregion[3] and line <= len(lines) - 1:
                if isinstance(lines[line], tuple):
                    imageloc = os.path.dirname(contents[cons][1])
                    if imageloc:
                        imageloc = '{0}/'.format(imageloc)
                    imageloc = os.path.normpath('{0}{1}'.format(imageloc, lines[line][0]))
                    img = Image.open(StringIO(ebook.read(imageloc))).convert('RGBA')
                    print "Opening Image: {0}".format(imageloc)
                    print img.size

                    # Resizing image
                    if img.width > 392 or img.height > 653 :
                        ratio = min(392.0 / img.width, 653.0 / img.height)
                        newsize = (int(ratio * img.width), int(ratio * img.height))
                        img.thumbnail(newsize, PIL.Image.ANTIALIAS)

                    if textarea[1] + img.height <= textarea[3]:
                        base.paste(img, (240 - (img.width / 2), textarea[1] + 2), mask=img)
                        textarea[1] += img.height
                        line += 1
                        ctr += 1
                    else:
                        textarea[1] += textarea[3] 
                else:
                    if lines[line] == '\n':
                        pass
                    else:
                        DisplayText(lines[line], tuple(textarea[0:2]), textfnt)
                        textarea[1] += 16
                    line += 1
                    ctr += 1
                continue

            print line
            print ctr
            if update:
                UpdateDisplay()

            update = True
            inp = GetInput()
            if inp == 'a':
                textarea = list(textregion)
                draw.rectangle((42, 92, 437, 757), fill=(255,255,255))
                draw.rectangle((0, 764, 479, 799), fill=(255,255,255))
                if line - (ctr * 2) >= 0:
                    line -= ctr * 2
                elif line - ctr == 0:
                    cons -= 1
                    break
                else:
                    line = 0

                ctr = 0
                continue
            elif inp == 'd':
                textarea = list(textregion)
                draw.rectangle((42, 92, 437, 757), fill=(255,255,255))
                draw.rectangle((0, 764, 479, 799), fill=(255,255,255))
                if line >= len(lines):
                    cons += 1
                    break
                ctr = 0
                continue
            elif inp == 'w':
                base.paste(temp_im, (0,0))
                cons = TableOfContentsView(user, book, contents, cons)
                DisplayText(book.title, (104, 36), fnt_21px)
                DisplayText(contents[cons][0], (40, 62), fnt_18px)
                textarea = list(textregion)
                draw.rectangle((42, 92, 437, 757), fill=(255,255,255))
                break
            elif inp == 's':
                db.CreateBookmark(user.uname, book.bid, cons, line - ctr, '{0}'.format(lines[line - ctr]))
                draw.rectangle((0, 764, 479, 799), fill=(255,255,255))
                DisplayText("Bookmark created.", (144, 766), fnt_18px)
                UpdateDisplay()
                # base.paste(temp_im, (0,0))
                # DisplayText(TruncateString(book.title, 30), (104, 36), fnt_21px)
                # DisplayText(TruncateString(contents[cons][0], 35), (40, 62), fnt_18px)
                update = False
                continue
            elif inp == 'j':
                print "Chapter: " + contents[cons][0]
                draw.rectangle((0, 764, 479, 799), fill=(255,255,255))
                if db.ScoreCheck(user.uname, book.bid, contents[cons][0]):
                    print 'You have already taken this exam'
                    DisplayText("You have already taken this exam.", (100, 767), fnt_18px)
                    UpdateDisplay()
                    update = False
                else:
                    result = ExamView(user, book, ebook, contents[cons][1], contents[cons][0])
                    if result  == 'No exam':
                        print 'This chapter has no exam'
                        DisplayText("This chapter has no exam.", (100, 767), fnt_18px)
                        continue
                    elif result == 'Cancelled':
                        print 'You just cancelled the exam'    
                        # cons = TableOfContentsView(user, book, contents, cons)
                        base.paste(temp_im, (0,0))
                        DisplayText(book.title, (104, 36), fnt_21px)
                        DisplayText(contents[cons][0], (40, 62), fnt_18px)
                        textarea = list(textregion)
                        draw.rectangle((42, 92, 437, 757), fill=(255,255,255))
                        DisplayText("You just cancelled the exam.", (100, 767), fnt_18px)
                        line -= ctr
                        ctr = 0
                        continue
                    elif result == 'Success':
                        print 'Exam was conducted peacefully'
                        base.paste(temp_im, (0,0))
                        DisplayText(book.title, (104, 36), fnt_21px)
                        DisplayText(contents[cons][0], (40, 62), fnt_18px)
                        textarea = list(textregion)
                        draw.rectangle((42, 92, 437, 757), fill=(255,255,255))
                        cons += 1
                    break
            elif inp == 'k':
                line -= ctr
                return 'Cancelled'

    return 'Success'


def TableOfContentsView(user, book, toc, chapindex):
    global base
    print 'Table of Contents View'

    temp_im = Image.open(pi_dir + '/resources/ui/screen_tableofcontents.png').convert('RGB')
    left = Image.open(pi_dir + '/resources/ui/arrow_left.png')
    right = Image.open(pi_dir + '/resources/ui/arrow_right.png')
    update = True


    i = 0
    while True:
        base.paste(temp_im, (0, 0))
        DisplayText(TruncateString(book.title, 30), (88, 35), fnt_25px)

        if i > 0:
            base.paste(left, (162, 746), mask=left)

        if i < (len(toc) - 1) / 17:
            base.paste(right, (289, 746), mask=right)

        j = 0
        while j < 10:
            k = i * 10 + j
            if k >= len(toc):
                break
            if len(toc[k][0]) > 20:
                toc[k][0] = toc[k][0][0:27] + '...'
            DisplayText(TruncateString(toc[k][0], 35), (42, 170 + (j * 58)), fnt_22px)
            j += 1

        selected = i * 10
        box = [32, 156, 448, 212]
        boxregion = base.crop(tuple(box))
        base.paste(PIL.ImageOps.invert(boxregion), box)

        while True:
            print 'Selected chapter: {0}'.format(toc[selected][0])
            if update:
                UpdateDisplay()
            
            update = True
            inp = GetInput()
            if inp == 'w':
                if selected == i * 10:
                    update = False
                else:
                    base.paste(boxregion, box)
                    selected -= 1
                    box[1] -= 58
                    box[3] -= 58
                    boxregion = base.crop(tuple(box))
                    base.paste(PIL.ImageOps.invert(boxregion), box)  
            elif inp == 'a':
                if i > 0:
                    i -= 1
                    break
                update = False
            elif inp == 's':
                if selected >= len(toc) - 1 or selected == i * 17 + 16:
                    update = False
                else:
                    base.paste(boxregion, box)
                    selected += 1
                    box[1] += 58
                    box[3] += 58
                    boxregion = base.crop(tuple(box))
                    base.paste(PIL.ImageOps.invert(boxregion), box)
            elif inp == 'd':
                if i < (len(toc) - 1) / 17:
                    i += 1
                    break
                update = False
            elif inp == 'j':
                return selected
            elif inp == 'k':
                temp_im.close()
                left.close()
                right.close()
                return chapindex


def ExamView(user, book, ebook, chappath, chaptitle):
    global base
    print 'Exam View'

    temp_im = Image.open(pi_dir + '/resources/ui/screen_exam.png')
    name =  GetNameString(user)
    questionbox = (42, 129, 437, 398)
    choicebox = (42, 411, 438, 449)
    draw = ImageDraw.Draw(base)
    update = True
    score = 0
    q = 0

    exam = GetExam(ebook, chappath)
    if not exam:
        return 'No exam'

    while q < len(exam):
        base.paste(temp_im, (0,0))
        DisplayText(book.title, (104, 33), fnt_25px)
        DisplayText(chaptitle, (136, 57), fnt_25px)
        DisplayText('{0}'.format(q + 1), (167, 83), fnt_25px)
        if q < 0:
            update = False

        # Display Question
        text = exam[q].question
        choices = exam[q].choices
        textarea = list(questionbox)
        choicearea = list(choicebox)
        text = textwrap.wrap(text, width=40, break_long_words=True, replace_whitespace=False)
        for t in text:
            DisplayText(t, (textarea[0] + 5, textarea[1] + 5), textfnt)
            textarea[1] += 16

        # Display Choices
        for c in choices:
            DisplayText(c, (choicearea[0] + 5, choicearea[1] + 9), textfnt)
            choicearea[1] += 50
            choicearea[3] += 50

        select = 0
        choicearea = list(choicebox)
        choiceregion = base.crop(tuple(choicearea))
        base.paste(PIL.ImageOps.invert(choiceregion), choicearea)
        while True:
            print "Selected choice: {0}".format(choices[select])
            if update:
                UpdateDisplay()

            update = True
            inp = GetInput()
            
            if inp == 'w':
                base.paste(choiceregion, choicearea)
                if select > 0:
                    choicearea[1] -= 50
                    choicearea[3] -= 50
                    select -= 1
                else:
                    select = len(choices) - 1
                    choicearea = [42, 561, 438, 599]
                choiceregion = base.crop(tuple(choicearea))
                base.paste(PIL.ImageOps.invert(choiceregion), choicearea) 
            elif inp == 's':
                base.paste(choiceregion, choicearea)
                if select < 3:
                    choicearea[1] += 50
                    choicearea[3] += 50
                    select += 1
                else: 
                    select = 0
                    choicearea = [42, 411, 438, 449]
                choiceregion = base.crop(tuple(choicearea))
                base.paste(PIL.ImageOps.invert(choiceregion), choicearea)                
            elif inp == 'a':
                if q - 1 >= 0:
                    q -= 1
                    score -= 1
                    break
                update = False
                continue
            elif inp == 'd':
                update = False
            elif inp == 'j':
                if exam[q].answer == select:
                    score += 1
                    print 'Correct answer'
                else:
                    print 'Wrong answer'
                q += 1
                break
            elif inp == 'k':
                return 'Cancelled'

    ScoreView(user, book, chaptitle, score, len(exam))
    return None


def ScoreView(user, book, chapter, score, total):
    global base
    print 'Score View'
    temp_im = Image.open(pi_dir + '/resources/ui/screen_scores.png').convert('RGB')
    base.paste(temp_im, (0,0))
    DisplayText('Name: {0}'.format(TruncateString(GetNameString(user), 20)), (50, 136), textfnt)
    DisplayText('Book: {0}'.format(book.title), (50, 157), textfnt)
    DisplayText('Chapter: {0}'.format(chapter) , (50, 178), textfnt)
    DisplayText('You got {0} correct answers out of {1}.'.format(score, total), (50, 199), textfnt)

    update = True
    while True:
        if update:
            UpdateDisplay()

        inp = GetInput()
        if inp == 'j' or inp == 'k':
            temp_im.close()
            db.StoreScore(book.bid, chapter, user.uname, score, total)
            return None
        else:
            update = False


def ScoresTableView(user):
    global base
    print 'Scores Table View'

    temp_im = Image.open(pi_dir + '/resources/ui/screen_scorestableview.png').convert('RGB')
    left = Image.open(pi_dir + '/resources/ui/arrow_left.png')
    right = Image.open(pi_dir + '/resources/ui/arrow_right.png')
    name = GetNameString(user)
    update = True

    scores = db.StudentViewScores(user.uname)
    i = 0
    while True:
        base.paste(temp_im, (0, 0))
        DisplayText(TruncateString(name, 20), (88, 34), fnt_20px)

        if i > 0:
            base.paste(left, (162, 746), mask=left)

        if i < (len(scores) - 1) / 17:
            base.paste(right, (289, 746), mask=right)
        
        j = 0
        while j < 17:
            k = i * 17 + j
            if k >= len(scores):
                break
            DisplayText(TruncateString(db.GetBookByBID(scores[k].bookid).title, 21), (30, 155 + (j * 30)), fnt_20px)
            DisplayText(TruncateString(scores[k].chapter, 10), (240, 155 + (j * 30)), fnt_20px)
            DisplayText("{0}/{1}".format(scores[k].score, scores[k].total), (370, 155 + (j * 30)), fnt_20px)
            j += 1


        while True:
            if update:
                UpdateDisplay()

            update = True
            inp = GetInput()
            if inp == 'w':
                update = False
                continue
            elif inp == 'a':
                if i > 0:
                    i -= 1
                    break
                update = False
            elif inp == 's':
                update = False
                continue        
            elif inp == 'd':
                if i < len(scores) / 17:
                    i += 1
                    break
                update = False
            elif inp == 'j':
                update = False
            elif inp == 'k':
                temp_im.close()
                left.close()
                right.close()
                return None


class QuestionItem:
    def __init__(self, question, answerid, choices):
        self.question = question
        self.answer = answerid
        self.choices = choices


def GetExam(ebook, chappath):
    soup = BeautifulSoup(ebook.read(chappath), 'lxml')
    soup = soup.find('quiz')
    
    if soup is None:
        return None

    items = soup.find_all('item')

    exam = []
    for i in items:
        q = i.question.string
        choices = i.find_all('choice')
        
        c = []
        for j in choices:
            c.append(j.string)

        exam.append(QuestionItem(q, int(i['answerid']) - 1, c))
    return exam


def GetNameString(user):
    if user.mname.strip():
        name = '{0}. {1}. {2}'.format(user.fname[0], user.mname[0], user.lname)
    else:
        name = '{0} {1}'.format(user.fname, user.lname)

    # TODO:
    # Shorten names that exceed boundaries from 

    return name


def TruncateString(string, maxlen):
    if len(string) > maxlen:
        string = string[0:maxlen - 3] + '...'
    return string



if __name__ == '__main__':
    Main()
    if args.pi:
        spi.close()

