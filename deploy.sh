gcloud builds submit --tag gcr.io/plaid-generic/rebalancer

gcloud run deploy rebalancer \
    --image gcr.io/plaid-generic/rebalancer \
    --platform managed \
    --set-env-vars PLAID_CLIENT_ID=61e8a5cf7b79c5001aa87be0,EMAIL_ADDRESS=andrew.vagliano1@gmail.com \
    --set-secrets="PLAID_SECRET=PlaidSecret:latest"
