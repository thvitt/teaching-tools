from argparse import ArgumentParser
from typing import List

from lxml import etree

import sys
from os import fspath
import codecs
from textwrap import dedent
import importlib.resources as resources
import json
import unicodedata
from .diffencoding import get_chars
import csv
from pathlib import Path

options = None

SVG_TEMPLATE = """
<svg xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
     xmlns:svg="http://www.w3.org/2000/svg" xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     inkscape:version="0.92.4 (5da689c313, 2019-01-14)" id="svg8" version="1.1"
     viewBox="0 0 640 480" height="12.7cm" width="16.9cm">

  <style id="style2455" type="text/css">
.cell {
    fill:none;
    stroke:#E0E0E0;
    stroke-width:0.26458332;
}
.no_char, .no_char * {
    display: none
}

.glyph {
    font-size:4.93889px;
    font-family:FreeSerif;
    text-align:center;
    text-anchor:middle;
}
.codepoint {
    font-size:2.11667px;
    font-family:Ubuntu;
    text-align:center;
    text-anchor:middle;
    fill:#808080;
}
.glyph .shortcut {
    font-size:2pt; 
    font-family:"Pragmata Pro";
}
  </style>

  <metadata id="metadata5">
    <rdf:RDF>
      <cc:Work rdf:about="">
        <dc:format>image/svg+xml</dc:format>
        <dc:type rdf:resource="http://purl.org/dc/dcmitype/StillImage"/>
        <dc:title/>
        <cc:license rdf:resource="http://creativecommons.org/licenses/by-sa/4.0/"/>
      </cc:Work>
      <cc:License rdf:about="http://creativecommons.org/licenses/by-sa/4.0/">
        <cc:permits rdf:resource="http://creativecommons.org/ns#Reproduction"/>
        <cc:permits rdf:resource="http://creativecommons.org/ns#Distribution"/>
        <cc:requires rdf:resource="http://creativecommons.org/ns#Notice"/>
        <cc:requires rdf:resource="http://creativecommons.org/ns#Attribution"/>
        <cc:permits rdf:resource="http://creativecommons.org/ns#DerivativeWorks"/>
        <cc:requires rdf:resource="http://creativecommons.org/ns#ShareAlike"/>
      </cc:License>
    </rdf:RDF>
  </metadata>
  <g transform="matrix(1.06667,0,0,1.06667,0.14124444,44.303093)" id="table" inkscape:groupmode="layer" inkscape:label="ASCII">
    <g transform="matrix(5.3025165,0,0,5.298385,-320.72037,-693.98015)" id="cellgroup0">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect0" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph0" class="glyph"><tspan id="glyph0ts" x="64.110626" y="128.55876">&#9216;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint0" class="codepoint"><tspan id="codepoint0ts" x="64.17141" y="132.90939">0</tspan></text>
    </g>
    <g id="cellgroup1" transform="matrix(5.3025165,0,0,5.298385,-283.30817,-693.98005)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect1" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph1" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph1ts">&#9217;</tspan></text>
      <text id="codepoint1" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint1ts">1</tspan></text>
    </g>
    <g id="cellgroup2" transform="matrix(5.3025165,0,0,5.298385,-245.89598,-693.98015)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect2" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph2" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph2ts">&#9218;</tspan></text>
      <text id="codepoint2" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint2ts">2</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-208.48378,-693.98012)" id="cellgroup3">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect3" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph3" class="glyph"><tspan id="glyph3ts" x="64.110626" y="128.55876">&#9219;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint3" class="codepoint"><tspan id="codepoint3ts" x="64.17141" y="132.90939">3</tspan></text>
    </g>
    <g id="cellgroup4" transform="matrix(5.3025165,0,0,5.298385,-171.07157,-693.98005)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect4" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph4" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph4ts">&#9220;</tspan></text>
      <text id="codepoint4" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint4ts">4</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-133.65935,-693.98001)" id="cellgroup5">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect5" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph5" class="glyph"><tspan id="glyph5ts" x="64.110626" y="128.55876">&#9221;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint5" class="codepoint"><tspan id="codepoint5ts" x="64.17141" y="132.90939">5</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-96.247143,-693.98012)" id="cellgroup6">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect6" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph6" class="glyph"><tspan id="glyph6ts" x="64.110626" y="128.55876">&#9222;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint6" class="codepoint"><tspan id="codepoint6ts" x="64.17141" y="132.90939">6</tspan></text>
    </g>
    <g id="cellgroup7" transform="matrix(5.3025165,0,0,5.298385,-58.834953,-693.98005)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect7" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph7" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph7ts">&#9223;</tspan></text>
      <text id="codepoint7" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint7ts">7</tspan></text>
    </g>
    <g id="cellgroup8" transform="matrix(5.3025165,0,0,5.298385,-21.422777,-693.98022)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect8" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph8" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph8ts">&#9224;</tspan></text>
      <text id="codepoint8" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint8ts">8</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,15.98941,-693.98015)" id="cellgroup9">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect9" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph9" class="glyph"><tspan id="glyph9ts" x="64.110626" y="128.55876">&#9225;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint9" class="codepoint"><tspan id="codepoint9ts" x="64.17141" y="132.90939">9</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,53.401615,-693.98022)" id="cellgroup10">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect10" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph10" class="glyph"><tspan id="glyph10ts" x="64.110626" y="128.55876">&#9226;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint10" class="codepoint"><tspan id="codepoint10ts" x="64.17141" y="132.90939">10</tspan></text>
    </g>
    <g id="cellgroup11" transform="matrix(5.3025165,0,0,5.298385,90.813806,-693.98015)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect11" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph11" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph11ts">&#9227;</tspan></text>
      <text id="codepoint11" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint11ts">11</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,128.22602,-693.98015)" id="cellgroup12">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect12" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph12" class="glyph"><tspan id="glyph12ts" x="64.110626" y="128.55876">&#9228;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint12" class="codepoint"><tspan id="codepoint12ts" x="64.17141" y="132.90939">12</tspan></text>
    </g>
    <g id="cellgroup13" transform="matrix(5.3025165,0,0,5.298385,165.63822,-693.98005)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect13" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph13" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph13ts">&#9229;</tspan></text>
      <text id="codepoint13" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint13ts">13</tspan></text>
    </g>
    <g id="cellgroup14" transform="matrix(5.3025165,0,0,5.298385,203.05043,-693.98015)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect14" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph14" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph14ts">&#9230;</tspan></text>
      <text id="codepoint14" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint14ts">14</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,240.4626,-693.98012)" id="cellgroup15">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect15" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph15" class="glyph"><tspan id="glyph15ts" x="64.110626" y="128.55876">&#9231;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint15" class="codepoint"><tspan id="codepoint15ts" x="64.17141" y="132.90939">15</tspan></text>
    </g>
    <g id="cellgroup16" transform="matrix(5.3025165,0,0,5.298385,-320.72037,-637.90556)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect16" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph16" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph16ts">&#9232;</tspan></text>
      <text id="codepoint16" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint16ts">16</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-283.30817,-637.90549)" id="cellgroup17">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect17" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph17" class="glyph"><tspan id="glyph17ts" x="64.110626" y="128.55876">&#9233;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint17" class="codepoint"><tspan id="codepoint17ts" x="64.17141" y="132.90939">17</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-245.89596,-637.90563)" id="cellgroup18">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect18" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph18" class="glyph"><tspan id="glyph18ts" x="64.110626" y="128.55876">&#9234;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint18" class="codepoint"><tspan id="codepoint18ts" x="64.17141" y="132.90939">18</tspan></text>
    </g>
    <g id="cellgroup19" transform="matrix(5.3025165,0,0,5.298385,-208.48377,-637.90556)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect19" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph19" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph19ts">&#9235;</tspan></text>
      <text id="codepoint19" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint19ts">19</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-171.07156,-637.90549)" id="cellgroup20">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect20" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph20" class="glyph"><tspan id="glyph20ts" x="64.110626" y="128.55876">&#9236;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint20" class="codepoint"><tspan id="codepoint20ts" x="64.17141" y="132.90939">20</tspan></text>
    </g>
    <g id="cellgroup21" transform="matrix(5.3025165,0,0,5.298385,-133.65934,-637.90545)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect21" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph21" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph21ts">&#9237;</tspan></text>
      <text id="codepoint21" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint21ts">21</tspan></text>
    </g>
    <g id="cellgroup22" transform="matrix(5.3025165,0,0,5.298385,-96.247133,-637.90556)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect22" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph22" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph22ts">&#9238;</tspan></text>
      <text id="codepoint22" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint22ts">22</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-58.834942,-637.90545)" id="cellgroup23">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect23" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph23" class="glyph"><tspan id="glyph23ts" x="64.110626" y="128.55876">&#9239;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint23" class="codepoint"><tspan id="codepoint23ts" x="64.17141" y="132.90939">23</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-21.422766,-637.90567)" id="cellgroup24">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect24" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph24" class="glyph"><tspan id="glyph24ts" x="64.110626" y="128.55876">&#9240;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint24" class="codepoint"><tspan id="codepoint24ts" x="64.17141" y="132.90939">24</tspan></text>
    </g>
    <g id="cellgroup25" transform="matrix(5.3025165,0,0,5.298385,15.98942,-637.90556)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect25" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph25" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph25ts">&#9241;</tspan></text>
      <text id="codepoint25" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint25ts">25</tspan></text>
    </g>
    <g id="cellgroup26" transform="matrix(5.3025165,0,0,5.298385,53.401625,-637.90567)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect26" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph26" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph26ts">&#9242;</tspan></text>
      <text id="codepoint26" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint26ts">26</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,90.81382,-637.90563)" id="cellgroup27">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect27" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph27" class="glyph"><tspan id="glyph27ts" x="64.110626" y="128.55876">&#9243;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint27" class="codepoint"><tspan id="codepoint27ts" x="64.17141" y="132.90939">27</tspan></text>
    </g>
    <g id="cellgroup28" transform="matrix(5.3025165,0,0,5.298385,128.22603,-637.90556)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect28" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph28" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph28ts">&#9244;</tspan></text>
      <text id="codepoint28" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint28ts">28</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,165.63823,-637.90549)" id="cellgroup29">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect29" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph29" class="glyph"><tspan id="glyph29ts" x="64.110626" y="128.55876">&#9245;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint29" class="codepoint"><tspan id="codepoint29ts" x="64.17141" y="132.90939">29</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,203.05043,-637.90563)" id="cellgroup30">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect30" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph30" class="glyph"><tspan id="glyph30ts" x="64.110626" y="128.55876">&#9246;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint30" class="codepoint"><tspan id="codepoint30ts" x="64.17141" y="132.90939">30</tspan></text>
    </g>
    <g id="cellgroup31" transform="matrix(5.3025165,0,0,5.298385,240.4626,-637.90556)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect31" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph31" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph31ts">&#9247;</tspan></text>
      <text id="codepoint31" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint31ts">31</tspan></text>
    </g>
    <g id="cellgroup32" transform="matrix(5.3025165,0,0,5.298385,-320.72037,-581.83084)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect32" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph32" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.785866" id="glyph32ts"> </tspan></text>
      <text id="codepoint32" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint32ts">32</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-283.30817,-581.83077)" id="cellgroup33">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect33" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph33" class="glyph"><tspan id="glyph33ts" x="64.110626" y="128.55876">!</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint33" class="codepoint"><tspan id="codepoint33ts" x="64.17141" y="132.90939">33</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-245.89598,-581.83084)" id="cellgroup34">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect34" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph34" class="glyph"><tspan id="glyph34ts" x="64.110626" y="128.55876">"</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint34" class="codepoint"><tspan id="codepoint34ts" x="64.17141" y="132.90939">34</tspan></text>
    </g>
    <g id="cellgroup35" transform="matrix(5.3025165,0,0,5.298385,-208.48378,-581.83081)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect35" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph35" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph35ts">#</tspan></text>
      <text id="codepoint35" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint35ts">35</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-171.07157,-581.83077)" id="cellgroup36">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect36" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph36" class="glyph"><tspan id="glyph36ts" x="64.110626" y="128.55876">$</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint36" class="codepoint"><tspan id="codepoint36ts" x="64.17141" y="132.90939">36</tspan></text>
    </g>
    <g id="cellgroup37" transform="matrix(5.3025165,0,0,5.298385,-133.65935,-581.8307)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect37" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph37" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph37ts">%</tspan></text>
      <text id="codepoint37" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint37ts">37</tspan></text>
    </g>
    <g id="cellgroup38" transform="matrix(5.3025165,0,0,5.298385,-96.247143,-581.83081)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect38" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph38" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph38ts">&amp;</tspan></text>
      <text id="codepoint38" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint38ts">38</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-58.834953,-581.83077)" id="cellgroup39">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect39" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph39" class="glyph"><tspan id="glyph39ts" x="64.110626" y="128.55876">'</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint39" class="codepoint"><tspan id="codepoint39ts" x="64.17141" y="132.90939">39</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-21.422774,-581.83091)" id="cellgroup40">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect40" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph40" class="glyph"><tspan id="glyph40ts" x="64.110626" y="128.55876">(</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint40" class="codepoint"><tspan id="codepoint40ts" x="64.17141" y="132.90939">40</tspan></text>
    </g>
    <g id="cellgroup41" transform="matrix(5.3025165,0,0,5.298385,15.989412,-581.83084)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect41" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph41" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph41ts">)</tspan></text>
      <text id="codepoint41" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint41ts">41</tspan></text>
    </g>
    <g id="cellgroup42" transform="matrix(5.3025165,0,0,5.298385,53.401618,-581.83091)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect42" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph42" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph42ts">*</tspan></text>
      <text id="codepoint42" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint42ts">42</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,90.813806,-581.83084)" id="cellgroup43">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect43" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph43" class="glyph"><tspan id="glyph43ts" x="64.110626" y="128.55876">+</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint43" class="codepoint"><tspan id="codepoint43ts" x="64.17141" y="132.90939">43</tspan></text>
    </g>
    <g id="cellgroup44" transform="matrix(5.3025165,0,0,5.298385,128.22602,-581.83084)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect44" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph44" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph44ts">,</tspan></text>
      <text id="codepoint44" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint44ts">44</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,165.63822,-581.83077)" id="cellgroup45">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect45" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph45" class="glyph"><tspan id="glyph45ts" x="64.110626" y="128.55876">-</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint45" class="codepoint"><tspan id="codepoint45ts" x="64.17141" y="132.90939">45</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,203.05043,-581.83084)" id="cellgroup46">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect46" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph46" class="glyph"><tspan id="glyph46ts" x="64.110626" y="128.55876">.</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint46" class="codepoint"><tspan id="codepoint46ts" x="64.17141" y="132.90939">46</tspan></text>
    </g>
    <g id="cellgroup47" transform="matrix(5.3025165,0,0,5.298385,240.4626,-581.83081)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect47" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph47" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph47ts">/</tspan></text>
      <text id="codepoint47" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint47ts">47</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-320.72037,-525.75619)" id="cellgroup48">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect48" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph48" class="glyph"><tspan id="glyph48ts" x="64.110626" y="128.55876">0</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint48" class="codepoint"><tspan id="codepoint48ts" x="64.17141" y="132.90939">48</tspan></text>
    </g>
    <g id="cellgroup49" transform="matrix(5.3025165,0,0,5.298385,-283.30817,-525.75616)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect49" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph49" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph49ts">1</tspan></text>
      <text id="codepoint49" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint49ts">49</tspan></text>
    </g>
    <g id="cellgroup50" transform="matrix(5.3025165,0,0,5.298385,-245.89596,-525.75626)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect50" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph50" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph50ts">2</tspan></text>
      <text id="codepoint50" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint50ts">50</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-208.48377,-525.75619)" id="cellgroup51">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect51" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph51" class="glyph"><tspan id="glyph51ts" x="64.110626" y="128.55876">3</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint51" class="codepoint"><tspan id="codepoint51ts" x="64.17141" y="132.90939">51</tspan></text>
    </g>
    <g id="cellgroup52" transform="matrix(5.3025165,0,0,5.298385,-171.07156,-525.75616)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect52" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph52" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph52ts">4</tspan></text>
      <text id="codepoint52" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint52ts">52</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-133.65934,-525.75612)" id="cellgroup53">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect53" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph53" class="glyph"><tspan id="glyph53ts" x="64.110626" y="128.55876">5</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint53" class="codepoint"><tspan id="codepoint53ts" x="64.17141" y="132.90939">53</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-96.247133,-525.75619)" id="cellgroup54">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect54" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph54" class="glyph"><tspan id="glyph54ts" x="64.110626" y="128.55876">6</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint54" class="codepoint"><tspan id="codepoint54ts" x="64.17141" y="132.90939">54</tspan></text>
    </g>
    <g id="cellgroup55" transform="matrix(5.3025165,0,0,5.298385,-58.834942,-525.75612)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect55" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph55" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph55ts">7</tspan></text>
      <text id="codepoint55" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint55ts">55</tspan></text>
    </g>
    <g id="cellgroup56" transform="matrix(5.3025165,0,0,5.298385,-21.422764,-525.7563)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect56" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph56" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph56ts">8</tspan></text>
      <text id="codepoint56" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint56ts">56</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,15.989423,-525.75619)" id="cellgroup57">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect57" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph57" class="glyph"><tspan id="glyph57ts" x="64.110626" y="128.55876">9</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint57" class="codepoint"><tspan id="codepoint57ts" x="64.17141" y="132.90939">57</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,53.401629,-525.7563)" id="cellgroup58">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect58" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph58" class="glyph"><tspan id="glyph58ts" x="64.110626" y="128.55876">:</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint58" class="codepoint"><tspan id="codepoint58ts" x="64.17141" y="132.90939">58</tspan></text>
    </g>
    <g id="cellgroup59" transform="matrix(5.3025165,0,0,5.298385,90.81382,-525.75626)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect59" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph59" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph59ts">;</tspan></text>
      <text id="codepoint59" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint59ts">59</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,128.22603,-525.75619)" id="cellgroup60">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect60" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph60" class="glyph"><tspan id="glyph60ts" x="64.110626" y="128.55876">&lt;</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint60" class="codepoint"><tspan id="codepoint60ts" x="64.17141" y="132.90939">60</tspan></text>
    </g>
    <g id="cellgroup61" transform="matrix(5.3025165,0,0,5.298385,165.63823,-525.75616)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect61" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph61" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph61ts">=</tspan></text>
      <text id="codepoint61" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint61ts">61</tspan></text>
    </g>
    <g id="cellgroup62" transform="matrix(5.3025165,0,0,5.298385,203.05043,-525.75626)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect62" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph62" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph62ts">&gt;</tspan></text>
      <text id="codepoint62" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint62ts">62</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,240.4626,-525.75619)" id="cellgroup63">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect63" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph63" class="glyph"><tspan id="glyph63ts" x="64.110626" y="128.55876">?</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint63" class="codepoint"><tspan id="codepoint63ts" x="64.17141" y="132.90939">63</tspan></text>
    </g>
    <g id="cellgroup64" transform="matrix(5.3025165,0,0,5.298385,-320.72037,-469.6821)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect64" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph64" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph64ts">@</tspan></text>
      <text id="codepoint64" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint64ts">64</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-283.30817,-469.68199)" id="cellgroup65">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect65" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph65" class="glyph"><tspan id="glyph65ts" x="64.110626" y="128.55876">A</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint65" class="codepoint"><tspan id="codepoint65ts" x="64.17141" y="132.90939">65</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-245.89598,-469.6821)" id="cellgroup66">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect66" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph66" class="glyph"><tspan id="glyph66ts" x="64.110626" y="128.55876">B</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint66" class="codepoint"><tspan id="codepoint66ts" x="64.17141" y="132.90939">66</tspan></text>
    </g>
    <g id="cellgroup67" transform="matrix(5.3025165,0,0,5.298385,-208.48378,-469.68206)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect67" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph67" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph67ts">C</tspan></text>
      <text id="codepoint67" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint67ts">67</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-171.07157,-469.68199)" id="cellgroup68">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect68" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph68" class="glyph"><tspan id="glyph68ts" x="64.110626" y="128.55876">D</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint68" class="codepoint"><tspan id="codepoint68ts" x="64.17141" y="132.90939">68</tspan></text>
    </g>
    <g id="cellgroup69" transform="matrix(5.3025165,0,0,5.298385,-133.65936,-469.68196)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect69" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph69" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph69ts">E</tspan></text>
      <text id="codepoint69" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint69ts">69</tspan></text>
    </g>
    <g id="cellgroup70" transform="matrix(5.3025165,0,0,5.298385,-96.24715,-469.68206)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect70" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph70" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph70ts">F</tspan></text>
      <text id="codepoint70" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint70ts">70</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-58.83496,-469.68199)" id="cellgroup71">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect71" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph71" class="glyph"><tspan id="glyph71ts" x="64.110626" y="128.55876">G</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint71" class="codepoint"><tspan id="codepoint71ts" x="64.17141" y="132.90939">71</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-21.422782,-469.68217)" id="cellgroup72">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect72" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph72" class="glyph"><tspan id="glyph72ts" x="64.110626" y="128.55876">H</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint72" class="codepoint"><tspan id="codepoint72ts" x="64.17141" y="132.90939">72</tspan></text>
    </g>
    <g id="cellgroup73" transform="matrix(5.3025165,0,0,5.298385,15.989404,-469.6821)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect73" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph73" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph73ts">I</tspan></text>
      <text id="codepoint73" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint73ts">73</tspan></text>
    </g>
    <g id="cellgroup74" transform="matrix(5.3025165,0,0,5.298385,53.401611,-469.68217)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect74" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph74" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph74ts">J</tspan></text>
      <text id="codepoint74" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint74ts">74</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,90.813803,-469.6821)" id="cellgroup75">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect75" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph75" class="glyph"><tspan id="glyph75ts" x="64.110626" y="128.55876">K</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint75" class="codepoint"><tspan id="codepoint75ts" x="64.17141" y="132.90939">75</tspan></text>
    </g>
    <g id="cellgroup76" transform="matrix(5.3025165,0,0,5.298385,128.22601,-469.6821)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect76" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph76" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph76ts">L</tspan></text>
      <text id="codepoint76" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint76ts">76</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,165.63822,-469.68199)" id="cellgroup77">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect77" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph77" class="glyph"><tspan id="glyph77ts" x="64.110626" y="128.55876">M</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint77" class="codepoint"><tspan id="codepoint77ts" x="64.17141" y="132.90939">77</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,203.05043,-469.6821)" id="cellgroup78">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect78" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph78" class="glyph"><tspan id="glyph78ts" x="64.110626" y="128.55876">N</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint78" class="codepoint"><tspan id="codepoint78ts" x="64.17141" y="132.90939">78</tspan></text>
    </g>
    <g id="cellgroup79" transform="matrix(5.3025165,0,0,5.298385,240.4626,-469.68206)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect79" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph79" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph79ts">O</tspan></text>
      <text id="codepoint79" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint79ts">79</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-320.72037,-413.60749)" id="cellgroup80">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect80" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph80" class="glyph"><tspan id="glyph80ts" x="64.110626" y="128.55876">P</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint80" class="codepoint"><tspan id="codepoint80ts" x="64.17141" y="132.90939">80</tspan></text>
    </g>
    <g id="cellgroup81" transform="matrix(5.3025165,0,0,5.298385,-283.30817,-413.60745)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect81" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph81" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph81ts">Q</tspan></text>
      <text id="codepoint81" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint81ts">81</tspan></text>
    </g>
    <g id="cellgroup82" transform="matrix(5.3025165,0,0,5.298385,-245.89598,-413.60756)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect82" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph82" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph82ts">R</tspan></text>
      <text id="codepoint82" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint82ts">82</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-208.48377,-413.60749)" id="cellgroup83">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect83" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph83" class="glyph"><tspan id="glyph83ts" x="64.110626" y="128.55876">S</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint83" class="codepoint"><tspan id="codepoint83ts" x="64.17141" y="132.90939">83</tspan></text>
    </g>
    <g id="cellgroup84" transform="matrix(5.3025165,0,0,5.298385,-171.07156,-413.60745)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect84" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph84" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph84ts">T</tspan></text>
      <text id="codepoint84" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint84ts">84</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-133.65935,-413.60738)" id="cellgroup85">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect85" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph85" class="glyph"><tspan id="glyph85ts" x="64.110626" y="128.55876">U</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint85" class="codepoint"><tspan id="codepoint85ts" x="64.17141" y="132.90939">85</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-96.247136,-413.60749)" id="cellgroup86">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect86" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph86" class="glyph"><tspan id="glyph86ts" x="64.110626" y="128.55876">V</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint86" class="codepoint"><tspan id="codepoint86ts" x="64.17141" y="132.90939">86</tspan></text>
    </g>
    <g id="cellgroup87" transform="matrix(5.3025165,0,0,5.298385,-58.834949,-413.60738)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect87" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph87" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph87ts">W</tspan></text>
      <text id="codepoint87" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint87ts">87</tspan></text>
    </g>
    <g id="cellgroup88" transform="matrix(5.3025165,0,0,5.298385,-21.422772,-413.60759)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect88" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph88" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph88ts">X</tspan></text>
      <text id="codepoint88" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint88ts">88</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,15.989415,-413.60749)" id="cellgroup89">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect89" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph89" class="glyph"><tspan id="glyph89ts" x="64.110626" y="128.55876">Y</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint89" class="codepoint"><tspan id="codepoint89ts" x="64.17141" y="132.90939">89</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,53.401622,-413.60759)" id="cellgroup90">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect90" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph90" class="glyph"><tspan id="glyph90ts" x="64.110626" y="128.55876">Z</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint90" class="codepoint"><tspan id="codepoint90ts" x="64.17141" y="132.90939">90</tspan></text>
    </g>
    <g id="cellgroup91" transform="matrix(5.3025165,0,0,5.298385,90.813813,-413.60756)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect91" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph91" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph91ts">[</tspan></text>
      <text id="codepoint91" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint91ts">91</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,128.22602,-413.60749)" id="cellgroup92">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect92" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph92" class="glyph"><tspan id="glyph92ts" x="64.110626" y="128.55876">\</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint92" class="codepoint"><tspan id="codepoint92ts" x="64.17141" y="132.90939">92</tspan></text>
    </g>
    <g id="cellgroup93" transform="matrix(5.3025165,0,0,5.298385,165.63823,-413.60745)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect93" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph93" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph93ts">]</tspan></text>
      <text id="codepoint93" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint93ts">93</tspan></text>
    </g>
    <g id="cellgroup94" transform="matrix(5.3025165,0,0,5.298385,203.05043,-413.60756)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect94" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph94" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph94ts">^</tspan></text>
      <text id="codepoint94" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint94ts">94</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,240.4626,-413.60749)" id="cellgroup95">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect95" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph95" class="glyph"><tspan id="glyph95ts" x="64.110626" y="128.55876">_</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint95" class="codepoint"><tspan id="codepoint95ts" x="64.17141" y="132.90939">95</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-320.72037,-357.53278)" id="cellgroup96">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect96" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph96" class="glyph"><tspan id="glyph96ts" x="64.110626" y="128.55876">`</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint96" class="codepoint"><tspan id="codepoint96ts" x="64.17141" y="132.90939">96</tspan></text>
    </g>
    <g id="cellgroup97" transform="matrix(5.3025165,0,0,5.298385,-283.30817,-357.53263)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect97" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph97" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph97ts">a</tspan></text>
      <text id="codepoint97" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint97ts">97</tspan></text>
    </g>
    <g id="cellgroup98" transform="matrix(5.3025165,0,0,5.298385,-245.89598,-357.53278)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect98" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph98" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph98ts">b</tspan></text>
      <text id="codepoint98" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint98ts">98</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-208.48378,-357.53271)" id="cellgroup99">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect99" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph99" class="glyph"><tspan id="glyph99ts" x="64.110626" y="128.55876">c</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint99" class="codepoint"><tspan id="codepoint99ts" x="64.17141" y="132.90939">99</tspan></text>
    </g>
    <g id="cellgroup100" transform="matrix(5.3025165,0,0,5.298385,-171.07157,-357.53263)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect100" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph100" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph100ts">d</tspan></text>
      <text id="codepoint100" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint100ts">100</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-133.65936,-357.5326)" id="cellgroup101">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect101" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph101" class="glyph"><tspan id="glyph101ts" x="64.110626" y="128.55876">e</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint101" class="codepoint"><tspan id="codepoint101ts" x="64.17141" y="132.90939">101</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-96.24715,-357.53271)" id="cellgroup102">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect102" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph102" class="glyph"><tspan id="glyph102ts" x="64.110626" y="128.55876">f</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint102" class="codepoint"><tspan id="codepoint102ts" x="64.17141" y="132.90939">102</tspan></text>
    </g>
    <g id="cellgroup103" transform="matrix(5.3025165,0,0,5.298385,-58.83496,-357.53263)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect103" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph103" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph103ts">g</tspan></text>
      <text id="codepoint103" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint103ts">103</tspan></text>
    </g>
    <g id="cellgroup104" transform="matrix(5.3025165,0,0,5.298385,-21.42278,-357.53281)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect104" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph104" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph104ts">h</tspan></text>
      <text id="codepoint104" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint104ts">104</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,15.989407,-357.53278)" id="cellgroup105">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect105" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph105" class="glyph"><tspan id="glyph105ts" x="64.110626" y="128.55876">i</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint105" class="codepoint"><tspan id="codepoint105ts" x="64.17141" y="132.90939">105</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,53.401611,-357.53281)" id="cellgroup106">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect106" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph106" class="glyph"><tspan id="glyph106ts" x="64.110626" y="128.55876">j</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint106" class="codepoint"><tspan id="codepoint106ts" x="64.17141" y="132.90939">106</tspan></text>
    </g>
    <g id="cellgroup107" transform="matrix(5.3025165,0,0,5.298385,90.813803,-357.53278)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect107" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph107" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph107ts">k</tspan></text>
      <text id="codepoint107" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint107ts">107</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,128.22601,-357.53278)" id="cellgroup108">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect108" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph108" class="glyph"><tspan id="glyph108ts" x="64.110626" y="128.55876">l</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint108" class="codepoint"><tspan id="codepoint108ts" x="64.17141" y="132.90939">108</tspan></text>
    </g>
    <g id="cellgroup109" transform="matrix(5.3025165,0,0,5.298385,165.63822,-357.53263)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect109" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph109" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph109ts">m</tspan></text>
      <text id="codepoint109" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint109ts">109</tspan></text>
    </g>
    <g id="cellgroup110" transform="matrix(5.3025165,0,0,5.298385,203.05043,-357.53278)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect110" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph110" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph110ts">n</tspan></text>
      <text id="codepoint110" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint110ts">110</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,240.4626,-357.53271)" id="cellgroup111">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect111" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph111" class="glyph"><tspan id="glyph111ts" x="64.110626" y="128.55876">o</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint111" class="codepoint"><tspan id="codepoint111ts" x="64.17141" y="132.90939">111</tspan></text>
    </g>
    <g id="cellgroup112" transform="matrix(5.3025165,0,0,5.298385,-320.72037,-301.45814)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect112" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph112" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph112ts">p</tspan></text>
      <text id="codepoint112" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint112ts">112</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-283.30817,-301.4581)" id="cellgroup113">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect113" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph113" class="glyph"><tspan id="glyph113ts" x="64.110626" y="128.55876">q</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint113" class="codepoint"><tspan id="codepoint113ts" x="64.17141" y="132.90939">113</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-245.89598,-301.45821)" id="cellgroup114">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect114" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph114" class="glyph"><tspan id="glyph114ts" x="64.110626" y="128.55876">r</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint114" class="codepoint"><tspan id="codepoint114ts" x="64.17141" y="132.90939">114</tspan></text>
    </g>
    <g id="cellgroup115" transform="matrix(5.3025165,0,0,5.298385,-208.48377,-301.45814)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect115" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph115" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph115ts">s</tspan></text>
      <text id="codepoint115" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint115ts">115</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-171.07156,-301.4581)" id="cellgroup116">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect116" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph116" class="glyph"><tspan id="glyph116ts" x="64.110626" y="128.55876">t</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint116" class="codepoint"><tspan id="codepoint116ts" x="64.17141" y="132.90939">116</tspan></text>
    </g>
    <g id="cellgroup117" transform="matrix(5.3025165,0,0,5.298385,-133.65935,-301.45807)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect117" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph117" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph117ts">u</tspan></text>
      <text id="codepoint117" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint117ts">117</tspan></text>
    </g>
    <g id="cellgroup118" transform="matrix(5.3025165,0,0,5.298385,-96.247136,-301.45814)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect118" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph118" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph118ts">v</tspan></text>
      <text id="codepoint118" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint118ts">118</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-58.834949,-301.45807)" id="cellgroup119">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect119" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph119" class="glyph"><tspan id="glyph119ts" x="64.110626" y="128.55876">w</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint119" class="codepoint"><tspan id="codepoint119ts" x="64.17141" y="132.90939">119</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,-21.422769,-301.45828)" id="cellgroup120">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect120" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph120" class="glyph"><tspan id="glyph120ts" x="64.110626" y="128.55876">x</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint120" class="codepoint"><tspan id="codepoint120ts" x="64.17141" y="132.90939">120</tspan></text>
    </g>
    <g id="cellgroup121" transform="matrix(5.3025165,0,0,5.298385,15.989418,-301.45814)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect121" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph121" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph121ts">y</tspan></text>
      <text id="codepoint121" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint121ts">121</tspan></text>
    </g>
    <g id="cellgroup122" transform="matrix(5.3025165,0,0,5.298385,53.401622,-301.45828)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect122" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph122" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph122ts">z</tspan></text>
      <text id="codepoint122" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint122ts">122</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,90.813813,-301.45821)" id="cellgroup123">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect123" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph123" class="glyph"><tspan id="glyph123ts" x="64.110626" y="128.55876">{</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint123" class="codepoint"><tspan id="codepoint123ts" x="64.17141" y="132.90939">123</tspan></text>
    </g>
    <g id="cellgroup124" transform="matrix(5.3025165,0,0,5.298385,128.22602,-301.45814)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect124" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph124" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph124ts">|</tspan></text>
      <text id="codepoint124" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint124ts">124</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,165.63823,-301.4581)" id="cellgroup125">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect125" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph125" class="glyph"><tspan id="glyph125ts" x="64.110626" y="128.55876">}</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint125" class="codepoint"><tspan id="codepoint125ts" x="64.17141" y="132.90939">125</tspan></text>
    </g>
    <g transform="matrix(5.3025165,0,0,5.298385,203.05043,-301.45821)" id="cellgroup126">
      <rect y="127.66666" x="63.5" height="10.583333" width="7.0555553" id="cellrect126" transform="translate(-2.9081225,-4.3938301)" class="cell"/>
      <text xml:space="preserve" x="64.110626" y="128.55876" id="glyph126" class="glyph"><tspan id="glyph126ts" x="64.110626" y="128.55876">~</tspan></text>
      <text x="64.17141" y="132.90939" id="codepoint126" class="codepoint"><tspan id="codepoint126ts" x="64.17141" y="132.90939">126</tspan></text>
    </g>
    <g id="cellgroup127" transform="matrix(5.3025165,0,0,5.298385,240.4626,-301.45814)">
      <rect transform="translate(-2.9081225,-4.3938301)" id="cellrect127" width="7.0555553" height="10.583333" x="63.5" y="127.66666" class="cell"/>
      <text id="glyph127" y="128.55876" x="64.110626" xml:space="preserve" class="glyph"><tspan y="128.55876" x="64.110626" id="glyph127ts"></tspan></text>
      <text id="codepoint127" y="132.90939" x="64.17141" class="codepoint"><tspan y="132.90939" x="64.17141" id="codepoint127ts">127</tspan></text>
    </g>
  </g>
</svg>
"""
NS = dict(svg="http://www.w3.org/2000/svg")

