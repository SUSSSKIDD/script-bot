from google import genai
from google.genai import types

from config import GENERATION_MODEL, TOP_K_RESULTS
from embeddings import query_similar_scripts


def _build_prompt(reference_scripts, user_inputs):
    refs_block = ""
    for i, script in enumerate(reference_scripts, 1):
        refs_block += f"\n--- REFERENCE SCRIPT {i} ---\n{script}\n"

    return f"""You are an expert Instagram Reels scriptwriter for educational content about studying Masters abroad.

Below are {len(reference_scripts)} reference scripts that demonstrate the exact tone, structure, and style you must follow:
{refs_block}
STUDY THESE SCRIPTS CAREFULLY. Learn:
- How hooks grab attention in the first 2 seconds
- The conversational, relatable tone (first person, like talking to a friend)
- How problems are framed as common student anxieties with specific details
- How solutions are detailed and comprehensive, listing out specific strategies and information
- The overall length and depth of each section

NOW GENERATE a new Instagram Reels script with these details:

- Person's Name: {user_inputs['name']}
- Masters College: {user_inputs['college']}
- Field of Study: {user_inputs['field']}
- Current Situation: {user_inputs['situation']}
- Topic/Title: {user_inputs['topic']}

OUTPUT FORMAT — Write the FULL script text under each heading. Match the length and detail level of the reference scripts above. Do NOT summarize or shorten.

Hook:
Write a bold, attention-grabbing opening line in first person. 1-2 sentences. Example style: "I am doing my masters from [college] and here's what nobody will tell you"

Intro:
Write a warm personal introduction. Mention their name, what they're studying, where. Share that the journey required proper planning. 2-3 sentences in first person.

Problem:
Write about the overwhelming confusion they faced — specific questions about applications, costs, exams, job prospects. Make it relatable with real concerns students have. 3-4 sentences.

Solution:
Write a detailed breakdown of what they built/learned — university shortlisting, exam strategies, application checklists, cost breakdowns, career pathways. Be specific and list multiple points. This should be the longest section. 4-6 sentences.

IMPORTANT RULES:
- Write the ACTUAL script dialogue, not a summary or outline
- Write in first person as if {user_inputs['name']} is speaking directly to camera
- Keep it conversational and authentic, not salesy
- Match the tone, length, and detail level of the reference scripts exactly
- Do NOT output sentence counts, bullet points, or meta-commentary
- Do NOT write things like "[Hook: 1 sentence]" — write the actual spoken words
- Output ONLY the script with section headings, nothing else"""


def generate_script(user_inputs, api_key):
    try:
        query_text = (
            f"{user_inputs['name']} studying {user_inputs['field']} "
            f"at {user_inputs['college']}, {user_inputs['situation']}. "
            f"Topic: {user_inputs['topic']}"
        )
        references = query_similar_scripts(query_text, api_key, top_k=TOP_K_RESULTS)

        if not references:
            return "Error: No reference scripts found. Please add PDF scripts to the scripts/ folder and restart."

        prompt = _build_prompt(references, user_inputs)

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GENERATION_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.8,
                max_output_tokens=2048,
            ),
        )
        return response.text

    except Exception as e:
        error_msg = str(e)
        if "block" in error_msg.lower() or "safety" in error_msg.lower():
            return "Error: Generation was blocked by safety filters. Try rephrasing your inputs."
        return f"Error generating script: {error_msg}"
