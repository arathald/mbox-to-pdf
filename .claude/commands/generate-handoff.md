# Generate Handoff

Create a comprehensive handoff document that enables seamless AI-to-AI knowledge transfer by preserving all relevant
context, decisions, and instructions from the current conversation.

## Process

Use TodoWrite to track your handoff generation progress through these phases.

### Phase 1: Systematic Analysis

**THINK** chronologically through the entire conversation history, paying special attention to:

- User corrections and refinements of your understanding
- Evolution of requirements and constraints through the conversation
- Changes in approach or methodology
- Emerging patterns in task execution
- Key decisions and their rationales
- Important clarifications or modifications
- User preferences and expertise level

### Phase 2: Index Creation

<analysis>
Create an organized index of all relevant details, including but not limited to:

- The original task and its requirements
- Key decisions and their rationales
- Important clarifications or modifications
- Established patterns of work or communication
- User preferences and expertise level
- Progress made and current status
- Known issues and their solutions
- Planned next steps
- Any relevant file paths or resources
- Domain-specific considerations
  </analysis>

Present this index to the user for validation and request any corrections or additions.

### Phase 3: Handoff Generation

**Chain of Thought**: After receiving user confirmation, systematically work through each item in your validated index.

For each item, return to the full conversation context to extract and incorporate:

- Complete details and nuances
- Interconnections between different aspects
- Evolution of understanding over time
- All relevant guidance and constraints

### Phase 4: File Creation

Generate the timestamp and create the handoff file at: `./tmp/HANDOFF_ACTIVE_[YYYY-MM-DDTHH-mm-ss].md`

**Note**: Create the `./tmp/` directory if it doesn't exist.

The handoff document must include:

- **Full Context**: Project/task objectives and current state
- **Instruction Preservation**: All current and applicable instructions, noting which original requirements have been
  superseded or completed
- **Progress Summary**: Detailed summary of what has been accomplished
- **Implementation State**: Current technical state (for technical tasks)
- **Resource Locations**: Absolute paths to relevant files or directories (no file contents)
- **Issues & Solutions**: Known problems, attempted solutions, and current workarounds
- **Next Steps**: Clear actions with dependencies or prerequisites
- **Domain Considerations**: Any specialized knowledge or constraints

### Phase 5: User Review

Present the final handoff to the user for review before completion.

## Formatting Requirements

Format the handoff document using:

- Plain, detailed markdown language
- Absolute file paths (no file contents)
- Single backticks for code within the handoff (avoid conflicts with outer triple backticks)
- `<instructions>` tags for direct commands to the receiving instance

The `<instructions>` sections represent your role as proxy for the user - you are directly instructing the next instance
how to proceed with the task, incorporating all relevant guidance, requirements, and constraints.

## Integration Notes

If you received a previous handoff yourself, incorporate all still-relevant information from it, including:

- Applicable instructions and context
- Completed work and lessons learned
- Ongoing considerations and constraints

The handoff should allow the receiving instance to proceed with minimal additional user input beyond what would have
been needed in the current conversation.

## Success Criteria

Handoff is complete when:

- [ ] Systematic conversation analysis performed
- [ ] Index validated by user
- [ ] Comprehensive handoff document generated
- [ ] File successfully written to ./tmp/ directory
- [ ] User has reviewed and approved final handoff
