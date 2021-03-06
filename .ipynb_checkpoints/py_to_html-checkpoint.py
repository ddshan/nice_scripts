import csv
import errno
import inspect
import io
import math
import os
import random
import string
import urllib.request as urllib
import uuid

from PIL import Image


class Element:
    """ A data element of a row in a table """
    def __init__(self, htmlCode="", drawBorderColor=''):
        self.htmlCode = htmlCode
        self.isHeader = False
        self.drawBorderColor = drawBorderColor

    def textToHTML(self, text):
        res = '<p><b>'+text+'</b></p>'
        return res

    def imgToHTML(self, img_path, width = 200, overlay_path=None):
        res = '<img src="' + img_path.strip().lstrip() + '" width="' + str(width) + 'px" '
        if self.drawBorderColor:
            res += 'style="border: 10px solid ' + self.drawBorderColor + '" '
        if overlay_path:
          res += 'onmouseover="this.src=\'' + overlay_path.strip().lstrip() + '\';"'
          res += 'onmouseout="this.src=\'' + img_path.strip().lstrip() + '\';"'
        res += '/>'
        return res

    def imgsToSlideShow_v1(self, img_paths, **kwargs):
      uid = str(uuid.uuid4().fields[-1])[:5]
      res = '<div class="%s" style="position:relative; width:400px; height:400px">\n' % uid
      for img_path in img_paths:
        # res += '<img src="%s" style="position:absolute; left:0; top:0; width:400px">\n' % img_path
        kwargs['width'] = 400
        res += self.imgToHTML_base(img_path, **kwargs)
      res += '</div>'
      res += """
        <script>
        $(function(){
          $('.%s img:gt(0)').hide();
          setInterval(function(){
            $('.%s :first-child').fadeOut()
              .next().fadeIn()
              .end().appendTo('.%s');},
            200);
        });
        </script>\n""" % (uid, uid, uid)
      return res

    def imgsToSlideShow(self, img_paths, **kwargs):
      poses = kwargs['poses'] if 'poses' in kwargs else []
      # currently only supported kwarg is poses
      uid = 'x_' + str(uuid.uuid4().fields[-1])[:5]
      html = ''
      if 'width' not in kwargs:
        kwargs['width'] = 400
      if 'height' not in kwargs:
        kwargs['height'] = kwargs['width'] / 2
      html += '<canvas id="{2}" width="{0}px" height="{1}px"></canvas>\n'.format(
          kwargs['width'], kwargs['height'], uid)
      html += '<script>'
      html += """
          parts = [
            [2, 3],
            [2, 6],
            [3, 4],
            [4, 5],
            [6, 7],
            [7, 8],
            [2, 9],
            [9, 10],
            [10, 11],
            [2, 12],
            [12, 13],
            [13, 14],
            [2, 1],
            [1, 15],
            [15, 17],
            [1, 16],
            [16, 18],
            [3, 17],
          ];
          colors = [
            'rgb(255, 0, 0)',
            'rgb(255, 85, 0)',
            'rgb(255, 170, 0)',
            'rgb(255, 255, 0)',
            'rgb(170, 255, 0)',
            'rgb(85, 255, 0)',
            'rgb(0, 255, 0)',
            'rgb(0, 255, 85)',
            'rgb(0, 255, 170)',
            'rgb(0, 255, 255)',
            'rgb(0, 170, 255)',
            'rgb(0, 85, 255)',
            'rgb(0, 0, 255)',
            'rgb(85, 0, 255)',
            'rgb(170, 0, 255)',
            'rgb(255, 0, 255)',
            'rgb(255, 0, 170)',
            'rgb(255, 0, 85)',
          ];
          var {0}_current = 0;
          function drawPose(poses, ctx) {{
            ctx.lineWidth = "2";
            for (body_id=0; body_id < poses.length; body_id++) {{
              for (part_id=0; part_id < parts.length; part_id++) {{
                if (poses[body_id][parts[part_id][0]-1][2] < 0.1 ||
                    poses[body_id][parts[part_id][1]-1][2] < 0.1) {{
                  continue;
                }}
                ctx.beginPath();
                ctx.strokeStyle = colors[part_id];
                ctx.moveTo(poses[body_id][parts[part_id][0]-1][0],
                  poses[body_id][parts[part_id][0]-1][1]);
                ctx.lineTo(poses[body_id][parts[part_id][1]-1][0],
                  poses[body_id][parts[part_id][1]-1][1]);
                ctx.stroke();
              }}
            }}
          }}
          function {0}_animate(canvas, context, frames, poses) {{
            // context.clearRect(0, 0, canvas.width, canvas.height);
            var base_image = new Image();
            base_image.src = frames[{0}_current];
            base_image.onload = function() {{
              context.drawImage(base_image, 0, 0, canvas.width, canvas.width / 2);
              drawPose(poses[{0}_current], context);
            }};
            {0}_current = ++{0}_current % frames.length;
            setTimeout(function() {{
              {0}_animate(canvas, context, frames, poses);
            }}, 60);
          }}
      """.format(uid)
      html += """
        var {0}_canvas = document.getElementById('{0}');
        var {0}_context = {0}_canvas.getContext('2d');
        var {0}_frames = {1};
        var {0}_poses = {2};
        """.format(
          uid,
          '[' + ','.join(['"' + el + '"' for el in img_paths]) + ']',
          str(poses)
        )
      html += """
        {0}_animate({0}_canvas, {0}_context, {0}_frames, {0}_poses);
      """.format(uid)
      html += """</script>"""
      return html

    def vidToHTML(self, vid_path, width=320):
        vid_type='mp4'
        res = '''
            <video width="%d" controls>
                <source src="%s" type="video/%s">
                Your browser does not support the video tag.
            </video>''' % (width, vid_path, vid_type)
        return res

    def imgToBboxHTML(self, img_path, bboxes, col='green', wid=300, ht=300, imsize = None):
        idd = "img_" + ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

        # compute the ratios
        if imsize:
            actW = imsize[0]
            actH = imsize[1]
        else:
            actW, actH = self.tryComputeImgDim(img_path)
        actW = float(actW)

        actH = float(actH)
        if actW > actH:
            ht = wid * (actH / actW)
        else:
            wid = ht * (actW / actH)
        ratioX = wid / actW
        ratioY = ht / actH

        for i in range(len(bboxes)):
            bboxes[i] = [bboxes[i][0] * ratioX, bboxes[i][1] * ratioY, bboxes[i][2] * ratioX, bboxes[i][3] * ratioY]
        colStr = ''
        if self.drawBorderColor:
            col = self.drawBorderColor
            colStr = 'border: 10px solid ' + col + ';'
        htmlCode = """
            <canvas id=""" + idd + """ style="border:1px solid #d3d3d3; """ + colStr + """
                background-image: url(""" + img_path + """);
                background-repeat: no-repeat;
                background-size: contain;"
                width=""" + str(wid) + """,
                height=""" + str(ht) + """>
           </canvas>
           <script>
                var c = document.getElementById(\"""" + idd + """\");
                var ctx = c.getContext("2d");
                ctx.lineWidth="2";
                ctx.strokeStyle=\"""" + col + """\";"""
        for i in range(len(bboxes)):
            htmlCode += """ctx.rect(""" + ",".join([str(i) for i in bboxes[i]]) + """);"""
        htmlCode += """ctx.stroke();
        </script>
        """
        return htmlCode

    def imgToPosesHTML_SVG(self, img_path, poses, scale):
      ## TODO: THIS CODE IS BROKEN, maybe fix in the future (SVG is probably lighter than drawing with JS)
      connected = [[1, 2], [2, 3], # right leg
                   [11, 12], [12, 13], # right arm
                   [8, 13], # thorax - right arm
                   [3, 7], # right hip    - pelvis
                   [14, 15], [15, 16], # left arm
                   [8, 14], # thorax - left arm
                   [4, 5], [5, 6], # left leg
                   [4, 7], # left hip    - pelvis
                   [7, 8], # pelvis      - thorax
                   [8, 9], # thorax      - upper neck
                   [9, 10]] # upper neck - head
      colors = ['red', 'red', # ... % right leg
                'red', 'red', # ... % right arm
                'red', # ... % thorax - right arm
                'red', # ... % right hip - pelvis
                'green', 'green', # ... % left arm
                'green', # ... % thorax - left arm
                'green', 'green', # ... % left leg
                'green', # ... % left hip - pelvis
                'yellow', # ... % pelvis - thorax
                'yellow', # ... % thorax - upper neck
                'yellow'] # % upper neck head
      htmlCode = '<div style="position: relative;"><img src="' + img_path + '" style="width:' + str(int(scale * 100)) + '%" /><svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="position:absolute; left:0px; top:0px;"> <!-- <image xlink:href="' + img_path + '"  width="' + str(scale * 100) + '%" height="' + str(scale * 100) + '%" x=0 y=0 /> -->'
      for pose in poses:
        for cid, con in enumerate(connected):
          htmlCode += '<line x1="' + str(scale*pose[con[0]-1][0]) + '" y1="' + str(scale*pose[con[0]-1][1]) + '" x2="' + str(scale*pose[con[1]-1][0]) + '" y2="' + str(scale*pose[con[1]-1][1]) + '" stroke="' + colors[cid] + '" stroke-width="1" />'
      htmlCode += '</svg></div>'
      return htmlCode

    def imgToPosesHTML(self, img_path, poses, wid=300, ht=300, imsize = None, overlay_path = None):
      idd = "img_" + ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))

      # compute the ratios
      if imsize:
          actW = imsize[0]
          actH = imsize[1]
      else:
          actW, actH = self.tryComputeImgDim(img_path)
      actW = float(actW)
      actH = float(actH)
      if actW > actH:
          ht = wid * (actH / actW)
      else:
          wid = ht * (actW / actH)
      ratioX = wid / actW
      ratioY = ht / actH

      connected = [[1, 2], [2, 3], # right leg
                   [11, 12], [12, 13], # right arm
                   [8, 13], # thorax - right arm
                   [3, 7], # right hip    - pelvis
                   [14, 15], [15, 16], # left arm
                   [8, 14], # thorax - left arm
                   [4, 5], [5, 6], # left leg
                   [4, 7], # left hip    - pelvis
                   [7, 8], # pelvis      - thorax
                   [8, 9], # thorax      - upper neck
                   [9, 10]] # upper neck - head
      colors = ['red', 'red', # ... % right leg
                'red', 'red', # ... % right arm
                'red', # ... % thorax - right arm
                'red', # ... % right hip - pelvis
                'green', 'green', # ... % left arm
                'green', # ... % thorax - left arm
                'green', 'green', # ... % left leg
                'green', # ... % left hip - pelvis
                'yellow', # ... % pelvis - thorax
                'yellow', # ... % thorax - upper neck
                'yellow'] # % upper neck head

      htmlCode = '<canvas id=' + idd + ' style="border:1px solid #d33d3; background-image: url(' + img_path + '); background-repeat: no-repeat; background-size: contain;" width="' + str(wid) + 'px" height="' + str(ht) + 'px"'
      if overlay_path:
        htmlCode += ' onMouseOver="this.style.backgroundImage=\'url(' + overlay_path + ')\'" onMouseOut="this.style.backgroundImage =\'url(' + img_path + ')\'"'
      htmlCode += ' ></canvas>'
      htmlCode += """
           <script>
                var c = document.getElementById(\"""" + idd + """\");
                var ctx = c.getContext(\"2d\");
                ctx.lineWidth="2";"""
      for pose in poses:
        for cid,con in enumerate(connected):
          htmlCode += 'ctx.strokeStyle="' + colors[cid] + '"; ctx.beginPath(); ctx.moveTo(' + str(pose[con[0]-1][0]*ratioX) + ',' + str(pose[con[0]-1][1]*ratioY) + '); ctx.lineTo(' + str(pose[con[1]-1][0]*ratioX) + ',' + str(pose[con[1]-1][1]*ratioY) + '); ctx.stroke();'
      htmlCode += '</script>'
      return htmlCode

    def addImg(self, img_path, **kwargs):
      self.htmlCode += self.imgToHTML_base(img_path, **kwargs)

    def imgToHTML_base(self, img_path, width=1000, bboxes=None, imsize=None, overlay_path=None, poses=None, scale=None):
        # bboxes must be a list of [x,y,w,h] (i.e. a list of lists)
        # imsize is the natural size of image at img_path.. used for putting bboxes, not required otherwise
        # even if it's not provided, I'll try to figure it out -- using the typical use cases of this software
        # overlay_path is image I want to show on mouseover
        if bboxes:
            # TODO overlay path not implemented yet for canvas image
            return self.imgToBboxHTML(img_path, bboxes, 'green', width, width, imsize)
        elif poses:
            return self.imgToPosesHTML(img_path, poses, width, width, imsize, overlay_path)
        else:
            return self.imgToHTML(img_path, width, overlay_path)

    def addVideo(self, vid_path):
        self.htmlCode += self.vidToHTML(vid_path)

    def addSlideShow(self, img_paths, **kwargs):
        # img_paths is a list of URLs
        self.htmlCode += self.imgsToSlideShow(img_paths, **kwargs)

    def addTxt(self, txt):
        if self.htmlCode: # not empty
                self.htmlCode += '<br />'
        self.htmlCode += str(txt)

    def addLink(self, url):
        self.htmlCode = '<a href="%s">%s</a>' % (url, url)

    def getHTML(self):
        return self.htmlCode

    def setIsHeader(self):
        self.isHeader = True

    def setDrawCheck(self):
        self.drawBorderColor = 'green'

    def setDrawUnCheck(self):
        self.drawBorderColor = 'red'

    def setDrawBorderColor(self, color):
        self.drawBorderColor = color

    @staticmethod
    def getImSize(impath):
        im = Image.open(impath)
        return im.size

    @staticmethod
    def tryComputeImgDim(impath):
        try:
            im = Image.open(impath)
            res = im.size
            return res
        except:
            pass
        try:
            # most HACKY way to do this, remove the first '../'
            # since most cases
            impath2 = impath[3:]
            return self.getImSize(impath2)
        except:
            pass
        try:
            # read from internet
            fd = urllib.urlopen(impath)
            image_file = io.BytesIO(fd.read())
            im = Image.open(image_file)
            return im.size
        except:
            pass
        print( 'COULDNT READ THE IMAGE SIZE!')


