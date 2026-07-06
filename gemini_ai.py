from google import genai

def ask_gemini(api_key, question, data):

    try:

        client = genai.Client(
            api_key=api_key.strip()
        )

        prompt = f"""
Factory Data:

{data}

Question:
{question}

Give industrial analysis and recommendations.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        return f"ERROR: {str(e)}"