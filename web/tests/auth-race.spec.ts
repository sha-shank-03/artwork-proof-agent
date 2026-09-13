import {test,expect} from '@playwright/test';

test('late unauthenticated history response cannot overwrite a successful login',async({page})=>{
 test.skip(process.env.EXPECT_LIVE_DISABLED==='true','Invitation UI is disabled in this deployment');
 let release!:()=>void;
 const delayed=new Promise<void>(resolve=>{release=resolve;});
 let requested!:()=>void;
 const started=new Promise<void>(resolve=>{requested=resolve;});
 await page.route('**/api/runs',async route=>{
  requested();await delayed;await route.fulfill({status:401,json:{detail:'Invitation required'}});
 });
 await page.route('**/api/session',route=>route.fulfill({status:200,json:{ok:true}}));
 await page.goto('/#run');await page.getByRole('tab',{name:'Invited live access'}).click();
 await started;
 await page.getByLabel('Invitation token').fill('test-only-invitation-not-a-live-secret');
 await page.getByRole('button',{name:'Open proof workspace'}).click();
 await expect(page.getByLabel('Or use original demo artwork')).toBeVisible();
 const response=page.waitForResponse(r=>r.url().endsWith('/api/runs'));
 release();await response;await page.waitForLoadState('networkidle');
 await expect(page.getByLabel('Or use original demo artwork')).toBeVisible();
 await expect(page.getByLabel('Invitation token')).toHaveCount(0);
});
