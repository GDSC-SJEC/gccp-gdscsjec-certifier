require('dotenv').config()
const {Storage} = require('@google-cloud/storage');

const storage = new Storage({
    projectId: process.env.PROJECT_ID
});
const bucket = storage.bucket(process.env.CLOUD_STORAGE_BUCKET);

const file = bucket.file('3/GDSC-SJEC0001.png');
let certificate_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII"
certificate_base64 = certificate_base64.replace(/^data:image\/png;base64,/, "");
file.save(Buffer.from(certificate_base64)).then(() => console.log('done'));

    