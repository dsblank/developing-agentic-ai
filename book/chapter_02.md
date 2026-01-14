# Agentic Systems

Now that we understand the core concepts, let's explore how to build complete agentic systems. This chapter walks through the process of designing, implementing, and deploying agentic AI systems using Opik.

## Building an Agentic System from scratch

Building an agentic system involves combining the core concepts we learned in Chapter 1 into a cohesive, working solution. Let's break down the process into clear steps.

### Step 1: Define the Problem and Scope

Before writing any code, clearly define:

- **What problem** are you solving?
- **What tasks** should the agent be able to perform?
- **What constraints** exist (time, cost, accuracy requirements)?
- **What tools** will the agent need access to?

Example: "Build an agent that helps users research and summarize information from multiple sources, with the ability to search the web, read documents, and synthesize findings."

### Step 2: Design the Agent Architecture

Design your agent's architecture by determining:

**Agent Type**: Will your agent be:

- **Single-turn**: Responds to individual queries independently
- **Multi-turn**: Maintains conversation context across interactions
- **Autonomous**: Works toward goals with minimal human intervention
- **Collaborative**: Works alongside humans, asking for clarification when needed

**Tool Selection**: Identify which tools your agent needs:

- Research tools (web search, database queries)
- Action tools (API calls, file operations)
- Analysis tools (data processing, calculations)
- Communication tools (email, notifications)

**Prompt Strategy**: Plan your prompt structure:

- How will you describe the agent's role?
- What examples will you include?
- How will you format tool descriptions?
- What constraints or guidelines are important?

### Step 3: Implement Core Components

With Opik, you'll implement:

**1. Tool Definitions**

```python
from opik import Tool

@Tool(
    name="web_search",
    description="Search the web for current information on a topic. Returns a list of relevant URLs and snippets."
)
def web_search(query: str, max_results: int = 5) -> dict:
    # Implementation here
    pass
```

**2. System Prompt**
Create a comprehensive system prompt that:

- Defines the agent's role and capabilities
- Lists available tools with clear descriptions
- Provides examples of good behavior
- Sets constraints and safety guidelines

**3. LLM Configuration**
Configure your LLM provider:

- Choose the model (GPT-4, Claude, local model, etc.)
- Set parameters (temperature, max tokens)
- Configure retry logic and error handling

**4. Thread Management**
Set up thread handling for:

- Creating new conversations
- Maintaining context across turns
- Storing session-specific state

### Step 4: Implement the Agent Loop

The core agent loop typically follows this pattern:

1. **Receive Input**: Get user request or task
2. **Build Context**: Assemble system prompt, tool descriptions, conversation history
3. **Generate Response**: Call LLM with full context
4. **Parse Output**: Extract tool calls, reasoning, or direct responses
5. **Execute Tools**: Run any requested tools
6. **Update Context**: Add results to conversation history
7. **Iterate or Respond**: Continue loop if more actions needed, or return final response

### Step 5: Add Observability

Integrate Opik's observability features:

**Trace Collection**: Ensure all agent interactions are traced

```python
from opik import trace

@trace
def agent_process(user_input: str):
    # Agent logic here
    pass
```

**Span Creation**: Create spans for major operations

```python
with span("tool_execution", tool_name="web_search"):
    results = web_search(query)
```

**Metric Tracking**: Track key metrics

```python
from opik import record_metric

record_metric("latency", duration_ms)
record_metric("tool_calls", num_calls)
```

### Step 6: Create Evaluation Datasets

Build datasets to test your agent:

**Test Cases**: Create representative examples covering:

- Common use cases
- Edge cases and error conditions
- Different difficulty levels
- Various input formats

**Expected Outcomes**: Define what success looks like for each test case

**Evaluation Metrics**: Determine how to measure performance (accuracy, completeness, latency, etc.)

### Step 7: Run Experiments and Optimize

Use Opik's experiment framework to:

**Test Variations**: Try different:

- System prompts
- Tool configurations
- LLM parameters
- Model choices

**Compare Results**: Analyze metrics across experiments to identify improvements

**Iterate**: Refine based on results and run new experiments

### Step 8: Deploy and Monitor

Once your agent is performing well:

**Deploy**: Make your agent available to users

- API endpoints
- Web interface
- Integration with existing systems

**Monitor**: Use Opik to track:

- Real-world performance metrics
- Error rates and types
- User satisfaction
- Cost and resource usage

**Improve**: Continuously collect data and iterate based on production usage

## Common Patterns and Architectures

### Pattern 1: Research Agent

A research agent gathers information from multiple sources and synthesizes findings:

**Tools**: Web search, document readers, database queries
**Flow**: Search → Read → Extract → Synthesize → Present
**Key Challenge**: Managing information overload and ensuring accuracy

### Pattern 2: Task Execution Agent

A task execution agent performs specific actions based on user requests:

**Tools**: API integrations, file operations, system commands
**Flow**: Parse request → Plan steps → Execute → Verify → Report
**Key Challenge**: Error handling and rollback capabilities

### Pattern 3: Conversational Assistant

A conversational assistant maintains context and provides helpful responses:

**Tools**: Knowledge base, calculators, formatters
**Flow**: Understand context → Retrieve information → Generate response → Maintain state
**Key Challenge**: Context management and avoiding hallucination

### Pattern 4: Autonomous Agent

An autonomous agent works toward goals with minimal supervision:

**Tools**: Planning tools, execution tools, monitoring tools
**Flow**: Set goal → Plan → Execute → Monitor → Adapt → Complete
**Key Challenge**: Balancing autonomy with safety and control

## Best Practices

### 1. Start Simple

Begin with a minimal viable agent and add complexity gradually. It's easier to debug and understand a simple system.

### 2. Design for Observability

Build tracing and logging into your system from the start. You'll need it for debugging and optimization.

### 3. Test Early and Often

Create test cases and evaluation datasets as you build. Regular testing catches issues before they compound.

### 4. Iterate on Prompts

Prompt engineering is an iterative process. Test different approaches and measure results.

### 5. Handle Errors Gracefully

Agents will encounter errors. Design robust error handling:

- Tool failures
- Invalid inputs
- Timeouts
- Rate limits
- Unexpected outputs

### 6. Set Clear Boundaries

Define what your agent can and cannot do. Clear boundaries prevent misuse and improve reliability.

### 7. Monitor Costs

LLM usage can be expensive. Track token usage and costs, and optimize for efficiency where possible.

### 8. Prioritize User Experience

Technical excellence means little if users can't effectively interact with your agent. Design for clarity and usability.

## Putting It All Together

Building an agentic system is an iterative process:

1. **Prototype**: Build a minimal version quickly
2. **Test**: Evaluate on your dataset
3. **Observe**: Use Opik to understand behavior
4. **Optimize**: Make improvements based on data
5. **Repeat**: Continue the cycle

Each iteration should bring you closer to a production-ready system that solves real problems effectively.

In the next section, we'll explore advanced topics and real-world case studies of agentic systems built with Opik.
