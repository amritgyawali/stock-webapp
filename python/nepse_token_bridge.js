const fs = require('fs');
const path = require('path');

async function run() {
    const wasmPath = process.argv[2] || path.join(__dirname, 'temp_nepse/nepse/data/css.wasm');
    const action = process.argv[3]; // 'parse'
    const salts = process.argv.slice(4).map(Number);

    if (!fs.existsSync(wasmPath)) {
        console.error(JSON.stringify({ error: `WASM not found at ${wasmPath}` }));
        process.exit(1);
    }

    const wasmBuffer = fs.readFileSync(wasmPath);
    const wasmModule = await WebAssembly.instantiate(wasmBuffer);
    const exports = wasmModule.instance.exports;

    if (action === 'call') {
        const funcName = process.argv[4];
        const funcSalts = process.argv.slice(5).map(Number);
        if (typeof exports[funcName] !== 'function') {
            console.error(JSON.stringify({ error: `Function ${funcName} not found` }));
            process.exit(1);
        }
        const result = exports[funcName](...funcSalts);
        console.log(JSON.stringify({ result }));
    } else if (action === 'batch') {
        // Expecting 5 salts: s1, s2, s3, s4, s5
        const [s1, s2, s3, s4, s5] = salts;
        
        const results = {
            // Access Token Logic
            n: exports.cdx(s1, s2, s3, s4, s5),
            l: exports.rdx(s1, s2, s4, s3, s5),
            o: exports.bdx(s1, s2, s4, s3, s5),
            p: exports.ndx(s1, s2, s4, s3, s5),
            q: exports.mdx(s1, s2, s4, s3, s5),
            
            // Refresh Token Logic
            a: exports.cdx(s2, s1, s3, s5, s4),
            b: exports.rdx(s2, s1, s3, s4, s5),
            c: exports.bdx(s2, s1, s4, s3, s5),
            d: exports.ndx(s2, s1, s4, s3, s5),
            e: exports.mdx(s2, s1, s4, s3, s5),
        };
        console.log(JSON.stringify(results));
    } else {
        console.error(JSON.stringify({ error: 'Unknown action' }));
        process.exit(1);
    }
}

run().catch(err => {
    console.error(JSON.stringify({ error: err.message }));
    process.exit(1);
});
