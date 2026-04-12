const https = require('https');
const fs = require('fs');
const path = require('path');

const url = 'https://hanyunfan.github.io/co-parenting-portal/';
const outPath = path.join(__dirname, '_fetched.html');

https.get(url, (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        fs.writeFileSync(outPath, data);
        console.log('Fetched', data.length, 'chars to', outPath);

        // Extract and check JS
        const m = data.match(/<script>([\s\S]*?)<\/script>/);
        if (!m) { console.log('No script'); return; }
        const js = m[1];
        try {
            new Function(js);
            console.log('JS SYNTAX: OK');
        } catch(e) {
            console.log('JS ERROR:', e.message);
        }

        // Check for key functions
        console.log('isMomSummerDay:', js.includes('isMomSummerDay') ? 'YES' : 'NO');
        console.log('getSchoolBreakCustody:', js.includes('getSchoolBreakCustody') ? 'YES' : 'NO');
        console.log('generateESPOCalendar:', js.includes('generateESPOCalendar') ? 'YES' : 'NO');
    });
}).on('error', e => console.error(e));