COLORS = """
.L {fill:#fafaa0;}
.Cc {fill:#fdedee;}
.P {fill:#edfdee;}
.N {fill:#ededfd;}
.S {fill:#fdfded;}
.Zs {fill:#ffffff;}
.notdef {fill:#222222;}
"""


def getargparser():
    parser = ArgumentParser(description="Creates SVG file with an encoding table")
    parser.add_argument("svg", help="Output file or folder for -a", type=Path)
    parser.add_argument("-s", "--start", default=0, type=int, help="Start index")
    parser.add_argument("-e", "--encoding", default="unicode", help="Encoding")
    parser.add_argument(
        "-f",
        "--format",
        default="{codepoint}",
        help="cell caption format (vars: codepoint, char, cat, unichar)",
    )
    parser.add_argument(
        "-c", "--colors", default=False, action="store_true", help="Color by type"
    )
    parser.add_argument(
        "-a",
        "--all-encodings",
        help="Generate SVGs for many encodings and a markdown file for them as well",
        default=False,
        action="store_true",
    )
    return parser


def prepare_svg(
    codepoints: List[int | None], chars: List[str], fmt="{codepoint:02X}   {unichar}"
):
    if fmt is None:
        fmt = "{codepoint}"
    if len(codepoints) > 128:
        raise ValueError(
            f"Cannot visualize more than 128 codepoints, you passed {len(codepoints)}"
        )
    if len(codepoints) > len(chars):
        codepoints = codepoints[: len(chars)]
    elif len(codepoints) < len(chars):
        raise ValueError(f"{len(codepoints)} codepoints, but {len(chars)} characters")

    if len(codepoints) < 128:
        n_fill = 128 - len(codepoints)
        codepoints.extend([None] * n_fill)
        chars += " " * n_fill

    with resources.files("teaching").joinpath("controls.json").open() as f:
        controls: dict[str, dict[str, str]] = json.load(f)

    def get_shortcut(ch: str | int):
        if isinstance(ch, str) and len(ch) == 1:
            key = str(ord(ch))
        elif isinstance(ch, int):
            key = str(ch)
        else:
            raise TypeError(f"{ch} must be an int or a character")
        if key in controls:
            return controls[key]["ISO"]
        else:
            return ""

    svg = etree.ElementTree(etree.fromstring(SVG_TEMPLATE))
    table = svg.xpath('//*[@id="table"]')[0]
    for cell, codepoint, char in zip(table.getchildren(), codepoints, chars):
        if codepoint is None:
            cell.attrib["class"] = "no_char"
            cell[1][0].text = ""
            continue

        cat = unicodedata.category(char)
        shortcut = get_shortcut(char)
        unichar = get_shortcut(codepoint) or chr(codepoint) or "—"
        caption = fmt.format_map(
            dict(codepoint=codepoint, char=shortcut or char, cat=cat, unichar=unichar)
        )
        cell[2][0].text = caption
        if shortcut:
            cell[0].attrib["class"] += f" {cat[0]} {cat}"
            cell[1][0].text = shortcut
            cell[1][0].attrib["class"] = "shortcut"
        elif char == "�":
            cell[0].attrib["class"] += " notdef"
            cell[1][0].text = " "
        else:
            cell[0].attrib["class"] += f" {cat[0]} {cat}"
            cell[1][0].text = char if cat[0] != "C" else ""  # TODO support chars
    return svg


