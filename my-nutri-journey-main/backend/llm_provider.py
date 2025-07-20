import base64
import json
import diskcache
import concurrent.futures
import time
from settings import LLM_TIMEOUT
#from langchain_g4f import G4FLLM
#from g4f import models as g4f_models

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_deepseek import DeepSeekLLM
except ImportError:
    DeepSeekLLM = None


class LLMProvider:
    _image_cache = diskcache.Cache("cache/image_llm_cache")

    def __init__(self, provider="g4f", model=None, cache_len=100, timeout=20, **kwargs):

        self.provider = provider.lower()
        self.model = model
        self.kwargs = kwargs
        self.llm = self._init_llm()
        self._cache_len = cache_len
        self.timeout = LLM_TIMEOUT or timeout  # Timeout in seconds

    def _init_llm(self):
        if self.provider == "g4f":
            #selected_model = self.model or g4f_models.gpt_4o
            #return G4FLLM(model=selected_model, **self.kwargs)
            pass
        elif self.provider == "openai":
            if ChatOpenAI is None:
                raise ImportError("langchain_openai is not installed.")
            selected_model = self.model or "gpt-3.5-turbo"
            return ChatOpenAI(model=selected_model, **self.kwargs)
        elif self.provider == "deepseek":
            if DeepSeekLLM is None:
                raise ImportError("langchain_deepseek is not installed.")
            selected_model = self.model or "deepseek-chat"
            return DeepSeekLLM(model=selected_model, **self.kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    @staticmethod
    def extract_json(response_str):
        """
        Extract JSON from a string, handling both markdown code blocks and raw JSON.
        
        Args:
            response_str: The response string from an LLM
            
        Returns:
            Parsed JSON as dict/list if successful, else None
        """
        if not response_str:
            return None
            
        # First try to extract from markdown code blocks
        if "```json" in response_str:
            # Extract content between ```json and ```
            start_idx = response_str.find("```json") + 7
            end_idx = response_str.find("```", start_idx)
            if end_idx > start_idx:
                json_str = response_str[start_idx:end_idx].strip()
                try:
                    return json.loads(json_str)
                except:
                    pass  # Fall through to other methods if this fails
        
        # Try code block without language specification
        if "```" in response_str:
            # Extract content between ``` and ```
            start_idx = response_str.find("```") + 3
            end_idx = response_str.find("```", start_idx)
            if end_idx > start_idx:
                json_str = response_str[start_idx:end_idx].strip()
                try:
                    return json.loads(json_str)
                except:
                    pass  # Fall through to other methods if this fails
        
        # Finally, try to find JSON anywhere in the string
        try:
            # Look for the first { and last }
            start = response_str.find('{')
            end = response_str.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = response_str[start:end]
                return json.loads(json_str)
        except:
            pass
            
        # If all attempts fail, return None
        return None

    def ask(self, prompt: str, json_response: bool = False, timeout: int = None) -> dict:
        """
        Ask a question to the LLM and get a response.
        
        Args:
            prompt: The prompt to send to the LLM
            json_response: Whether to parse the response as JSON
            timeout: Timeout in seconds (overrides the instance timeout)
        
        Returns:
            A dictionary with the response and token count, or None if timeout occurs
        """
        # Use the provided timeout or fall back to the instance timeout
        request_timeout = timeout or self.timeout
        
        # Use ThreadPoolExecutor to run the LLM request with a timeout
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit the task
            future = executor.submit(self._execute_llm_request, prompt)
            
            try:
                # Wait for the result with a timeout
                start_time = time.time()
                response = future.result(timeout=request_timeout)
                elapsed_time = time.time() - start_time
                print(f"LLM response received in {elapsed_time:.2f} seconds")
                
                if isinstance(response, str):
                    content = response
                else:
                    content = getattr(response, "content", None) or str(response)
                
                if hasattr(response, "response_metadata"):
                    token_info = response.response_metadata.get("token_usage", {})
                    tokens = token_info.get('total_tokens', None)
                else:
                    tokens = (len(prompt) + len(content)) // 4
                
                if json_response:
                    parsed_json = self.extract_json(content)
                    return {
                        'response': parsed_json,
                        'raw_response': content,
                        'tokens': tokens
                    }
                else:
                    return {
                        'response': content,
                        'tokens': tokens
                    }
            
            except concurrent.futures.TimeoutError:
                print(f"LLM request timed out after {request_timeout} seconds")
                # Cancel the future if possible
                future.cancel()
                # Return None to indicate timeout
                return {
                    'response': None,
                    'error': 'Request timed out',
                    'tokens': 0
                }
            except Exception as e:
                print(f"Error in LLM request: {str(e)}")
                return {
                    'response': None,
                    'error': str(e),
                    'tokens': 0
                }
    
    def _execute_llm_request(self, prompt):
        """Execute the actual LLM request - separated for timeout handling"""
        return self.llm.invoke(prompt)
    
    def extract_json_from_response(self, response_text):
        """
        Extract JSON from a response text that might include markdown code blocks.
        """
        if not response_text:
            return None
            
        # Check if the response contains a JSON code block
        if "```json" in response_text:
            # Extract the content between ```json and ```
            start_idx = response_text.find("```json") + 7
            end_idx = response_text.find("```", start_idx)
            if end_idx > start_idx:
                json_str = response_text[start_idx:end_idx].strip()
                try:
                    return json.loads(json_str)
                except:
                    return None
        
        # Check if it's a code block without language specification
        elif "```" in response_text:
            # Extract content between ``` and ```
            start_idx = response_text.find("```") + 3
            end_idx = response_text.find("```", start_idx)
            if end_idx > start_idx:
                json_str = response_text[start_idx:end_idx].strip()
                try:
                    return json.loads(json_str)
                except:
                    return None
        
        # If no code blocks, try to extract JSON directly
        return None

    def ask_with_image(self, prompt: str, image_path: str, mime_type: str = "image/jpeg", 
                   json_response: bool = False, cache: bool = True, timeout: int = None) -> dict:
        """
        Use a vision-capable OpenAI model via LangChain to process a prompt and image.
        Uses diskcache to cache results by image_path, keeping only the last self._cache_len elements.
        
        Args:
            timeout: Timeout in seconds (overrides the instance timeout)
        """
        # Use the provided timeout or fall back to the instance timeout
        request_timeout = timeout or self.timeout
        
        # Clean up cache if over limit
        while len(self._image_cache) > self._cache_len:
            self._image_cache.popitem(last=False)

        if cache and image_path in self._image_cache:
            return self._image_cache[image_path]

        if self.provider != "openai":
            raise NotImplementedError("ask_with_image is only implemented for OpenAI provider.")

        if ChatOpenAI is None:
            raise ImportError("langchain_openai is not installed.")

        # Read and encode the image
        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        # Prepare the message in OpenAI's vision format
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}"
                        }
                    }
                ]
            }
        ]

        llm = ChatOpenAI(model=self.model or "gpt-4o", **self.kwargs)
        
        # Use ThreadPoolExecutor to run the LLM request with a timeout
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit the task
            future = executor.submit(llm.invoke, messages)
            
            try:
                # Wait for the result with a timeout
                start_time = time.time()
                response = future.result(timeout=request_timeout)
                elapsed_time = time.time() - start_time
                print(f"LLM image response received in {elapsed_time:.2f} seconds")
                
                content = getattr(response, "content", None) or str(response)
                tokens = (len(prompt) + len(content)) // 4

                if json_response:
                    result = {
                        "response": self.extract_json(content),
                        "raw_response": content,
                        "tokens": tokens
                    }
                else:
                    result = {
                        "response": content,
                        "tokens": tokens
                    }

                if cache:
                    self._image_cache[image_path] = result

                return result
            
            except concurrent.futures.TimeoutError:
                print(f"LLM image request timed out after {request_timeout} seconds")
                # Cancel the future if possible
                future.cancel()
                # Return None to indicate timeout
                return {
                    'response': None,
                    'error': 'Request timed out',
                    'tokens': 0
                }
            except Exception as e:
                print(f"Error in LLM image request: {str(e)}")
                return {
                    'response': None,
                    'error': str(e),
                    'tokens': 0
                }
    

def main():
    prompt = "Hello, who are you?"

    # Test g4f
    '''print("\n--- Testing g4f ---")
    try:
        g4f_provider = LLMProvider(provider="g4f")
        response = g4f_provider.ask(prompt)
        print("g4f response:", response)
    except Exception as e:
        print("g4f failed:", e)'''

    # Test openai
    print("\n--- Testing OpenAI ---")
    try:
        openai_provider = LLMProvider(provider="openai", model="gpt-3.5-turbo")
        response = openai_provider.ask(prompt)
        print("OpenAI response:", response)
    except Exception as e:
        print("OpenAI failed:", e)


if __name__ == "__main__":
    main()
