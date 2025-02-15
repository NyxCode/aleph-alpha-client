import requests
from typing import List, Optional, Dict

POOLING_OPTIONS = ["mean", "max", "last_token", "abs_max"]

class QuotaError(Exception):
    def __init__(self, *args, **kwargs):            
        super().__init__(*args, **kwargs)
            
class AlephAlphaClient:
    def __init__(self, host, token=None, email=None, password=None):
        if host[-1] != "/": host += "/"
        self.host = host

        assert (token is not None or (email is not None and password is not None))
        self.token = token or self.get_token(email, password)

    def get_token(self, email, password):
        response = requests.post(self.host + "get_token", json={
            "email": email,
            "password": password
        })
        if response.status_code == 200:
            response_json = response.json()
            return response_json["token"]
        else:
            raise ValueError("cannot get token")

    @property
    def request_headers(self):
        return {'Authorization': 'Bearer ' + self.token}

    def complete(self,
                   model: str,
                   prompt: str = "",
                   maximum_tokens: Optional[int] = 64,
                   temperature: Optional[float] = 0.0,
                   top_k: Optional[int] = 0,
                   top_p: Optional[float] = 0.0,
                   presence_penalty: Optional[float] = 0.0,
                   frequency_penalty: Optional[float] = 0.0,
                   repetition_penalties_include_prompt: Optional[bool] = False,
                   use_multiplicative_presence_penalty: Optional[bool] = False,
                   best_of: Optional[int] = None,
                   n: Optional[int] = 1,
                   logit_bias: Optional[Dict[int, float]] = None,
                   log_probs: Optional[int] = None,
                   stop_sequences: Optional[List[str]] = None,
                   tokens: Optional[bool] = False):
        """
        Generates samples from a prompt.

        Parameters:
            model (str, required):
                Name of model to use. A model name refers to a model architecture (number of parameters among others). Always the latest version of model is used. The model output contains information as to the model version.

            prompt (str, optional, default ""):
                The text to be completed. Unconditional completion can be started with an empty string (default). The prompt may contain a zero shot or few shot task.

            maximum_tokens (int, optional, default 64):
                The maximum number of tokens to be generated. Completion will terminate after the maximum number of tokens is reached. Increase this value to generate longer texts. A text is split into tokens. Usually there are more tokens than words. The summed number of tokens of prompt and maximum_tokens depends on the model (for EleutherAI/gpt-neo-2.7B, it may not exceed 2048 tokens).
                
            temperature (float, optional, default 0.0)
                A higher sampling temperature encourages the model to produce less probable outputs ("be more creative"). Values are expected in a range from 0.0 to 1.0. Try high values (e.g. 0.9) for a more "creative" response and the default 0.0 for a well defined and repeatable answer.

                It is recommended to use either temperature, top_k or top_p and not all at the same time. If a combination of temperature, top_k or top_p is used rescaling of logits with temperature will be performed first. Then top_k is applied. Top_p follows last.

            top_k (int, optional, default 0)
                Introduces random sampling from generated tokens by randomly selecting the next token from the k most likely options. A value larger than 1 encourages the model to be more creative. Set to 0 if repeatable output is to be produced.
                It is recommended to use either temperature, top_k or top_p and not all at the same time. If a combination of temperature, top_k or top_p is used rescaling of logits with temperature will be performed first. Then top_k is applied. Top_p follows last.

            top_p (float, optional, default 0.0)
                Introduces random sampling for generated tokens by randomly selecting the next token from the smallest possible set of tokens whose cumulative probability exceeds the probability top_p. Set to 0.0 if repeatable output is to be produced.
                It is recommended to use either temperature, top_k or top_p and not all at the same time. If a combination of temperature, top_k or top_p is used rescaling of logits with temperature will be performed first. Then top_k is applied. Top_p follows last.

            presence_penalty (float, optional, default 0.0)
                The presence penalty reduces the likelihood of generating tokens that are already present in the text. Presence penalty is independent of the number of occurences. Increase the value to produce text that is not repeating the input.

            frequency_penalty (float, optional, default 0.0)
                The frequency penalty reduces the likelihood of generating tokens that are already present in the text. Presence penalty is dependent on the number of occurences of a token.

            repetition_penalties_include_prompt (bool, optional, default False)
                Flag deciding whether presence penalty or frequency penalty are applied to the prompt and completion (True) or only the completion (False)

            use_multiplicative_presence_penalty (bool, optional, default True)
                Flag deciding whether presence penalty is applied multiplicatively (True) or additively (False). This changes the formula stated for presence and frequency penalty. 

            best_of (int, optional, default None)
                Generates best_of completions server-side and returns the "best" (the one with the highest log probability per token). Results cannot be streamed.
                When used with n, best_of controls the number of candidate completions and n specifies how many to return – best_of must be greater than n.
            
            n (int, optional, default 1)
                How many completions to generate for each prompt.

            logit_bias (dict mapping token ids to score, optional, default None)
                The logit bias allows to influence the likelihood of generating tokens. A dictionary mapping token ids (int) to a bias (float) can be provided. Such bias is added to the logits as generated by the model. 

            log_probs (int, optional, default None)
                Number of top log probabilities to be returned for each generated token. Log probabilities may be used in downstream tasks or to assess the model's certainty when producing tokens.

            stop_sequences (List(str), optional, default None)
                List of strings which will stop generation if they're generated. Stop sequences may be helpful in structured texts.

                Example: In a question answering scenario a text may consist of lines starting with either "Question: " or "Answer: " (alternating). After producing an answer, the model will be likely to generate "Question: ". "Question: " may therfore be used as stop sequence in order not to have the model generate more questions but rather restrict text generation to the answers.

            tokens (bool, optional, default False)
                return tokens of completion
        """
        
        # validate data types
        if not isinstance(model, str):
            raise ValueError("model must be a string")
        if not isinstance(prompt, str):
            raise ValueError("prompt must be a string")
        if not (maximum_tokens is None or isinstance(maximum_tokens, int)):
            raise ValueError("maximum_tokens must be an int or None")
        if isinstance(temperature, int):
            temperature = float(temperature)
        if not (temperature is None or isinstance(temperature, float)):
            raise ValueError("temperature must be a float or None")
        if not (top_k is None or isinstance(top_k, int)):
            raise ValueError("top_k must be a positive int or None")
        if isinstance(top_p, int):
            top_p = float(top_p)
        if not (top_p is None or isinstance(top_p, float)):
            raise ValueError("top_p must be a float or None")
        if isinstance(presence_penalty, int):
            presence_penalty = float(presence_penalty)
        if not (presence_penalty is None or isinstance(presence_penalty, float)):
            raise ValueError("presence_penalty must be a float or None")
        if isinstance(frequency_penalty, int):
            frequency_penalty = float(frequency_penalty)
        if not (frequency_penalty is None or isinstance(frequency_penalty, float)):
            raise ValueError("frequency_penalty must be a float or None")
        if not (repetition_penalties_include_prompt is None or isinstance(repetition_penalties_include_prompt, bool)):
            raise ValueError("repetition_penalties_include_prompt must be a bool or None")
        if not (use_multiplicative_presence_penalty is None or isinstance(use_multiplicative_presence_penalty, bool)):
            raise ValueError("use_multiplicative_presence_penalty must be a bool or None")
        if not (best_of is None or isinstance(best_of, int)):
            raise ValueError("best_of must be an int or None")
        if not (n is None or isinstance(n, int)):
            raise ValueError("n must be an int or None")
        if not (logit_bias is None or isinstance(logit_bias, dict)):
            raise ValueError("logit_bias must be a dict or None")
        if logit_bias is not None:
            for k, v in logit_bias.items():
                if not isinstance(k, int):
                    raise ValueError("a key in the logit_bias dict must be an integer")
                if not isinstance(k, float):
                    raise ValueError("a value in the logit_bias dict must be a float")
        if not (log_probs is None or isinstance(log_probs, int)):
            raise ValueError("log_probs must be an int or None")
        if not (stop_sequences is None or isinstance(stop_sequences, list)):
            raise ValueError("stop_sequences must be an list of strings or None")
        if stop_sequences is not None:
            for stop_sequence in stop_sequences:
                if not isinstance(stop_sequence, str):
                    raise ValueError("each item in the stop_sequences list must be a string")
        if not (tokens is None or isinstance(tokens, bool)):
            raise ValueError("tokens must be a bool or None")

        # validate values
        if maximum_tokens is not None:
            if maximum_tokens <= 0:
                raise ValueError("maxiumum_tokens must be a positive integer")
        if top_k is not None:
            if top_k < 0:
                raise ValueError("top_k must be a positive integer, 0 or None")
        if temperature is not None:
            if temperature < 0.0 or temperature > 1.0:
                raise ValueError("temperature must be a float between 0.0 and 1.0")
        if top_p is not None:
            if top_p < 0.0 or top_p > 1.0:
                raise ValueError("top_p must be a float between 0.0 and 1.0")
        if n is not None:
            if n <= 0:
                raise ValueError("top_k must be a positive integer")
        
        if best_of is not None:
            if best_of == n:
                raise ValueError("With best_of equal to n no best completions are choses because only n are computed.")
            if best_of < n:
                raise ValueError(
                    "best_of needs to be bigger than n. The model cannot return more completions (n) than were computed (best_of).")

        payload = {
            "model": model,
            "prompt": prompt,
            "maximum_tokens": maximum_tokens,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "best_of": best_of,
            "n": n,
            "logit_bias": logit_bias,
            "log_probs": log_probs,
            "repetition_penalties_include_prompt": repetition_penalties_include_prompt,
            "use_multiplicative_presence_penalty": use_multiplicative_presence_penalty,
            "stop_sequences": stop_sequences,
            "tokens": tokens,
        }

        response = requests.post(self.host + "complete", headers=self.request_headers, json=payload,
                                 timeout=None)
        return self._parse_response(response)

    def embed(self, model, prompt: str, layers: List[int], tokens: Optional[bool] = False, pooling: List[str] = None):
        """
        Embeds a text and returns vectors that can be used for downstream tasks (e.g. semantic similarity) and models (e.g. classifiers).

        Parameters:
            model (str, required):
                Name of model to use. A model name refers to a model architecture (number of parameters among others). Always the latest version of model is used. The model output contains information as to the model version.

            prompt (str, required):
               The text to be embedded.

            layers (List[int], required):
               A list of layer indices from which to return embeddings. 
                    * Index 0 corresponds to the word embeddings used as input to the first transformer layer
                    * Index 1 corresponds to the hidden state as output by the first transformer layer, index 2 to the output of the second layer etc. 
                    * Index -1 corresponds to the last transformer layer (not the language modelling head), index -2 to the second last layer etc.
        
            tokens (bool, optional, default False)
                Flag indicating whether the tokenized prompt is to be returned (True) or not (False)

            pooling (List[str] optional, default None)
                Pooling operation to use. No pooling is used (an embedding per input token is returned) if None. 

                Pooling operations include:
                    * mean: aggregate token embeddings across the sequence dimension using an average
                    * max: aggregate token embeddings across the sequence dimension using a maximum
                    * last_token: just use the last token
                    * abs_max: aggregate token embeddings across the sequence dimension using a maximum of absolute values
        """

        if not isinstance(model, str):
            raise ValueError("model must be a string")

        if not isinstance(prompt, str):
            raise ValueError("prompt must be a string")
        
        if len(prompt) == 0:
            raise ValueError("prompt must contain at least one character")

        if not isinstance(layers, list):
            raise ValueError("layers must be a list")
        
        if len(layers) == 0:
            raise ValueError("layers must contain at least one layer")

        for layer in layers:
            if not isinstance(layer, int):
                raise ValueError("each item in the layers list must be an integer; got "+str(layer))

        if tokens is None:
            tokens = False
        if not isinstance(tokens, bool):
            raise ValueError("tokens must be a bool")

        if not pooling is None and not isinstance(pooling, list):
            raise ValueError("pooling must be None or a list")

        if pooling is not None:
            for pooling_option in pooling:
                if pooling_option not in POOLING_OPTIONS:
                    raise ValueError("each item in the pooling list must be either one of "+str(POOLING_OPTIONS)+"; got "+str(pooling_option))

        payload = {
            "model": model,
            "prompt": prompt,
            "layers": layers,
            "tokens": tokens,
            "pooling": pooling,
        }
        response = requests.post(self.host + "embed", headers=self.request_headers, json=payload)
        return self._parse_response(response)

    def evaluate(self, model, completion_expected, prompt=""):
        """
        Evaluates the model's likelihood to produce a completion given a prompt.

        Parameters:
            model (str, required):
                Name of model to use. A model name refers to a model architecture (number of parameters among others). Always the latest version of model is used. The model output contains information as to the model version.

            completion_expected (str, required):
                The ground truth completion expected to be produced given the prompt. 

            prompt (str, optional, default ""):
                The text to be completed. Unconditional completion can be used with an empty string (default). The prompt may contain a zero shot or few shot task.
        """

        if not isinstance(model, str):
            raise ValueError("model must be a string")

        if not isinstance(prompt, str):
            raise ValueError("prompt must be a string")

        if not isinstance(completion_expected, str):
            raise ValueError("completion_expected must be a string")

        if len(completion_expected) == 0:
            raise ValueError("completion_expected cannot be empty")

        payload = {
            "model": model,
            "prompt": prompt,
            "completion_expected": completion_expected,
        }
        response = requests.post(self.host + "evaluate", headers=self.request_headers, json=payload)
        return self._parse_response(response)

    @staticmethod
    def _parse_response(response):
        if response.status_code == 200:
            return response.json()
        else:
            if response.status_code == 400:
                raise ValueError(response.status_code, response.json())
            elif response.status_code == 401:
                raise PermissionError(response.status_code, response.json())
            elif response.status_code == 402:
                raise QuotaError(response.status_code, response.json())
            elif response.status_code == 408:
                raise TimeoutError(response.status_code, response.json())
            else:
                raise RuntimeError(response.status_code, response.json())
