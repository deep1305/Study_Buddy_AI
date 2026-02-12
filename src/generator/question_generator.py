from __future__ import annotations

from typing import Any

# LangChain recently moved some modules into langchain-core.
# Support both import paths to avoid ModuleNotFoundError across versions.
try:
    from langchain.output_parsers import PydanticOutputParser  # type: ignore
except ModuleNotFoundError:  # pragma: no cover
    from langchain_core.output_parsers import PydanticOutputParser  # type: ignore
from pydantic import BaseModel

from src.common.custom_exception import CustomException
from src.common.logger import get_logger
from src.config.settings import settings
from src.llm.client_factory import get_llm
from src.models.question_schemas import FillBlankQuestion, MCQQuestion
from src.prompts.templates import fill_blank_prompt_template, mcq_prompt_template

class QuestionGenerator:
    def __init__(self):
        self.llm = get_llm()
        self.logger = get_logger(self.__class__.__name__)

    def _retry_and_parse(
        self,
        prompt: Any,
        parser: PydanticOutputParser,
        topic: str,
        difficulty: str,
    ) -> BaseModel:
        max_retries = max(1, settings.max_retries)
        last_err: Exception | None = None

        for attempt in range(1, max_retries + 1):
            try:
                self.logger.info(
                    f"Generating question (attempt {attempt}/{max_retries}) "
                    f"topic='{topic}', difficulty='{difficulty}'"
                )

                response = self.llm.invoke(prompt.format(topic=topic, difficulty=difficulty))

                parsed = parser.parse(response.content)

                self.logger.info("Successfully parsed the question")
                return parsed

            except Exception as e:
                last_err = e
                self.logger.error(f"Error generating/parsing question: {e}")

                if attempt == max_retries:
                    raise CustomException(
                        f"Failed to generate question after {max_retries} attempts",
                        last_err,
                    ) from last_err

        # Should never happen due to the return/raise above.
        raise CustomException("Failed to generate question", last_err)

    def generate_mcq(self, topic: str, difficulty: str="medium") -> MCQQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=MCQQuestion)

            question = self._retry_and_parse(mcq_prompt_template, parser, topic, difficulty)
            
            self.logger.info(f"Generated MCQ: {question.question}")

            return question  # type: ignore[return-value]
        
        except Exception as e:
            self.logger.error(f"Error generating MCQ question: {str(e)}")
            raise CustomException("MCQ generation failed", e) from e
    
    def generate_fill_blank(self, topic: str, difficulty: str="medium") -> FillBlankQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)

            question = self._retry_and_parse(fill_blank_prompt_template, parser, topic, difficulty)

            if "_____" not in question.question:
                raise ValueError("Invalid fill blank question: question must contain '_____'")
            
            self.logger.info(f"Generated fill-blank: {question.question}")

            return question  # type: ignore[return-value]
        
        except Exception as e:
            self.logger.error(f"Error generating fill blank question: {str(e)}")
            raise CustomException("Fill blank generation failed", e) from e
    