class Table:
    def __init__(self, rows = []):
        self.rows = [row for row in rows if not row.isHeader]
        self.headerRows = [row for row in rows if row.isHeader]

    def addRow(self, row):
        if not row.isHeader:
            self.rows.append(row)
        else:
            self.headerRows.append(row)

    def getHTML(self, makeChart = False, transposeTableForChart = False, chartType = 'line', chartHeight = 650):
        html = '<table border=1 id="data" class="sortable">'
        for r in self.headerRows + self.rows:
            html += r.getHTML()
        html += '</table>'
        if makeChart:
            html += self.genChart(transposeTable=transposeTableForChart, chartType = chartType, chartHeight = chartHeight)
        return html

    def readFromCSV(self, fpath, scale=1.0):
        with open(fpath) as f:
            tablereader = csv.reader(filter(lambda row: row[0]!='#', f))
            for row in tablereader:
                tr = TableRow()
                for elt in row:
                    try:
                        tr.addElement(Element(str(float(elt) * scale)))
                    except:
                        tr.addElement(Element(elt))
                self.addRow(tr)

    def countRows(self):
        return len(self.rows)

    def genChart(self, transposeTable=False, chartType = 'line', chartHeight = 650):
        # Generate HighCharts.com chart using the table
        # data. Assumes that data is numeric, and first row
        # and the first column are headers
        for row in self.rows:
            row.elements[0].setIsHeader()
        scrdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        f = open(os.path.join(scrdir, '../templates/highchart_js.html'))
        base_js = f.read()
        f.close()
        base_js =  string.Template(base_js).safe_substitute({'transpose': 'true'} if transposeTable else {'transpose': 'false'})
        base_js =  string.Template(base_js).safe_substitute({'chartType': "'" + chartType + "'"})
        base_js =  string.Template(base_js).safe_substitute({'chartHeight': str(chartHeight)})
        return base_js

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class TableRow:
    def __init__(self, isHeader=False, rno=-1, elementsPerRow=9999999999):
        self.isHeader = isHeader
        self.elements = []
        self.rno = rno
        self.elementsPerRow = elementsPerRow

    def addElement(self, element):
        self.elements.append(element)

    def getHTML(self):
        html = ''
        for elements in chunks(self.elements, self.elementsPerRow):
            html += '<tr>'
            if self.rno >= 0:
                html += '<td><a href="#' + \
                        str(self.rno) + '">' + str(self.rno) + '</a>'
                html += '<a name=' + str(self.rno) + '></a></td>'
            for e in elements:
                if self.isHeader or e.isHeader:
                    elTag = 'th'
                else:
                    elTag = 'td'
                html += '<%s>' % elTag + e.getHTML() + '</%s>' % elTag
            html += '</tr>\n'
        return html


