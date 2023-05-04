from django.conf import settings
import openai
OPENAI_API_KEY=settings.OPENAI_API_KEY

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

def openai_call(
      prompt: str,
      temperature: float = 0.5,
      max_tokens: int = 100,
      role: str = "system",
      previous_messages: list = None
):
        model = "gpt-3.5-turbo"
        max_retries = 5
        for retries in range(0, max_retries):
            try:
                # Use chat completion API
                if not previous_messages:
                    messages = [{"role": role, "content": prompt}]
                else:
                    messages = previous_messages + [{"role": role, "content": prompt}]
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=1,
                    stop=None,
                )
                return (response.choices[0].message.content.strip(), response.usage.total_tokens)
            except openai.error.RateLimitError:
                print(
                    "   *** The OpenAI API rate limit has been exceeded. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
                continue
            except openai.error.Timeout:
                print(
                    "   *** OpenAI API timeout occured. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
                continue
            except openai.error.APIError:
                print(
                    "   *** OpenAI API error occured. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
                continue
            except openai.error.APIConnectionError:
                print(
                    "   *** OpenAI API connection error occured. Check your network settings, proxy configuration, SSL certificates, or firewall rules. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
                continue
            except openai.error.InvalidRequestError as e:
                print(
                        f"   *** OpenAI API invalid request. {e} Check the documentation for the specific API method you are calling and make sure you are sending valid and complete parameters. Waiting 10 seconds and bailing. "
                )
                time.sleep(10)  # Wait 10 seconds and try again
                retries=max_retries
            except openai.error.ServiceUnavailableError:
                print(
                    "   *** OpenAI API service unavailable. Waiting 10 seconds and trying again. ***"
                )
                time.sleep(10)  # Wait 10 seconds and try again
                continue
            else:
                break
            
            print(
                "   *** OpenAI API max retries or weird error hit, so bailing on request & returning false."
            )
            return False, 0

