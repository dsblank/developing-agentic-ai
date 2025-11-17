# Core Concepts

Understanding the fundamental building blocks of agentic AI systems is essential before building complex applications. This chapter introduces the core concepts that form the foundation of Opik and agentic AI development.

## LLM

At the heart of every agentic AI system is a **Large Language Model (LLM)**. LLMs are neural networks trained on vast amounts of text data, enabling them to understand and generate human-like text, reason about problems, and follow instructions.

In the context of agentic systems, LLMs serve as the "brain" that:
- Processes natural language inputs and instructions
- Generates responses and decisions
- Reasons about problems and plans solutions
- Interprets tool outputs and context

When working with Opik, you'll interact with LLMs through various providers (OpenAI, Anthropic, local models, etc.). The LLM receives prompts containing system instructions, tool descriptions, conversation history, and user requests, then generates responses that may include tool calls, reasoning, or direct answers.

## Traces and Spans

**Traces** and **spans** are fundamental concepts for understanding and debugging agentic systems. They provide a hierarchical view of how your agent processes requests and executes actions.

### Traces

A **trace** represents a complete execution of an agentic task from start to finish. It captures the entire lifecycle of a single request or conversation, including:
- The initial user input
- All intermediate reasoning and decisions
- Every tool call and its results
- The final response or outcome

Each trace has a unique identifier and contains metadata such as timestamps, duration, and status (success, failure, timeout, etc.).

### Spans

Each trace is composed of multiple sub-steps called **spans**. A span represents a single unit of work within a trace, such as:
- A single LLM call
- A tool invocation
- A reasoning step
- A data transformation

Spans are organized hierarchically, allowing you to see the complete flow of execution. For example:
- A trace might contain a span for "planning the solution"
- That planning span might contain child spans for "analyzing the problem" and "selecting tools"
- Each tool call becomes its own span with details about inputs, outputs, and execution time

This hierarchical structure makes it easy to:
- **Debug** issues by drilling down into specific spans
- **Profile** performance to identify bottlenecks
- **Understand** agent behavior and decision-making processes
- **Optimize** specific parts of the system

## Thread

A **thread** represents a conversation or session with an agentic system. It maintains the context and history of interactions between a user (or system) and the agent over time.

Key characteristics of threads:
- **Persistent context**: Threads preserve conversation history, allowing agents to reference previous interactions
- **State management**: Threads can maintain state between interactions, such as user preferences or session-specific data
- **Multi-turn conversations**: Threads enable natural back-and-forth interactions where the agent can ask clarifying questions or build upon previous responses

In Opik, threads are essential for:
- Tracking long-running conversations
- Maintaining context across multiple agent invocations
- Grouping related traces together
- Analyzing conversation patterns and user interactions

## Tool

**Tools** are the capabilities that agentic systems use to interact with the world beyond the LLM. A tool is essentially a function that the agent can call to perform actions, retrieve information, or manipulate data.

Common types of tools include:
- **API integrations**: Accessing external services (databases, web APIs, cloud services)
- **File operations**: Reading, writing, and manipulating files
- **Code execution**: Running code in various languages or environments
- **Data processing**: Transforming, analyzing, or querying data
- **System operations**: Interacting with the operating system or infrastructure

In Opik, tools are defined with:
- **Name**: A unique identifier for the tool
- **Description**: Natural language description that helps the LLM understand when and how to use the tool
- **Parameters**: Input schema defining what arguments the tool accepts
- **Implementation**: The actual code or endpoint that executes the tool's functionality

The LLM uses tool descriptions to decide which tools to call and with what parameters, making clear and accurate descriptions crucial for effective agent behavior.

## Metrics

**Metrics** are quantitative measurements that help you understand and improve your agentic systems. They provide insights into performance, quality, cost, and user experience.

Common categories of metrics include:

### Performance Metrics
- **Latency**: Time taken to complete tasks
- **Throughput**: Number of requests processed per unit time
- **Token usage**: Number of tokens consumed by LLM calls
- **Cost**: Financial cost of running the system

### Quality Metrics
- **Accuracy**: Correctness of agent responses
- **Relevance**: How well responses address user needs
- **Completeness**: Whether tasks are fully completed
- **Error rate**: Frequency of failures or incorrect outputs

