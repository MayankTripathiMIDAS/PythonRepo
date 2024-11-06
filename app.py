import requests
import re
import json

# External API details
EXTERNAL_API_URL_TEMPLATE = "https://hrmsapi.midastech.org:8443/api/v1/candidateMidas/candidateById/{}"
UPDATE_API_URL = "https://hrmsapi.midastech.org:8443/api/v1/candidateMidas/updateCandidateById"
EXTERNAL_API_HEADERS = {
    "accept": "*/*",
    "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhcmNoaXQubWlzaHJhQG1pZGFzdHJhdmVsLm9yZyIsInJvbGVzIjpbIlNVUEVSQURNSU4iXSwiZXhwIjoxNzMxNTU5MDc1fQ.OAOjUusBcpP92NQCNn54p51gVd9I42uDNUm_GxkmpfBeNXtFz9CJ9H5XA4X9_cntFOYJs6EVGRvgrltPEjJKyA"
}

def extract_address(full_text):
    """Extract address components (city, state, zip) from the full text."""
    address_match = re.search(r'([A-Za-z\s]+),\s([A-Z]{2})\s(\d{5})', full_text)
    return address_match.groups() if address_match else (None, None, None)

# Load the JSON file with IDs
with open('hrms1.json', 'r') as file:
    ids_data = json.load(file)

# Process each candidate by ID
for entry in ids_data:
    candidate_id = entry["_id"]["$oid"]
    external_api_url = EXTERNAL_API_URL_TEMPLATE.format(candidate_id)

    try:
        # Fetch data from the external API for each candidate
        response = requests.get(external_api_url, headers=EXTERNAL_API_HEADERS)
        response.raise_for_status()  # Check for HTTP errors

        # Parse the JSON response
        external_data = response.json()
        print(f"Data for candidate {candidate_id}: {external_data}")

        # Attempt to access the 'payload' key safely
        try:
            fulldata = external_data['payload']
            if fulldata is None:
                print(f"'payload' is None for candidate {candidate_id}. Skipping update.")
                continue  # Skip to the next candidate if payload is None

            full_text = fulldata.get('fullText')

            # Check if 'fullText' is available
            if full_text:
                try:
                    # Extract address from full text
                    city, state, zip_code = extract_address(full_text)
                    print("Extracted Address:", city, state, zip_code)

                    # Prepare the updated JSON data
                    json_data = {
                        "additionalProperties": fulldata.get("additionalProperties", {}),
                        "certifications": fulldata.get("certifications"),
                        "city": city or "",
                        "companiesWorkedAt": fulldata.get("companiesWorkedAt", []),
                        "contactTime": fulldata.get("contactTime", ""),
                        "currentCTC": fulldata.get("currentCTC", ""),
                        "dateIssued": fulldata.get("dateIssued", ""),
                        "dateOfBirth": fulldata.get("dateOfBirth", ""),
                        "date_added": fulldata.get("date_added", ""),
                        "degree": fulldata.get("degree", [{}]),
                        "designation": fulldata.get("designation", []),
                        "desiredShifts": fulldata.get("desiredShifts", ""),
                        "eligibleToWorkUS": fulldata.get("eligibleToWorkUS", True),
                        "email": fulldata.get("email", ""),
                        "expirationDate": fulldata.get("expirationDate", ""),
                        "fileHandle": fulldata.get("fileHandle", {}),
                        "fullText": full_text,
                        "gender": fulldata.get("gender", ""),
                        "hasLicenseInvestigated": fulldata.get("hasLicenseInvestigated", True),
                        "id": fulldata.get("id", ""),
                        "investigationDetails": fulldata.get("investigationDetails", ""),
                        "issuingState": fulldata.get("issuingState", ""),
                        "lastName": fulldata.get("lastName", ""),
                        "last_updated": fulldata.get("last_updated", ""),
                        "license": fulldata.get("license", [""]),
                        "licenseNumber": fulldata.get("licenseNumber", ""),
                        "licensedStates": fulldata.get("licensedStates", ""),
                        "licenses": fulldata.get("licenses", [{}]),
                        "municipality": fulldata.get("municipality", ""),
                        "name": fulldata.get("name", ""),
                        "otherPhone": fulldata.get("otherPhone", ""),
                        "phone": fulldata.get("phone", ""),
                        "preferredCities": fulldata.get("preferredCities", [""]),
                        "preferredDestinations": fulldata.get("preferredDestinations", ""),
                        "primarySpeciality": fulldata.get("primarySpeciality", ""),
                        "profession": fulldata.get("profession", ""),
                        "regions": fulldata.get("regions", ""),
                        "skills": fulldata.get("skills", [""]),
                        "source": fulldata.get("source", ""),
                        "state": state or "",
                        "totalExp": fulldata.get("totalExp", ""),
                        "travelStatus": fulldata.get("travelStatus", ""),
                        "workAuthorization": fulldata.get("workAuthorization", ""),
                        "zip": zip_code or ""
                    }

                    print("Updated JSON Data:", json_data)

                    # Send the PATCH request to update the candidate
                    patch_response = requests.patch(UPDATE_API_URL, headers=EXTERNAL_API_HEADERS, json=json_data)

                    if patch_response.ok:
                        print(f"Candidate {candidate_id} updated successfully.")
                    else:
                        print(f"Failed to update candidate {candidate_id}: {patch_response.status_code} {patch_response.text}")

                except AttributeError:
                    print(f"No address found in fullText for candidate {candidate_id}. Skipping update.")
            else:
                print(f"'fullText' not available for candidate {candidate_id}. Skipping update.")

        except KeyError:
            print(f"'payload' key not found in the response for candidate {candidate_id}. Skipping update.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data for candidate {candidate_id}: {e}")
