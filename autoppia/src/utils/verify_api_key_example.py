"""
Example usage of the API key verification utilities.
"""
from autoppia.src.utils.api_key import ApiKeyVerifier

def example_verify_api_key(api_key: str):
    try:
        verifier = ApiKeyVerifier(base_url="https://api.autoppia.com")
        result = verifier.verify_api_key(api_key)
        print("Verification result:", result)
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    example_verify_api_key("pk_uql4okogwfm") 