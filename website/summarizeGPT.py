import requests
import json
from pydantic import BaseModel, Field

OLLAMA_SERVER_URL = "http://192.168.0.135:11434/api/generate"
MODEL_NAME = "gemma3:27b"

class CategoryScores(BaseModel):
    impact_explanation: str
    impact_score: int
    unambiguity_explanation: str
    unambiguity_score: int
    meaningfulness_explanation: str
    meaningfulness_score: int
    unexpectedness_explanation: str
    unexpectedness_score: int
    continuity_explanation: str
    continuity_score: int
    elite_involvement_explanation: str
    elite_involvement_score: int
    negativity_explanation: str
    negativity_score: int
    consonance_explanation: str
    consonance_score: int
    composition_explanation: str
    composition_score: int
    timeliness_explanation: str
    timeliness_score: int

class SummarySchema(BaseModel):
    article_title: str
    category_scores: CategoryScores
    justification: str
    overall_importance_score: float = Field(..., ge=1, le=10)

def getSummary(text):
    schema = SummarySchema.model_json_schema()
    payload = {
        "model": MODEL_NAME,
        "prompt": ('''Analyze the provided article and rate it using the following criteria. 
Each criterion must have an explanation variable before the corresponding score variable.

**Scoring Criteria (Each followed by explanation + score format):**
1. **Impact**: How many people are affected?
   - _impact_explanation: Explanation of the impact.
   - _impact_score: A number from 1-10.

2. **Unambiguity**: Is the event clear and easy to understand?
   - _unambiguity_explanation: Explanation of clarity.
   - _unambiguity_score: A number from 1-10.

3. **Meaningfulness**: Is the event socially, culturally, or politically significant?
   - _meaningfulness_explanation: Explanation of significance.
   - _meaningfulness_score: A number from 1-10.

4. **Unexpectedness**: Is the event surprising?
   - _unexpectedness_explanation: Explanation of surprise factor.
   - _unexpectedness_score: A number from 1-10.

5. **Continuity**: Is this part of an ongoing story?
   - _continuity_explanation: Explanation of continuity.
   - _continuity_score: A number from 1-10.

6. **Elite Involvement**: Does it involve powerful individuals/nations?
   - _elite_involvement_explanation: Explanation of involvement.
   - _elite_involvement_score: A number from 1-10.

7. **Negativity**: Does the event contain crisis, conflict, or disaster?
   - _negativity_explanation: Explanation of negative aspects.
   - _negativity_score: A number from 1-10.

8. **Consonance**: Does it align with existing narratives or audience expectations?
   - _consonance_explanation: Explanation of alignment.
   - _consonance_score: A number from 1-10.

9. **Composition**: Is the event well-balanced among other news topics?
   - _composition_explanation: Explanation of coverage balance.
   - _composition_score: A number from 1-10.

10. **Timeliness**: Is the event recent or still unfolding?
    - _timeliness_explanation: Explanation of recency.
    - _timeliness_score: A number from 1-10.

The **Overall Importance Score** is the average of all category scores. A number between 1 and 10

**Expected JSON Output Format:**
{
  "article_title": "Extracted from input",
  "category_scores": {
    "impact_explanation": "Explanation here",
    "impact_score": X,
    "unambiguity_explanation": "Explanation here",
    "unambiguity_score": X,
    ...
  },
  "justification": "Overall explanation of scoring.",
  "overall_importance_score": X
}\n\nArticle text:'''+ text),
        "stream": False,
        "format": schema  # Ensures structured JSON output
    }

    response = requests.post(OLLAMA_SERVER_URL, json=payload)
    
    try:
        result = response.json()
        
        # Ensure the response is parsed into a dictionary before validation
        parsed_json = json.loads(result.get("response", "{}"))

        summary = SummarySchema.model_validate(parsed_json)
        return summary.dict()
    
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON response from model."}
    except Exception as e:
        return {"error": f"Invalid response from model: {e}"}

# Example usage:
if __name__ == "__main__":
    article_text = '''
    USA: Arrest and Detention of Mahmoud Khalil Is Chilling Attack on Human Rights 
    In response to the Trump administration’s unlawful arrest and detention of Mahmoud Khalil, a lawful permanent resident and recent graduate of Columbia University, Paul O’Brien, Amnesty International USA’s Executive Director, made the following statement: 

    “The arrest and detention of Mahmoud Khalil, a Palestinian student activist and lawful permanent resident, is another attack on human rights by the Trump administration. Each and every one of us – regardless of immigration status – has the right to peaceful assembly, freedom of expression, and due process.  

    “Targeting and threatening peaceful protesters and their immigration status for the content of their protest, such as advocating for the human rights of Palestinians, is a violation of human rights. This targeting sends a chilling message to people across this country, on and off campuses, that anyone exercising their rights will be subject to repression, detention, and possible deportation. And for the immigrant communities already living in fear throughout the U.S., they are now only further pushed into the shadows with fear that they could be deported for speaking out. 

    “Freedom of expression and peaceful assembly are human rights, not grounds for deportation.  

    “The U.S. government must release Mahmoud Khalil immediately. Colleges and universities must also take steps to protect their immigrant students from ICE enforcement and ensure that the human rights of all of their students and faculty to protest in support of Palestinian rights and other issues is respected and protected.” '''
    summary = getSummary(article_text)
    print(summary)
