import subprocess, re

r = subprocess.run(
    ['node', '-e', '''
const fs = require("fs");
const m = fs.readFileSync("index.html","utf8").match(/<script>([\\s\\S]*?)<\\/script>/);
if(!m){console.log("no script");process.exit(1);}
try{new Function(m[1]);console.log("JS OK");}
catch(e){console.log("JS ERROR:",e.message);}
'''],
    capture_output=True, text=True,
    cwd=r'C:\Users\frank\.openclaw\workspace\projects\co-parenting-portal'
)
print(r.stdout)
if r.stderr: print('STDERR:', r.stderr)
