
TARGET = 'site'

if TARGET == 'site':
    pagelist = ['index', 'concepts', 'lgl', 'pyleaf', 'examples', 'citing', 'download']
    pageNames = ['Leaf home',  'Concepts', 'LGL Howto', 'Pyleaf Howto', 'Examples', 'Citing Leaf', 'Downloads']
    folder = 'leafsite'
    template_file = 'template.raw'

else:
    pagelist = ['index', 'concepts', 'lgl', 'pyleaf', 'examples', 'citing']
    pageNames = ['Leaf home', 'Concepts', 'LGL Howto', 'Pyleaf Howto', 'Examples', 'Citing Leaf']
    folder = 'leafhelp'
    template_file = 'templateH.raw'




tag = '<!-- ADD CONTENT -->'

text = open(template_file).read()
n=text.find(tag)
before = text[0:n-1]
after = text[n + len(tag):len(text)]

def genPages(pagelist, pagenames, outdir):
    links = """<div class="right">
                  <h2>Navigation</h2><ul>"""

    for i,page in enumerate(pagelist):
        links = links + '<li><a href="'+ page + '.html">' + pageNames[i] + '</a></li>'

    links = links + '</ul>'+"""
                   <h2>Links</h2><br>
                   <a href="http://www.unisa.it">
                       <div align="left">
                       <img width="120px" class="images" src="img/logounisa.gif" padding="10px">
                       </div>
                   </a><br>
                   <a href="http://www.di.unisa.it">
                       <div align="left">
                       <img width="120px" class="images" src="img/logo_DI.jpg" padding="10px">
                       </div>
                   </a><br>
                   <a href="http://www.neuronelab.dmi.unisa.it">
                       <div align="left">
                       <img width="120px" class="images" src="img/neurone.png" padding="10px">
                       </div>
                   </a><br>
                   </div>
"""
    
    import os
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    for i,page in enumerate(pagelist):
        breadcrumbs = '<div class="breadcrumbs"><h1>' + pageNames[i] + '</h1></div>'

        content = open(page+'.raw').read()
        out = open(os.path.join(outdir,page)+'.html', 'w')
        out.write(before +
                  breadcrumbs +
                  '<div class="middle">'+
                  content +
                  '</div>' +
                  links +
                  after)
        out.close()

genPages(pagelist, pageNames, 'leafsite')
genPages(pagelist, pageNames, 'leafhelp')