def _writeslide(target: Path, encoding, start=128, title=None, caption=""):
    if title is None:
        title = encoding

    codepoints = list(range(start, start + 128))
    chars = get_chars(codepoints=codepoints, encoding=encoding)
    svg = prepare_svg(codepoints, chars)
    filename = f"{encoding}.svg" if start == 128 else f"{encoding}{start}.svg"
    svgfile = target / filename
    write_svg(svg, svgfile)
    return dedent(
        f"""\
    ## {title}

    ![{caption}]({svgfile.relative_to(target.parent).with_suffix('.pdf')}){{height="80%"}}


    """
    )


def full_encoding_doc(folder: Path):
    ascii = get_chars(codepoints=range(0, 128))
    folder = Path(folder)
    images = folder / "img"
    images.mkdir(exist_ok=True, parents=True)
    with resources.files("teaching").joinpath("encoding-desc.tsv").open(
        "r", encoding="utf-8"
    ) as encodings, folder.joinpath("codepages.md").open("wt", encoding="utf-8") as out:
        out.write("---\ntitle: Traditionelle 8-Bit-Zeichenkodierungen\n---\n\n")
        out.write(
            _writeslide(
                images,
                "ascii",
                0,
                "ASCII",
                "Bei den meisten Encodings sind die ersten 128 Zeichen mit ASCII identisch",
            )
        )
        next(encodings)  # skip header
        for encoding, label, alias, lang in csv.reader(encodings, delimiter="\t"):
            start = get_chars(encoding=encoding, codepoints=range(0, 128))
            if start != ascii:
                out.write(
                    _writeslide(
                        images,
                        encoding,
                        start=0,
                        title=f"{label} (1)",
                        caption=f"{label} (0–127, weicht von ASCII ab) ({lang})",
                    )
                )
                title = f"{label} (2)"
            else:
                title = label
            out.write(
                _writeslide(
                    images, encoding, title=title, caption=f"{label} (128–255) ({lang})"
                )
            )

        images.joinpath("legende.svg").write_text(
            resources.files("teaching").joinpath("legende.svg").read_text()
        )
        out.write(
            dedent(
                f"""\
                  ## Legende

                  ![Legende zu den Grafiken]({images.relative_to(folder) / 'legende.svg'})

                  ## Quellen & Weitere Informationen

                  Zu den Steuerzeichen gibt es eine informative [Wikipedia-Seite](https://en.wikipedia.org/wiki/C0_and_C1_control_codes). Die Tabelle [am Ende jener Seite](https://en.wikipedia.org/wiki/C0_and_C1_control_codes#Character_encodings) verweist für fast jede Codierung auf eine Seite mit Details und Hintergründen.

                  Die Tabellen werden mit einem Python-Script befüllt, in dessen Zentrum diese Funktion steht:

                  ```python
                  def get_chars(*, codepoints: Iterable = range(256), encoding: str = "unicode"):
                      if encoding == "unicode":
                          return "".join(chr(n) for n in codepoints)
                      else:
                          octet_stream = bytes(codepoints)
                          return codecs.decode(octet_stream, encoding=encoding, errors="replace")
                  ```

                  Das Ergebnis eines Aufrufs wie `get_chars(encoding='latin1')`{{.python}} ist ein 256 Zeichen langer String 
                  mit den (Unicode-)Zeichen, die im [Encoding](https://docs.python.org/3/library/codecs.html#standard-encodings) _Latin 1_ an den Positionen 0 bis 255 stehen, nicht definierte
                  Zeichen sind durch U+FFFD `�` ersetzt. Die [Zeichenklassen](http://www.unicode.org/reports/tr44/#General_Category_Values) können mit [`unicodedata.category(chr)`{{.python}}](https://docs.python.org/3/library/unicodedata.html#unicodedata.category) 
                  abgefragt werden. 
                  """
            )
        )


def write_svg(svg, file):
    if options.colors:
        style_el = svg.xpath("//svg:style", namespaces=NS)[0]
        style_el.text += COLORS
    svg.write(fspath(file), pretty_print=True)


def main():
    global options
    options = getargparser().parse_args()
    if options.all_encodings:
        full_encoding_doc(options.svg)
    else:
        codepoints = list(range(options.start, options.start + 128))
        chars = list(get_chars(codepoints=codepoints, encoding=options.encoding))
        svg = prepare_svg(codepoints, chars, fmt=options.format)
        write_svg(svg, options.svg)


if __name__ == "__main__":
    main()
