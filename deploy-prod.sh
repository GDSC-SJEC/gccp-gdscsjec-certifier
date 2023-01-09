gcloud run deploy gccp-gdscsjec-certifier \
--source . \
--region=us-central1 \
--allow-unauthenticated \
--no-cpu-throttling \
--min-instances=1 \
--max-instances=1 

cd bulk-certify-function

gcloud functions deploy bulkcertify \
--gen2 \
--region=us-central1 \
--runtime=nodejs16 \
--entry-point=bulkcertify \
--trigger-http \
--allow-unauthenticated \
--memory=1GiB