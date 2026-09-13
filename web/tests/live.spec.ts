import {test,expect} from '@playwright/test';
import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';

test('invited upload and clarification survive refresh without a provider call',async({page})=>{
 test.skip(process.env.LOCAL_API_TEST!=='true','Local API must be explicitly enabled');
 execFileSync('.venv/bin/python',['-m','app.cli','invite'],{cwd:'..',stdio:'ignore'});
 const invitation=readFileSync('../.local/invite.txt','utf8').trim();
 await page.goto('/');await page.getByRole('tab',{name:'Invited live access'}).click();
 await page.getByLabel('Invitation token').fill(invitation);
 await page.getByRole('button',{name:'Open proof workspace'}).click();
 await page.getByLabel('Or use original demo artwork').selectOption('clean-mark');
 await expect(page.getByText('Selected: clean-mark.png')).toBeVisible();
 await page.getByLabel('Width (in)').fill('');await page.getByLabel('Height (in)').fill('');
 await page.getByRole('button',{name:'Analyze artwork'}).click();
 await expect(page.getByLabel('Reviewer clarification')).toBeVisible();
 await expect(page.getByText('$0.0000',{exact:true})).toBeVisible();
 await page.reload();await page.getByRole('tab',{name:'Invited live access'}).click();
 await expect(page.getByLabel('Reviewer clarification')).toBeVisible();
 await page.getByRole('button',{name:'Cancel analysis'}).click();
 await expect(page.getByLabel('Reviewer clarification')).toHaveCount(0);
});
