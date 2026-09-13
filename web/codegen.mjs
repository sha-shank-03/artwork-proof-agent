import {execFileSync} from 'node:child_process';
import {writeFileSync} from 'node:fs';
import openapiTS, {astToString} from 'openapi-typescript';
const schema=execFileSync('.venv/bin/python',['-m','app.cli','schema'],{cwd:'..',encoding:'utf8'});
writeFileSync('../openapi.json',schema);
const ast=await openapiTS(JSON.parse(schema));
writeFileSync('src/generated.ts',astToString(ast));
