
# This file must never import django stuff.

import openai
import time
import re
from team import secrets

OPENAI_API_KEY=secrets.OPENAI_API_KEY

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

def lookahead_filter(result, prefix, filters):
    print("looking ahead")
    lookahead_n =10 
    i = 0
    n = next(result)
    next_thing = prefix
    while i < lookahead_n and n:
        next_thing += n['choices'][0]['delta']['content']
        i += 1
        n=next(result)
    try:
        next_thing += n['choices'][0]['delta']['content']
    except:
        print(f"no more tokens in lookahead filter")
    #print(f"i is {i} and nextthing is {next_thing}")

    r = '|'.join(filters)
    next_thing = (re.sub(r, '', 
                   next_thing,
                   flags=re.IGNORECASE))
    #print(f"nextthing is now {next_thing}")
    return next_thing


def openai_call(
      prompt: str,
      temperature: float = 0.5,
      max_tokens: int = 100,
      role: str = "system",
      previous_messages: list = None,
      stream = False,
):
        print(f"openai call, stream = {stream}")
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
                    stream=stream,
                )
                
                if stream:
                    for message in response:
                        yield message
                    return

                retval = (re.sub('as an ai language model, |as the ai language model, ', '', 
                               response.choices[0].message.content.strip(), 
                               flags=re.IGNORECASE))
                #response.usage.total_tokens)
                print(f"Returning {retval}")
                yield retval
                return retval
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
            yield False
            return False

def openai_image(prompt):
    max_retries = 5
    failure_return_value = False
    for retries in range(0, max_retries):
        try:
            print(f"openai.Image.create(prompt={prompt},n=1,size='512x512')")
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512"
            )
            print(f"Result of {prompt} is {response}")
            image_url = response['data'][0]['url']
            print("OpenAI made"+ image_url)
            return image_url

        except openai.error.RateLimitError:
            print(f"***Error generating image for {prompt}.")
            print("   *** The OpenAI API rate limit has been exceeded. Waiting 10 seconds and trying again. ***")
            time.sleep(10)  # Wait 10 seconds and try again
            continue
        except openai.error.Timeout:
            print(f"***Error generating image for {prompt}.")
            print("   *** OpenAI API timeout occured. Waiting 10 seconds and trying again. ***")
            time.sleep(10)  # Wait 10 seconds and try again
            continue
        except openai.error.APIError:
            print(f"***Error generating image for {prompt}.")
            print( "   *** OpenAI API error occured. Waiting 10 seconds and trying again. ***")
            time.sleep(10)  # Wait 10 seconds and try again
            continue
        except openai.error.APIConnectionError:
            print(f"***Error generating image for {prompt}.")
            print( "   *** OpenAI API connection error occured. Check your network settings, proxy configuration, SSL certificates, or firewall rules. Waiting 10 seconds and trying again. ***")
            time.sleep(10)  # Wait 10 seconds and try again
            continue
        except openai.error.InvalidRequestError:
            print(f"***Error generating image for {prompt}.")
            print(f"   *** OpenAI API invalid request. Check the documentation for the specific API method you are calling and make sure you are sending valid and complete parameters. Bailing immediately, returning {failure_return_value}. ***")
            return failure_return_value
        except openai.error.ServiceUnavailableError:
            print(f"***Error generating image for {prompt}.")
            print( "   *** OpenAI API service unavailable. Waiting 10 seconds and trying again. ***")
            time.sleep(10)  # Wait 10 seconds and try again
            continue
        else:
            print(f"***FATAL Error generating image for {prompt}.")
            break

