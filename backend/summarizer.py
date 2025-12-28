def simple_summarize(text):
    # For now, let's just grab the first two sentences as a 'summary'
    # We will replace this with Ollama/AI later!
    sentences = text.replace("summarize", "").strip().split('.')
    summary = ". ".join(sentences[:2])
    return f"📝 Here is a quick summary: {summary}..."