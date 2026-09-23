#!/usr/bin/env node
/* Build-time only: embed SVG + assistive MathML. No browser dependency or fonts.
 * npm install --ignore-scripts
 * node tools/typeset_math.cjs writing/example.html
 */
'use strict';
const fs = require('fs');
const {mathjax} = require('mathjax-full/js/mathjax.js');
const {TeX} = require('mathjax-full/js/input/tex.js');
const {SVG} = require('mathjax-full/js/output/svg.js');
const {liteAdaptor} = require('mathjax-full/js/adaptors/liteAdaptor.js');
const {RegisterHTMLHandler} = require('mathjax-full/js/handlers/html.js');
const {AssistiveMmlHandler} = require('mathjax-full/js/a11y/assistive-mml.js');
const {AllPackages} = require('mathjax-full/js/input/tex/AllPackages.js');
const version = require('mathjax-full/package.json').version;
const adaptor = liteAdaptor();
AssistiveMmlHandler(RegisterHTMLHandler(adaptor));
const paths = process.argv.slice(2);
if (!paths.length) throw new Error('Supply at least one generated article HTML file.');
for (const path of paths) {
  let source = fs.readFileSync(path, 'utf8');
  if (!source.includes('data-math ')) throw new Error(`${path}: expected untypeset article; regenerate it first.`);
  source = source.replace('data-math ', `data-math-static="${version}" `);
  const input = new TeX({packages: AllPackages, inlineMath: [['\\(', '\\)']],
    displayMath: [['\\[', '\\]']], tags: 'ams', processEscapes: true});
  const output = new SVG({fontCache: 'local', displayAlign: 'left'});
  const document = mathjax.document(source, {InputJax: input, OutputJax: output,
    enableAssistiveMml: true});
  document.render();
  let html = adaptor.doctype(document.document)+'\n'+adaptor.outerHTML(adaptor.root(document.document));
  if (/<g[^>]*data-mml-node="merror"/.test(html)) {
    fs.writeFileSync(path+'.failed.html', html);
    throw new Error(`${path}: invalid TeX; inspect the .failed.html file.`);
  }
  fs.writeFileSync(path, html);
  console.log(`Typeset ${path}: SVG and assistive MathML, MathJax ${version}, no runtime typesetter`);
}
