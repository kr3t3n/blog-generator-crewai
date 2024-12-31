from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, WebsiteSearchTool, ScrapeWebsiteTool
from models.content_models import ContentOutput, SocialMediaPost
import json

class ContentCreationCrew:
    """Content Creation Crew for AI Analysis"""

    def __init__(self, agents_config, tasks_config, llm):
        self.agents_config = agents_config
        self.tasks_config = tasks_config
        self.llm = llm
        self._setup_crew()

    def _setup_crew(self):
        """Set up the crew with agents and tasks."""
        # Create agents
        self.market_news_monitor_agent = Agent(
            config=self.agents_config['market_news_monitor_agent'],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            llm=self.llm,
            verbose=True
        )

        self.data_analyst_agent = Agent(
            config=self.agents_config['data_analyst_agent'],
            tools=[SerperDevTool(), WebsiteSearchTool()],
            llm=self.llm,
            verbose=True
        )

        self.content_creator_agent = Agent(
            config=self.agents_config['content_creator_agent'],
            tools=[SerperDevTool(), WebsiteSearchTool()],
            llm=self.llm,
            verbose=True
        )

        self.quality_assurance_agent = Agent(
            config=self.agents_config['quality_assurance_agent'],
            llm=self.llm,
            verbose=True
        )

        # Create tasks
        self.monitor_financial_news_task = Task(
            config=self.tasks_config['monitor_financial_news'],
            agent=self.market_news_monitor_agent
        )

        self.analyze_market_data_task = Task(
            config=self.tasks_config['analyze_market_data'],
            agent=self.data_analyst_agent
        )

        self.create_content_task = Task(
            config=self.tasks_config['create_content'],
            agent=self.content_creator_agent,
            context=[self.monitor_financial_news_task, self.analyze_market_data_task]
        )

        self.quality_assurance_task = Task(
            config=self.tasks_config['quality_assurance'],
            agent=self.quality_assurance_agent,
            output_pydantic=ContentOutput
        )

        # Create crew
        self.crew = Crew(
            agents=[
                self.market_news_monitor_agent,
                self.data_analyst_agent,
                self.content_creator_agent,
                self.quality_assurance_agent
            ],
            tasks=[
                self.monitor_financial_news_task,
                self.analyze_market_data_task,
                self.create_content_task,
                self.quality_assurance_task
            ],
            process=Process.sequential,
            verbose=True
        )

    def _parse_output(self, result):
        """Parse the output into the expected format."""
        try:
            if hasattr(result, 'raw'):
                # If it's a CrewOutput object, try to parse its raw content
                if isinstance(result.raw, str):
                    try:
                        # Try to parse as JSON first
                        data = json.loads(result.raw)
                    except json.JSONDecodeError:
                        # If not JSON, treat as markdown article
                        data = {
                            "article": result.raw,
                            "social_media_posts": [
                                {
                                    "platform": "Twitter",
                                    "content": "Check out our latest article on AI and market trends! #AI #MarketAnalysis"
                                },
                                {
                                    "platform": "LinkedIn",
                                    "content": "We've just published an in-depth analysis of the current market trends in AI. Read more to discover the latest insights and opportunities."
                                }
                            ]
                        }
                else:
                    data = result.raw
            else:
                data = result

            # Create ContentOutput object
            return ContentOutput(**data)
        except Exception as e:
            print(f"Error parsing crew output: {str(e)}")
            # Return a basic ContentOutput as fallback
            return ContentOutput(
                article=str(result),
                social_media_posts=[
                    SocialMediaPost(
                        platform="Twitter",
                        content="Check out our latest article on AI and market trends! #AI #MarketAnalysis"
                    ),
                    SocialMediaPost(
                        platform="LinkedIn",
                        content="We've just published an in-depth analysis of the current market trends in AI. Read more to discover the latest insights and opportunities."
                    )
                ]
            )

    def kickoff(self):
        """Start the content creation process."""
        result = self.crew.kickoff()
        return self._parse_output(result) 