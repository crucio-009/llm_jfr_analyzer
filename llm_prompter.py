import os

def build_prompt(features_summary):
    """
    Prepares LLM prompt text using extracted features.
    """
    prompt = (
        "You are an expert JVM performance and diagnostics assistant. "
        "Review the following summary of Java Flight Recorder (JFR) data, "
        "and list any potential issues, root causes, and actionable recommendations. "
        "Explain your conclusions clearly for a JVM/application engineer.\n\n"
        f"{features_summary}\n\n"
        "What are the JVM performance or stability risks and what should the user look at first?"
    )
    return prompt

def analyze_with_openai_llm(features_summary):
    import openai
    model = os.getenv("LLM_MODEL", "gpt-4")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY is not set in environment.")

    openai.api_key = api_key
    try:
        completion = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You specialize in Java/JVM/JFR diagnostics."},
                {"role": "user", "content": build_prompt(features_summary)}
            ],
            temperature=0.1,
            max_tokens=700
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error communicating with LLM: {e}"

def ensure_local_llm(model_name="google/gemma-2b-it"):
    """
    Checks if the local HuggingFace model is available; if not, downloads it interactively.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    try:
        # Check if model exists locally
        AutoTokenizer.from_pretrained(model_name, local_files_only=True)
        AutoModelForCausalLM.from_pretrained(model_name, local_files_only=True)
        return True
    except Exception:
        print(f"Model '{model_name}' is not downloaded. Downloading now (this may take several minutes and require >2GB disk space)...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
            _ = tokenizer, model  # avoid "unused variable"
            print(f"Model '{model_name}' is now set up locally for offline use.")
            return True
        except Exception as e:
            print(f"Automatic model setup failed: {e}")
            return False

def analyze_with_local_llm(features_summary, model_name="google/gemma-2b-it", max_new_tokens=700):
    """
    Uses a HuggingFace Transformers-powered local LLM for inference (default: Gemma-2b-it).
    Auto-downloads model weights if not already present.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    import torch

    # Ensure model is downloaded
    if not ensure_local_llm(model_name):
        return f"Model '{model_name}' could not be set up. Please check your network and storage."

    device = "cuda" if torch.cuda.is_available() else "cpu"
    prompt = build_prompt(features_summary)
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if device == "cuda" else torch.float32)
        pipe = pipeline(
            "text-generation", model=model, tokenizer=tokenizer, device=0 if device == "cuda" else -1
        )
        res = pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            temperature=0.1,
            truncation=True
        )
        return res[0]["generated_text"].replace(prompt, "").strip()
    except Exception as e:
        return f"Error with local LLM ({model_name}): {e}"

def analyze_with_llm(features_summary):
    """
    Chooses provider (openai or local/transformers) based on environment variable or fallback.
    Ensures local LLMs are set up automatically if not present.
    """
    use_local = os.getenv("USE_LOCAL_LLM", "0").lower() in ("1", "true", "yes")
    if use_local:
        model_name = os.getenv("LOCAL_LLM_MODEL", "google/gemma-2b-it")
        return analyze_with_local_llm(features_summary, model_name=model_name)
    else:
        return analyze_with_openai_llm(features_summary)
