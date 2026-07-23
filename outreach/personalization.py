import google.generativeai as genai
import config

def generate_personalized_line(buyer_name, company_name, country, platform):
    """
    Use Gemini to generate a single personalized icebreaker sentence for the email.
    Falls back to a dynamic template-based sentence if the Gemini key is missing or fails.
    """
    api_key = config.GEMINI_API_KEY
    buyer_name = buyer_name or "Wellness Partner"
    company_name = company_name or "Wellness Center"
    country = country or "Global"
    platform = platform or "Web Search"
    
    if not api_key or api_key == 'your_gemini_api_key_here':
        return f"I came across {company_name} on {platform} and was very impressed by your dedication to wellness and sound healing in {country}."
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
You are writing a cold sales email to a prospective wellness buyer.
Create a single, natural-sounding introductory sentence (max 20 words) as an icebreaker.
The buyer's details are:
- Name: {buyer_name}
- Company: {company_name}
- Country/Location: {country}
- Discovered on: {platform}

Context: We are pitching high-quality handcrafted Himalayan Singing Bowls from Kathmandu.
Instructions:
- Reference their business, platform, or location organically (e.g. "I saw your yoga studio on Facebook...", "I noticed your wellness work in Hamburg...").
- Keep it polite, conversational, and direct.
- Return ONLY the single sentence. Do not include any quotes, markdown formatting, or notes.
"""
        response = model.generate_content(prompt)
        line = response.text.strip().replace('"', '').replace("'", "")
        return line
    except Exception as e:
        print(f"Personalization error: {e}. Using fallback.")
        return f"I came across {company_name} on {platform} and was very impressed by your dedication to wellness and sound healing in {country}."