### Behavioral Metrics
- **Tool usage patterns**: Which tools are used most frequently
- **Reasoning depth**: Number of reasoning steps taken
- **Iteration count**: How many attempts needed to complete tasks
- **User satisfaction**: Feedback scores or ratings

Opik provides built-in support for tracking and analyzing metrics across traces, spans, and experiments, enabling data-driven optimization of your agentic systems.

## Datasets

**Datasets** are collections of test cases, examples, or scenarios used to evaluate and improve agentic systems. A dataset typically contains:
- **Input examples**: Sample user requests or tasks
- **Expected outputs**: Desired responses or outcomes
- **Metadata**: Additional context, difficulty ratings, or categories

Datasets serve multiple purposes:
- **Evaluation**: Testing agent performance on standardized inputs
- **Benchmarking**: Comparing different models, prompts, or configurations
- **Training**: Fine-tuning models or improving prompts
- **Regression testing**: Ensuring changes don't degrade performance

In Opik, datasets can be:
- **Static**: Pre-defined collections of test cases
- **Dynamic**: Generated or sampled from real usage
- **Synthetic**: Artificially created to test specific capabilities
- **Real-world**: Collected from actual user interactions

## Experiments

**Experiments** are systematic tests where you vary one or more aspects of your agentic system to measure the impact on performance. An experiment typically involves:
- **Baseline**: The current system configuration
- **Variations**: Modified versions (different prompts, models, tools, etc.)
- **Evaluation**: Running both on the same dataset
- **Comparison**: Analyzing differences in metrics

Common experiment types include:
- **Prompt engineering**: Testing different system prompts or instructions
- **Model comparison**: Evaluating different LLMs on the same tasks
- **Tool selection**: Comparing different tool configurations
- **Parameter tuning**: Optimizing temperature, max tokens, and other LLM parameters

Opik's experiment framework helps you:
- Run controlled experiments with proper isolation
- Track results and compare configurations
- Identify optimal settings for your use case
- Make data-driven decisions about system improvements

## Prompts

Prompts are the instructions and context provided to LLMs that guide their behavior. In agentic systems, prompts are carefully structured to enable effective tool use, reasoning, and task completion.

### Foundational Prompt

The **foundational prompt** is the base instruction set that defines the agent's core identity, capabilities, and behavioral guidelines. It typically includes:
- The agent's role and purpose
- Core principles and constraints
- General instructions for how to approach problems
- Ethical guidelines and safety considerations

The foundational prompt is usually static and defines the "personality" and fundamental behavior of your agentic system.

### System Prompt

The **system prompt** is the primary instruction set sent to the LLM for each interaction. It combines:
- Elements from the foundational prompt
- Current context and state
- Available tools and their descriptions
- Task-specific instructions

The system prompt is more dynamic than the foundational prompt and may be customized based on the current thread, user context, or specific task requirements.

### Tool Descriptions

**Tool descriptions** are natural language explanations of available tools that help the LLM understand:
- What each tool does
- When to use it
- What parameters it requires
- What it returns

Well-written tool descriptions are critical for effective agent behavior. They should be:
- **Clear and concise**: Easy for the LLM to understand
- **Specific**: Include examples and edge cases
- **Accurate**: Match the actual tool implementation
- **Comprehensive**: Cover all important use cases

### User Prompt

The **user prompt** is the actual request or input from the user (or system) that the agent needs to process. It can be:
- A direct question or instruction
- Part of an ongoing conversation
- A task description
- A combination of text and structured data

The user prompt, combined with the system prompt and conversation history, forms the complete input to the LLM for generating a response.

### Prompt Engineering Best Practices

Effective prompt engineering is crucial for building high-performing agentic systems:

1. **Be explicit**: Clearly state what you want the agent to do
2. **Provide examples**: Include few-shot examples when possible
3. **Structure information**: Use clear formatting and organization
4. **Iterate and test**: Continuously refine prompts based on results
5. **Consider context length**: Balance detail with token efficiency
6. **Test edge cases**: Ensure prompts handle unusual inputs gracefully

In the next chapter, we'll see how these core concepts come together to build complete agentic systems.
