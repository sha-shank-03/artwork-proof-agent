import {test,expect} from '@playwright/test';

test('public catalogue never calls a backend and is honest about unavailable recordings',async({page})=>{
 const calls:string[]=[];const errors:string[]=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/api/**',route=>{calls.push(route.request().url());return route.abort();});
 await page.goto('/');
 await expect(page.getByRole('heading',{level:1})).toContainText('Inspect the details.');
 const index=await (await page.request.get('/replays/index.json')).json();
 if(index.runs.length===0)await expect(page.getByText('There are no fabricated model results here.',{exact:false})).toBeVisible();
 else await expect(page.getByRole('slider',{name:'Recorded timeline position'})).toBeVisible();
 expect(calls).toEqual([]);expect(errors).toEqual([]);
});
test('mobile layout and keyboard invitation entry',async({page})=>{
 await page.setViewportSize({width:390,height:844});await page.goto('/');
 await expect(page.getByRole('heading',{level:1})).toBeVisible();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBe(true);
 const live=page.getByRole('tab',{name:'Invited live access'});await live.focus();await page.keyboard.press('Enter');
 await expect(page.getByLabel('Invitation token')).toBeVisible();
 await page.getByLabel('Invitation token').fill('deliberately-invalid-demo-token');
 await expect(page.getByLabel('Invitation token')).toHaveAttribute('type','password');
});
