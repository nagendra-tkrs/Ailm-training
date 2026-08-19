import fs from 'fs/promises';
import path from 'path';
import { chromium } from 'playwright';

const root = path.resolve('..'); // d:/Ailm-training/frontend/.. -> d:/Ailm-training
const reportsDir = path.join(root, 'reports');
const csvPath = path.join(reportsDir, 'frontend_e2e_report.csv');
const jsonPath = path.join(root, 'scripts', 'frontend_e2e_report.json');
const screenshotPath = path.join(reportsDir, 'playwright', 'e2e-final.png');
const outputHtml = path.join(reportsDir, 'frontend_test_report.html');
const outputPdf = path.join(reportsDir, 'frontend_test_report.pdf');

function csvToTable(csv) {
  const lines = csv.trim().split(/\r?\n/);
  const headers = lines[0].split(',');
  const rows = lines.slice(1).map(l => {
    // naive CSV split
    const parts = [];
    let cur = '';
    let inQuote = false;
    for (let i = 0; i < l.length; i++) {
      const ch = l[i];
      if (ch === '"') { inQuote = !inQuote; continue; }
      if (ch === ',' && !inQuote) { parts.push(cur); cur = ''; continue; }
      cur += ch;
    }
    parts.push(cur);
    return parts;
  });

  let html = '<table class="csv-table">';
  html += '<thead><tr>' + headers.map(h => `<th>${h}</th>`).join('') + '</tr></thead>';
  html += '<tbody>' + rows.map(r => '<tr>' + r.map(c => `<td>${c}</td>`).join('') + '</tr>').join('') + '</tbody>';
  html += '</table>';
  return html;
}

(async ()=>{
  try {
    const [csvBuf, jsonBuf] = await Promise.all([
      fs.readFile(csvPath, 'utf8'),
      fs.readFile(jsonPath, 'utf8')
    ]);

    let screenshotBase64 = null;
    try {
      const img = await fs.readFile(screenshotPath);
      screenshotBase64 = img.toString('base64');
    } catch(e) {
      console.warn('Screenshot not found, continuing without image.');
    }

    const jsonReport = JSON.parse(jsonBuf);

    const htmlParts = [];
    htmlParts.push(`<!doctype html><html><head><meta charset="utf-8"><title>Frontend Test Report</title><style>body{font-family:Arial,Helvetica,sans-serif;margin:24px;color:#222}h1,h2{color:#0b5d6a}section{margin-bottom:20px}table.csv-table{width:100%;border-collapse:collapse}table.csv-table th,table.csv-table td{border:1px solid #ddd;padding:8px;text-align:left}table.csv-table th{background:#f2f2f2}img.screenshot{max-width:100%;height:auto;border:1px solid #ccc;box-shadow:0 2px 6px rgba(0,0,0,.08)}</style></head><body>`);

    htmlParts.push('<h1>Frontend Test Report</h1>');
    htmlParts.push('<section><h2>Summary</h2>');
    htmlParts.push('<p>Automated Playwright UI and API tests were run against the local backend and frontend. This report includes the CSV summary, JSON details, and screenshots.</p>');
    htmlParts.push('</section>');

    // CSV as table
    htmlParts.push('<section><h2>CSV Summary</h2>');
    htmlParts.push(csvToTable(csvBuf));
    htmlParts.push('</section>');

    // JSON details (pretty)
    htmlParts.push('<section><h2>JSON Report Details</h2>');
    htmlParts.push('<pre style="background:#f8f8f8;border:1px solid #eee;padding:12px;overflow:auto;max-height:400px">');
    htmlParts.push(JSON.stringify(jsonReport, null, 2));
    htmlParts.push('</pre>');
    htmlParts.push('</section>');

    // Screenshot
    htmlParts.push('<section><h2>Screenshots</h2>');
    if (screenshotBase64) {
      htmlParts.push(`<p>Final UI screenshot captured after running Playwright:</p><img class="screenshot" src="data:image/png;base64,${screenshotBase64}" alt="e2e-final"/>`);
    } else {
      htmlParts.push('<p>No screenshot available.</p>');
    }
    htmlParts.push('</section>');

    // Footer
    htmlParts.push(`<footer><p>Generated: ${new Date().toISOString()}</p></footer>`);
    htmlParts.push('</body></html>');

    const html = htmlParts.join('\n');
    await fs.writeFile(outputHtml, html, 'utf8');

    // Render PDF via Playwright
    const browser = await chromium.launch();
    const page = await browser.newPage({viewport:{width:1200,height:1600}});
    await page.setContent(html, {waitUntil:'networkidle'});
    await page.pdf({ path: outputPdf, format: 'A4', printBackground: true });
    await browser.close();

    console.log('PDF generated at:', outputPdf);
  } catch (err) {
    console.error('Error generating PDF report:', err);
    process.exit(1);
  }
})();
