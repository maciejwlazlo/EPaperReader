
import formatter, htmllib, os, StringIO, zipfile
from bs4 import BeautifulSoup



def CheckEpub(fl):
    '''
    Check if fl is a file and ends in ".epub" 
    '''
    if os.path.isfile(fl) and os.path.splitext(fl)[1].lower() == '.epub':
        return True


def OpenEpub(fl):
    if not CheckEpub(fl):
        print 'File ' + fl + ' was not found'
        return None

    return zipfile.ZipFile(fl, 'r')


def GetTableOfContents(fl):
    basedir = ''

    # find opf file
    soup = BeautifulSoup(fl.read('META-INF/container.xml'), 'lxml')
    opf = dict(soup.find('rootfile').attrs)['full-path']

    basedir = os.path.dirname(opf)
    if basedir:
        basedir = '{0}/'.format(basedir)

    soup =  BeautifulSoup(fl.read(opf), 'lxml')

    # all files, not in order
    x, ncx = {}, None
    for item in soup.find('manifest').findAll('item'):
        d = dict(item.attrs)
        x[d['id']] = '{0}{1}'.format(basedir, d['href'])
        if d['media-type'] == 'application/x-dtbncx+xml':
            ncx = '{0}{1}'.format(basedir, d['href'])

    # reading order, not all files
    y = []
    for item in soup.find('spine').findAll('itemref'):
        y.append(x[dict(item.attrs)['idref']])

    z = {}
    if ncx:
        # get titles from the toc
        soup =  BeautifulSoup(fl.read(ncx), 'lxml')

        for navpoint in soup('navpoint'):
            k = '{0}{1}'.format(basedir, navpoint.content.get('src', None))
            # strip off any anchor text
            k = k.split('#')[0]
            if k:
                z[k] = navpoint.navlabel.text.strip()

    # # output
    # for section in y:
    #     if section in z:
    #         yield (z[section].encode('utf-8'), section.encode('utf-8'))
    #     else:
    #         yield (u'', section.encode('utf-8').strip())
    toc = []
    for section in y:
        if section in z:
            toc.append([z[section].encode('utf-8'), section.encode('utf-8')])
        else:
            toc.append([u'', section.encode('utf-8').strip()])
    return toc



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("book", help="Load the book.");
    args = parser.parse_args()
    dump_epub(args.book)