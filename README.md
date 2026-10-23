# Agent Lens integration skill

Record supported agent conversations in **CoreWeave Agent Lens**. This skill inspects your application, selects the matching SDK or plugin, and verifies that turns, model calls, and tool calls appear in the same conversation.

[Choose an Agent Lens integration](https://docs.coreweave.com/products/agent-lens/get-started/integrations?utm_source=github&utm_medium=referral&utm_campaign=agent-lens-integrations-2026q4&utm_content=weave-integration-skills-readme).

## Install and invoke

From your application root, install the skill using its existing repository and identifier, `weave-integration`:

```bash
git clone https://github.com/wandb/weave-integration-skills.git
mkdir -p .claude/skills
cp -r weave-integration-skills/skills/weave-integration .claude/skills/
```

Invoke `@skills weave-integration` in that application. The skill runs only when explicitly invoked.

Example requests:

- “Use weave-integration to add Agent Lens to my Google ADK agent.”
- “Use weave-integration to trace my OpenAI Agents SDK conversation in Agent Lens.”
- “Use weave-integration to verify that my agent's turns and tools are grouped correctly.”

## What the skill does

1. Identify the provider SDK, agent framework, or coding-agent plugin and select its Agent Lens guide.
2. Inspect dependencies and configuration, and prepare an instrumentation plan for review.
3. Apply the approved changes using the package and grouping mechanism documented for that integration.
4. Run a multi-turn example and inspect the resulting conversation in Agent Lens.

The guide determines the required package. Some framework integrations use `weave`; provider SDK integrations use the Forge SDK. A function decorator alone does not establish Agent Lens conversation support.

The skill retains its existing plan and implementation approval steps. Its function-tracing and evaluation references remain available for tasks that explicitly request those workflows.

## Example result

![Google ADK conversation in Agent Lens showing calculator arguments and its result](assets/agent-lens/2026-10/adk-tool-detail.png)

Captured October 22, 2026 with ADK 2.12.0 and `weave` 0.53.12. Model responses are scripted; ADK tool execution, export, and the Agent Lens UI are real. This image demonstrates the ADK example. Validate other integrations with their own guides and runs.

## Documentation

- [Agent Lens integration chooser](https://docs.coreweave.com/products/agent-lens/get-started/integrations)
- [Google ADK guide](https://docs.coreweave.com/products/agent-lens/integrations/google-adk)
- [OpenAI Agents SDK guide](https://docs.coreweave.com/products/agent-lens/integrations/openai-agents-sdk)
- [Inspect conversations](https://docs.coreweave.com/products/agent-lens/conversations/view-activity)

## License

MIT
