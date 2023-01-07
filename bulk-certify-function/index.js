require('dotenv').config()
const functions = require('@google-cloud/functions-framework');
const puppeteer = require('puppeteer')
const fs = require("fs/promises")
const {Storage} = require('@google-cloud/storage');

// Register an HTTP function with the Functions Framework
functions.http('bulkcertify', async (req, res) => {
    const group_no = req.body.group_no
    const certicates_list = req.body.certificates

    const browser = await puppeteer.launch();
    const storage = new Storage({
        projectId: process.env.PROJECT_ID
    });
    const bucket = storage.bucket(process.env.CLOUD_STORAGE_BUCKET);

    certicates_list.forEach(async (certificate) => {

        const page = await browser.newPage();
        await page.goto(certificate.certificate_link);
 
        let certificate_base64 = await page.$eval("#download-btn", element=> element.getAttribute("href"))
        certificate_base64 = certificate_base64.replace(/^data:image\/png;base64,/, "");
        const file = bucket.file(`${group_no}/${certificate.certificate_no}.png`);
        await file.save(Buffer.from(certificate_base64, 'base64'))
        
        await fs.writeFile(`${certificate.certificate_no}.png`, certificate_base64, "base64")
        console.log(`Uploaded ${certificate.certificate_no}`)
    })
    
    res.send('Hello, cert');
});