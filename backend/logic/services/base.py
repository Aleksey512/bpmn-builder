from typing import Generic, List, NotRequired, Protocol, TypedDict, TypeVar

T = TypeVar("T")


class Xml(TypedDict):
    xml: str


class Suggestion(TypedDict):
    """
    Represents a suggestion with an error and its corresponding correction.

    :key error: The original error string.
    :key correction: The suggested correction.
    """

    error: str
    correction: str


class GenerateResponse(TypedDict, Generic[T]):
    """
    Represents the response returned by the generation API.

    :key model: Model name used.
    :key created_at: Timestamp of generation.
    :key response: The generated response string.
    :key done: Whether generation is complete.
    :key context: List of token IDs from the context.
    :key total_duration: Total generation time in milliseconds.
    :key load_duration: Time taken to load the model.
    :key prompt_eval_count: Number of prompt tokens evaluated.
    :key prompt_eval_duration: Time taken to evaluate prompt.
    :key eval_count: Number of generated tokens.
    :key eval_duration: Time taken to generate tokens.
    """

    model: str
    response: T
    created_at: NotRequired[str]
    done: NotRequired[bool]
    context: NotRequired[List[int]]
    total_duration: NotRequired[int]
    load_duration: NotRequired[int]
    prompt_eval_count: NotRequired[int]
    prompt_eval_duration: NotRequired[int]
    eval_count: NotRequired[int]
    eval_duration: NotRequired[int]


class BpmnService(Protocol):
    """
    Protocol for services that handle Business Process Model and Notation BPMN operation
    using AI-based generation and analysis.

    This interface defines methods for:
    - Checking model readiness
    - Generating BPMN diagrams from text prompts
    - Extracting improvement suggestions from BPMN descriptions

    All methods are asynchronous and intended for use in AI-powered BPMN tooling.

    Methods:
        model_ready() -> bool:
            Checks if the underlying model or service is ready to accept requests.

        generate_bpmn(prompt: str) -> GenerateResponse[Xml]:
            Generates BPMN-compliant XML from a natural language desc of a process.

        get_suggestions(prompt: str) -> GenerateResponse[list[Suggestion]]:
            Analyzes a BPMN description (text or XML) and returns suggested improvements
            or corrections in the form of errors and their corresponding suggestions.
    """

    async def model_ready(self) -> bool:
        """
        Checks if the BPMN generation model is ready.

        :return: True if the model is available and ready to process, otherwise False.
        """
        ...

    async def generate_bpmn(self, prompt: str) -> GenerateResponse[Xml]:
        """
        Generates BPMN XML output from a given prompt.

        :param prompt: Input prompt string.
        :return: A GenerateResponse object containing the generated BPMN XML.
        """
        ...

    async def get_suggestions(self, prompt: str) -> GenerateResponse[list[Suggestion]]:
        """
        Generates suggestions (errors and corrections) from a BPMN diagram prompt.

        :param prompt: Input BPMN XML string or natural language.
        :return: A GenerateResponse containing a list of suggestions.
        """
        ...

    async def create_model(self) -> None: ...
