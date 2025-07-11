import requests
from decouple import config
import base64
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_change_description_from_llm(image1_base64: str, image2_base64: str, model_name: str,
                                    prompt_context: str) -> str:
    api_key = config('LLM_API_KEY', default='')
    api_url = config('LLM_API_URL', default='')

    if not api_key or not api_url:
        logger.warning("LLM service API Key or URL is not configured.")
        return "LLM service API Key or URL is not configured."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    current_time = timezone.localtime(timezone.now()).strftime('%Y-%m-%d %H:%M:%S')
    time_context = f"System Context: The current time of analysis is {current_time}. Please consider this time in your response."

    final_prompt = f"{time_context}\n\nUser's Prompt: {prompt_context}"

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

    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    response = None
    try:
        response = session.post(api_url, headers=headers, json=json_payload, timeout=180, verify=False)
        response.raise_for_status()
        data = response.json()
        description = data['output'][0]['content'][0]['text']
        return description

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling LLM service: {e}")
        return "Error connecting to the analysis service."
    except (KeyError, IndexError, TypeError) as e:
        data_preview = str(response.json())[:200] if 'response' in locals() else "N/A"
        logger.error(f"Error parsing LLM response structure: {e}. Response preview: {data_preview}")
        return "Could not parse the response from the analysis service."
