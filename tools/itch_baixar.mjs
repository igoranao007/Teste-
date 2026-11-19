import { chromium } from 'playwright';
const [url, out] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ acceptDownloads: true });
await p.goto(url); await p.click('a.button.buy_btn, .download_btn, a:has-text("Download Now"), a:has-text("Download")', { timeout: 15000 });
await p.waitForTimeout(1500);
const nt = p.locator('a:has-text("No thanks")'); if (await nt.count()) { await nt.first().click(); await p.waitForLoadState(); }
await p.waitForSelector('.download_btn', { timeout: 20000 });
const btns = p.locator('.upload .download_btn'); const n = await btns.count(); console.log('uploads', n);
for (let i = 0; i < n; i++) { const [d] = await Promise.all([p.waitForEvent('download', { timeout: 120000 }), btns.nth(i).click()]); const f = out + '/' + d.suggestedFilename(); await d.saveAs(f); console.log('ok', f); }
await b.close();
