import openai # Or any local/demo AI framework like Ollama / Llama-Edge

def generate_clinical_sql(user_natural_language_query: str) -> str:
    """
    Accepts natural language text and converts it to a SQL query 
    strictly targeting safe MIMIC metadata lookup schemas.
    """
    
    # We pass only the schema of the lookup dictionaries to the AI
    system_prompt = """
    You are a healthcare data engineering assistant. You translate natural language questions into Postgres SQL queries.
    You must only query the following lookup reference tables:
    
    1. d_icd_diagnoses (columns: icd_code, icd_version, long_title)
    2. d_labitems (columns: itemid, label, fluid, category)
    
    Do not reference personal patient information, values, dates, or charts. Return ONLY executable raw SQL text.
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini", # Cost-effective demo model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Translate this request to SQL: {user_natural_language_query}"}
        ],
        temperature=0.0
    )
    
    return response.choices[0].message.content

# Example Simulation
user_prompt = "Find the code for kidney diseases or diabetes diagnoses"
compiled_sql = generate_clinical_sql(user_prompt)
print(f"Generated Clean SQL:\n{compiled_sql}")
