import asyncio
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain import hub

from app.tools.bandit_tool import run_bandit_scan
from app.tools.semgrep_tool import run_semgrep_scan
from app.tools.rag_tool import search_codebase_context
from app.tools.github_tool import get_pr_diff
from app.agents.prompts import REVIEW_SYSTEM_PROMPT

tools = [
    get_pr_diff,
    run_bandit_scan,
    run_semgrep_scan,
    search_codebase_context,
]

llm = ChatOpenAI(model="gpt-4o", temperature=0)
prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=8,
    handle_parsing_errors=True,
)


async def run_code_review(repo: str, pr: int) -> str:
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: executor.invoke({
                "input": f"Review PR #{pr} in repo {repo}"
            })
        )
        return result["output"]
    except Exception as e:
        return f"Review failed: {str(e)}"