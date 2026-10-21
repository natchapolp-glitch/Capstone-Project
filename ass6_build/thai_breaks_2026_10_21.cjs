const fs = require('fs');
const texts = JSON.parse(fs.readFileSync(0, 'utf8'));
const segmenter = new Intl.Segmenter('th', {granularity:'word'});
const out = texts.map(text => {
  let previous = '', result = '';
  for (const item of segmenter.segment(text)) {
    if (/[\u0e00-\u0e7f]$/.test(previous) && /^[\u0e00-\u0e7f]/.test(item.segment)) result += '\u200b';
    result += item.segment;
    previous = item.segment;
  }
  return result;
});
process.stdout.write(JSON.stringify(out));
