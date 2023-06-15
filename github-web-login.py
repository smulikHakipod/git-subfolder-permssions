import asyncio
from pyppeteer import launch
import sys
import time
import json 

browser = None
async def main():
    global browser
    print("starting")
    browser = await launch(headless=True, executablePath='/usr/bin/chromium-browser', args=['--no-sandbox'])
    page = await browser.newPage()
    await page.goto('https://github.com/login')
    await page.type('#login_field', sys.argv[1])
    await page.type('#password', sys.argv[2]) 
    await page.click('[name="commit"]')
    await page.waitForNavigation()
    print("username", sys.argv[1])
    if page.url.endswith('/session'):
        print("failed logged in")
        exit(1)
    print("logged in")

    with open('/app/cookies.json', 'w') as f:
        json.dump(await page.cookies(), f)


    # we want to the token to be refreshed every hour
    while True:
        await page.reload()
        with open('/app/cookies.json', 'w') as f:
            json.dump(await page.cookies(), f)
        time.sleep(60)




asyncio.get_event_loop().run_until_complete(main())