from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from typing import Dict, List
from app.models.task import Task, TaskPriority
import os
from app.core.cache import cache_response
import logging

logger = logging.getLogger(__name__)

PRIORITIZATION_TEMPLATE = """
Du er en erfaren projektleder der skal hjælpe med at prioritere opgaver.
Baseret på følgende opgavedetaljer, foreslå en prioritet (HIGH, MEDIUM, LOW) og forklar hvorfor:

Opgave: {title}
Beskrivelse: {description}
Deadline: {deadline}
Nuværende status: {status}

Overvej følgende faktorer:
1. Tidskritisk (deadline)
2. Kompleksitet (baseret på beskrivelsen)
3. Afhængigheder
4. Forretningsværdi

Giv dit svar i følgende format:
Anbefalet prioritet: [PRIORITY]
Begrundelse: [Din detaljerede forklaring]
"""

class TaskPrioritizationChain:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.3,
            model_name="gpt-3.5-turbo",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.prompt = PromptTemplate(
            template=PRIORITIZATION_TEMPLATE,
            input_variables=["title", "description", "deadline", "status"]
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    @cache_response(expire_time=1800)
    async def get_priority_suggestion(self, task: Task) -> Dict[str, str]:
        try:
            response = await self.chain.arun(
                title=task.title,
                description=task.description or "Ingen beskrivelse",
                deadline=task.deadline.isoformat() if task.deadline else "Ingen deadline",
                status=task.status.value
            )
            
            # Parse response
            lines = [line.strip() for line in response.strip().split("\n") if line.strip()]
            priority = None
            reasoning = None
            
            for line in lines:
                if line.startswith("Anbefalet prioritet:"):
                    priority = line.split(":", 1)[1].strip()
                elif line.startswith("Begrundelse:"):
                    reasoning = line.split(":", 1)[1].strip()
            
            if not priority or not reasoning:
                raise ValueError("Ugyldigt response format fra AI")
                
            return {
                "suggested_priority": priority,
                "reasoning": reasoning
            }
        except Exception as e:
            logger.error(f"Fejl ved AI prioritering: {str(e)}")
            return {
                "suggested_priority": "MEDIUM",
                "reasoning": f"Fejl: Kunne ikke analysere denne opgave ({str(e)})"
            }

    async def batch_prioritize(self, tasks: List[Task]) -> List[Dict[str, str]]:
        results = []
        for task in tasks:
            try:
                suggestion = await self.get_priority_suggestion(task)
                results.append({
                    "task_id": task.id,
                    **suggestion
                })
            except Exception as e:
                logger.error(f"Fejl ved prioritering af task {task.id}: {str(e)}")
                results.append({
                    "task_id": task.id,
                    "suggested_priority": "MEDIUM",
                    "reasoning": "Fejl: Kunne ikke analysere denne opgave"
                })
        return results 