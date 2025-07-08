import requests
from decouple import config
import base64


def get_change_description_from_llm(image1_base64: str, image2_base64: str, model_name: str,
                                    prompt_context: str) -> str:
    api_key = config('LLM_API_KEY', default='')
    api_url = config('LLM_API_URL', default='')

    if not api_key or not api_url:
        return "LLM service API Key or URL is not configured."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    base_prompt = "You are an AI assistant for environmental monitoring. Analyze the two provided images, " \
                  "taken seconds apart. Identify significant, real-world changes. Focus on: objects that have " \
                  "appeared, disappeared, or moved; the state of devices (e.g., a light on/off); or the presence of " \
                  "people/animals. Please IGNORE minor changes in lighting, shadows, or camera noise. Provide a " \
                  "concise summary of tangible differences in Farsi."

    final_prompt = f"{base_prompt} Specific focus for this analysis: {prompt_context}" if prompt_context else base_prompt

    image1_data_uri = f"data:image/jpeg;base64,{image1_base64}"
    image2_data_uri = f"data:image/jpeg;base64,{image2_base64}"

    json_payload = {
        "model": model_name,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": final_prompt},
                    {"type": "input_image", "image_url": image1_data_uri},
                    {"type": "input_image", "image_url": image2_data_uri},
                ]
            }
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, json=json_payload, timeout=180, verify=False)
        response.raise_for_status()
        data = response.json()
        description = data['output'][0]['content'][0]['text']
        return description

    except requests.exceptions.RequestException as e:
        print(f"Error calling LLM service: {e}")
        return "Error connecting to the analysis service."
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error parsing LLM response structure: {e}. Response was: {data}")
        return "Could not parse the response from the analysis service."
