require('dotenv').config()
const functions = require('@google-cloud/functions-framework');
const puppeteer = require('puppeteer')
//const fs = require("fs/promises")
const {Storage} = require('@google-cloud/storage');
const axios = require("axios")

functions.http('bulkcertify', async (req, res) => {
    res.set('Access-Control-Allow-Origin', '*');

    if (req.method === 'OPTIONS') {
        // Send response to OPTIONS requests
        res.set('Access-Control-Allow-Methods', 'GET');
        res.set('Access-Control-Allow-Headers', 'Content-Type');
        res.set('Access-Control-Max-Age', '3600');
        res.status(204).send('');
    } else {
        const group_no = req.query.group_no
        console.log(`Bulk Certifying Group: ${group_no}`)
        const bulk_certificate_response = await axios.get(process.env.API_URL + "/certificate/mass-generate/" + group_no)
        const certicates_list = bulk_certificate_response.data.certificates

        const browser = await puppeteer.launch();
        const storage = new Storage({
            projectId: process.env.PROJECT_ID
        });
        const bucket = storage.bucket(process.env.CLOUD_STORAGE_BUCKET);

        for (i = 0; i < certicates_list.length; i++) {
            const certificate = certicates_list[i]
            console.log(bucket.name)
            console.log(certificate)
            const page = await browser.newPage();
            await page.goto(certificate.certficate_link);
    
            let certificate_base64 = await page.$eval("#download-btn", element=> element.getAttribute("href"))
            certificate_base64 = certificate_base64.replace(/^data:image\/png;base64,/, "");
            const file = bucket.file(`${group_no}/${certificate.certificate_no}.png`);
            await file.save(Buffer.from(certificate_base64, 'base64'))
            
            //await fs.writeFile(`${certificate.certificate_no}.png`, certificate_base64, "base64")
            console.log(`Uploaded ${certificate.certificate_no}`)
          } 
        
        const certificate_url_response = await axios.get(process.env.API_URL + "/download-zip/" + group_no)

        await axios.put(process.env.API_URL + "/update-zip-url/" + group_no + "?zip_url=" + certificate_url_response.data.certificate_url)

        res.json({certificate_url: certificate_url_response.data.certificate_url})
    }
});