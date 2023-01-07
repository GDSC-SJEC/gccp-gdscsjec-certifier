const functions = require('@google-cloud/functions-framework');
const puppeteer = require('puppeteer')
const fs = require("fs/promises")

// Register an HTTP function with the Functions Framework
functions.http('bulkcertify', async (req, res) => {
    const certicates_list = req.body
    const browser = await puppeteer.launch();
    let counter=0;

    certicates_list.forEach(async (certificate) => {
        counter++
        console.log(certificate)

        const page = await browser.newPage();
        await page.goto(certificate);
 
        let certificate_base64 = await page.$eval("#download-btn", element=> element.getAttribute("href"))
        certificate_base64 = certificate_base64.replace(/^data:image\/png;base64,/, "");
        try {
            await fs.writeFile(`out_${counter}.png`, certificate_base64, "base64")
        } catch (error) {
            console.log(error)
        }

    })
    

    res.send('Hello, cert');
});