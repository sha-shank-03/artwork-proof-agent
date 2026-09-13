/** Update only this app's existing Railway service; credentials stay in memory. */
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {parseArgs} from 'node:util';
const root=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
async function main(){
 const {values:a}=parseArgs({options:{project:{type:'string'},environment:{type:'string'},service:{type:'string'},apply:{type:'boolean',default:false}}});
 if(!a.project||!a.environment||!a.service)throw new Error('Exact --project, --environment and --service are required');
 const controls=JSON.parse(fs.readFileSync(path.join(root,'deploy/railway-controls.json'),'utf8'));
 const statusResult=spawnSync('railway',['status','--json'],{cwd:root,encoding:'utf8'});
 if(statusResult.status!==0)throw new Error('Link this repository to the intended Railway project first');
 const status=JSON.parse(statusResult.stdout);
 if(status.id!==a.project || !status.services.edges.some(x=>x.node.id===a.service&&x.node.name===controls.serviceName) || !status.environments.edges.some(x=>x.node.id===a.environment))throw new Error('Target does not match this linked application');
 console.log(JSON.stringify(controls,null,2));
 if(!a.apply){console.log('Preview only. Add --apply to update this service, then redeploy it.');return;}
 const auth=JSON.parse(fs.readFileSync(path.join(os.homedir(),'.railway/config.json'),'utf8')).user;
 const token=auth.accessToken||auth.token;
 if(typeof token!=='string'||!token)throw new Error('Railway CLI login required');
 async function gql(query,variables){
  const response=await fetch('https://backboard.railway.com/graphql/v2',{method:'POST',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify({query,variables})});
  if(!response.ok)throw new Error('Railway HTTP '+response.status);
  const result=await response.json();
  if(result.errors)throw new Error('Railway rejected controls; raw response suppressed');
  return result.data;
 }
 const selectors={serviceId:a.service,environmentId:a.environment};
 await gql('mutation($serviceId:String!,$environmentId:String!,$input:ServiceInstanceUpdateInput!){serviceInstanceUpdate(serviceId:$serviceId,environmentId:$environmentId,input:$input)}',{...selectors,input:controls.settings});
 await gql('mutation($input:ServiceInstanceLimitsUpdateInput!){serviceInstanceLimitsUpdate(input:$input)}',{input:{...selectors,...controls.limits}});
 const verified=await gql('query($serviceId:String!,$environmentId:String!){serviceInstance(serviceId:$serviceId,environmentId:$environmentId){serviceName healthcheckPath healthcheckTimeout sleepApplication restartPolicyMaxRetries}}',selectors);
 console.log(JSON.stringify(verified));
 console.log('Settings stored. Redeploy the service and verify the active deployment and /ready.');
}
main().catch(e=>{console.error('Configuration failed: '+e.name+'; credential-bearing details suppressed. Check CLI login and exact target IDs.');process.exitCode=1;});
