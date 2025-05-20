import os
import streamlit as st
import glob
from pathlib import Path

def initialize_llm_settings():
    """Initialize LLM settings in session state if they don't exist"""
    if "llm_provider" not in st.session_state:
        st.session_state.llm_provider = "None"
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""
    if "anthropic_api_key" not in st.session_state:
        st.session_state.anthropic_api_key = ""
    if "local_model_path" not in st.session_state:
        st.session_state.local_model_path = ""
    if "local_models_available" not in st.session_state:
        st.session_state.local_models_available = []

def detect_local_models(model_directory):
    """
    Detect local LLM model files in specified directory
    
    Parameters:
    model_directory: Path to the directory to check for models
    
    Returns:
    list: List of model files found
    """
    if not model_directory or not os.path.exists(model_directory):
        return []
    
    # Common extensions for LLM model files
    extensions = ["*.gguf", "*.bin", "*.onnx", "*.pt", "*.pth", "*.safetensors"]
    
    model_files = []
    for ext in extensions:
        model_files.extend(glob.glob(os.path.join(model_directory, ext)))
    
    # Extract just the filenames without path
    model_names = [Path(path).name for path in model_files]
    return model_names

def render_llm_config_sidebar():
    """
    Render the LLM configuration options in the sidebar
    """
    initialize_llm_settings()
    
    with st.sidebar.expander("🤖 AI Model Configuration"):
        # LLM Provider Selection
        provider_options = ["None", "OpenAI API", "Anthropic API", "Local Model"]
        provider = st.selectbox(
            "Select AI Provider:",
            provider_options,
            index=provider_options.index(st.session_state.llm_provider)
        )
        st.session_state.llm_provider = provider
        
        # Provider-specific settings
        if provider == "OpenAI API":
            openai_key = st.text_input(
                "OpenAI API Key:", 
                type="password",
                value=st.session_state.openai_api_key
            )
            st.session_state.openai_api_key = openai_key
            
            if openai_key:
                st.success("✅ OpenAI API key configured")
                model = st.selectbox(
                    "Select OpenAI Model:",
                    ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
                )
                st.session_state.openai_model = model
            else:
                st.info("Enter your OpenAI API key to use enhanced analytics features")
        
        elif provider == "Anthropic API":
            anthropic_key = st.text_input(
                "Anthropic API Key:", 
                type="password",
                value=st.session_state.anthropic_api_key
            )
            st.session_state.anthropic_api_key = anthropic_key
            
            if anthropic_key:
                st.success("✅ Anthropic API key configured")
                model = st.selectbox(
                    "Select Anthropic Model:",
                    ["claude-3-5-sonnet-20241022", "claude-3-opus", "claude-3-sonnet"]
                )
                st.session_state.anthropic_model = model
            else:
                st.info("Enter your Anthropic API key to use enhanced analytics features")
        
        elif provider == "Local Model":
            local_path = st.text_input(
                "Local Model Directory:", 
                value=st.session_state.local_model_path
            )
            st.session_state.local_model_path = local_path
            
            if local_path and os.path.exists(local_path):
                models = detect_local_models(local_path)
                st.session_state.local_models_available = models
                
                if models:
                    st.success(f"✅ Found {len(models)} local models")
                    selected_model = st.selectbox(
                        "Select Local Model:",
                        models
                    )
                    st.session_state.local_model_selected = selected_model
                else:
                    st.warning("No compatible model files found in the specified directory")
            else:
                st.info("Enter the path to your local models directory")
        
        # Token usage settings
        if provider != "None":
            st.subheader("Token Usage Settings")
            max_tokens = st.slider(
                "Max Tokens per Request:",
                min_value=100,
                max_value=4000,
                value=1000,
                step=100
            )
            st.session_state.max_tokens = max_tokens
            
            enable_caching = st.checkbox("Enable Response Caching", value=True)
            st.session_state.enable_caching = enable_caching
            
            if enable_caching:
                st.info("Caching will help reduce token usage by storing responses")

def get_llm_client():
    """
    Get an LLM client based on the configured provider
    
    Returns:
    client: LLM client object or None if not configured
    """
    provider = st.session_state.get("llm_provider", "None")
    
    if provider == "OpenAI API":
        api_key = st.session_state.get("openai_api_key", "")
        model = st.session_state.get("openai_model", "gpt-4o")
        
        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                return {
                    "client": client,
                    "model": model,
                    "provider": "openai",
                    "max_tokens": st.session_state.get("max_tokens", 1000)
                }
            except ImportError:
                st.warning("OpenAI package not installed. Run 'pip install openai' to install.")
            except Exception as e:
                st.error(f"Error initializing OpenAI client: {str(e)}")
    
    elif provider == "Anthropic API":
        api_key = st.session_state.get("anthropic_api_key", "")
        model = st.session_state.get("anthropic_model", "claude-3-5-sonnet-20241022")
        
        if api_key:
            try:
                from anthropic import Anthropic
                client = Anthropic(api_key=api_key)
                return {
                    "client": client,
                    "model": model,
                    "provider": "anthropic",
                    "max_tokens": st.session_state.get("max_tokens", 1000)
                }
            except ImportError:
                st.warning("Anthropic package not installed. Run 'pip install anthropic' to install.")
            except Exception as e:
                st.error(f"Error initializing Anthropic client: {str(e)}")
    
    elif provider == "Local Model":
        model_path = st.session_state.get("local_model_path", "")
        model_name = st.session_state.get("local_model_selected", "")
        
        if model_path and model_name:
            try:
                # This is a placeholder for local model initialization
                # Actual implementation would depend on the local inference library used
                return {
                    "client": "local",
                    "model": os.path.join(model_path, model_name),
                    "provider": "local",
                    "max_tokens": st.session_state.get("max_tokens", 1000)
                }
            except Exception as e:
                st.error(f"Error initializing local model: {str(e)}")
    
    return None

def analyze_text_with_llm(text, prompt_template, cache_key=None):
    """
    Analyze text using the configured LLM
    
    Parameters:
    text: The text to analyze
    prompt_template: Template for the prompt (text will be inserted)
    cache_key: Optional key for caching the response
    
    Returns:
    str: LLM response or error message
    """
    if not text:
        return "No text provided for analysis"
    
    llm_config = get_llm_client()
    if not llm_config:
        return "LLM not configured. Please set up an AI provider in the sidebar."
    
    # Check cache if enabled
    if st.session_state.get("enable_caching", True) and cache_key:
        cache_dict = st.session_state.get("llm_response_cache", {})
        if cache_key in cache_dict:
            return cache_dict[cache_key]
    
    prompt = prompt_template.replace("{text}", text)
    
    try:
        if llm_config["provider"] == "openai":
            response = llm_config["client"].chat.completions.create(
                model=llm_config["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=llm_config["max_tokens"]
            )
            result = response.choices[0].message.content
        
        elif llm_config["provider"] == "anthropic":
            response = llm_config["client"].messages.create(
                model=llm_config["model"],
                max_tokens=llm_config["max_tokens"],
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.content[0].text
        
        elif llm_config["provider"] == "local":
            # Placeholder for local model inference
            # This would be replaced with actual local inference code
            result = "Local model analysis not yet implemented"
        
        else:
            return "Unknown LLM provider configured"
        
        # Cache the result if caching is enabled
        if st.session_state.get("enable_caching", True) and cache_key:
            if "llm_response_cache" not in st.session_state:
                st.session_state.llm_response_cache = {}
            st.session_state.llm_response_cache[cache_key] = result
        
        return result
    
    except Exception as e:
        return f"Error using LLM for analysis: {str(e)}"