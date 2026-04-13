export CLIENT_ID = "guilledb-api-client"
export CLIENT_SECRET = "xxqukdq26ZWKx4wvx79yn1ziTVp66EkY"

export TOKEN=$ (curl -X POST "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=$CLIENT_ID" \
  -d "client_secret=$CLIENT_SECRET" | jq -r .access_token)