class TableWriter:
    def __init__(self, table, outputdir, rowsPerPage=20, pgListBreak=20, makeChart = False, meta=False, topName='default', headDesc='', desc='', transposeTableForChart=False, chartType='line', chartHeight=650):
        self.outputdir = outputdir
        self.rowsPerPage = rowsPerPage
        self.table = table
        self.pgListBreak = pgListBreak
        self.makeChart = makeChart
        self.meta = meta 
        self.topName = topName
        self.desc = desc
        self.headDesc = headDesc
        self.transposeTableForChart = transposeTableForChart  # used in genCharts
        self.chartType = chartType # used in genCharts
        self.chartHeight = chartHeight

    def write(self, writePgLinks=True):
        # returns a list with each element as (link to table
        # row, row)
        ret_data = []
        self.mkdir_p(self.outputdir)
        nRows = self.table.countRows()
        pgCounter = 1
        for i in range(0, nRows, self.rowsPerPage):
            rowsSubset = self.table.rows[i : i + self.rowsPerPage]
            t = Table(self.table.headerRows + rowsSubset)
            ret_data.append((pgCounter, rowsSubset))
            if self.meta:
                f = open(os.path.join(self.outputdir, 'index.html'), 'w')
            else:
                f = open(os.path.join(self.outputdir, str(self.topName) + str(pgCounter) + '.html'), 'w')
            f.write('<head>')
            f.write('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css">\n')
            f.write(self.headDesc)
            f.write('<script src="http://www.kryogenix.org/code/browser/sorttable/sorttable.js"></script>\n')
            f.write('<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>\n')
            f.write('</head>')
            f.write('<div class="parent">')
            f.write(self.desc)
            pgLinks = self.getPageLinks(int(math.ceil(nRows * 1.0 / self.rowsPerPage)),
                    pgCounter, self.pgListBreak, self.topName)
            if writePgLinks:
                f.write(pgLinks)
            f.write(t.getHTML(makeChart = self.makeChart, transposeTableForChart=self.transposeTableForChart, chartType = self.chartType, chartHeight = self.chartHeight))
            if writePgLinks:
                f.write(pgLinks)
            f.write('</div>')
            f.write(self.getCredits())
            f.close()
            pgCounter += 1

        return ret_data

    @staticmethod
    def mkdir_p(path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

    @staticmethod
    def getPageLinks(nPages, curPage, pgListBreak, topName):
        if nPages < 2:
            return ''
        links = ''
        for i in range(1, nPages + 1):
            if not i == curPage:
                links += '<a href="' + str(topName) + str(i) + '.html">' + str(topName) + str(i) + '</a>&nbsp'
            else:
                links += str(i) + '&nbsp'
            if (i % pgListBreak == 0):
                links += '<br />'
        return '\n' + links + '\n'

    @staticmethod
    def getCredits():
        return '\n<br/><div align="center"><small>Generated using <a href="https://github.com/rohitgirdhar/PyHTMLWriter">PyHTMLWriter</a></small></div>'


if __name__ == "__main__":
    columns = ['index', 'image', 'name', 'date', 'epoch', 'loss', 'other']

    t = Table()
    r = TableRow(isHeader=True)

    # create html headers
    for name in columns:
        r.addElement(Element(name))
    t.addRow(r)

    real_data_here = [['test1', 'test2.png', 'test3', 'test4', 'test5'],
                 ['test1', 'test2.png', 'test3', 'test4', 'test5'],
                 ['test1', 'test2.png', 'test3', 'test4', 'test5'],
                 ['test1', 'test2.png', 'test3', 'test4', 'test5'],
                 ['test1', 'test2.png', 'test3', 'test4', 'test5'],
                 ['test1', 'test2.png', 'test3', 'test4', 'test5']]

    # add real_data
    for index, row in enumerate(real_data_here):
        r = TableRow()
        r.addElement(Element("#"+str(index)))
        for item in row:  
            if '.png' in item:
                ele = Element()
                ele.addImg('/~relh/images/'+item)
                r.addElement(ele)
            else:
                r.addElement(Element(item))
        t.addRow(r)

    # read any extra non table content from disk
    with open('web/index.html', 'r') as handle:
        custom_html = handle.read()
    with open('web/style.css', 'r') as handle:
        custom_css = handle.read()

    file_name = 'h2a_0hr'

    tw = TableWriter(t, '/home/relh/public_html/test/', topName=file_name, desc=custom_html, headDesc=custom_css)
    tw.write()
