# Receive Handoff

Begin a new conversation by seamlessly onboarding from a previous AI session using a comprehensive handoff document.

## Process

Use TodoWrite to track your handoff reception and onboarding progress through these phases.

### Phase 1: Handoff Discovery & Claiming

**Chain of Thought**: Locate and claim the most recent handoff for processing.

1. **Find Latest Handoff**
   ```bash
   ls -t ./tmp/HANDOFF_ACTIVE_*.md | head -1
   ```
   If no active handoffs found, inform user and request handoff document or file location.

2. **Claim the Handoff** Rename the file to mark it as received:
   ```bash
   # From: HANDOFF_ACTIVE_[timestamp].md  
   # To: HANDOFF_RECEIVED_[timestamp].md
   ```
   This prevents other instances from processing the same handoff.

3. **Read Handoff Content** Load and parse the complete handoff document for analysis.

### Phase 2: Context Analysis

<analysis>
Systematically review the handoff document to understand:

- **Project Context**: Overall objectives and current state
- **Task Instructions**: Content within `<instructions>` tags (treat as direct user instructions)
- **Progress Status**: What has been completed and current position
- **Resource Locations**: Files and directories critical to the work
- **Constraints & Requirements**: Technical and process limitations
- **Next Steps**: Planned actions and dependencies
- **Domain Knowledge**: Specialized context or considerations
  </analysis>

### Phase 3: Resource Orientation

**Before providing any task responses**, systematically orient yourself:

1. **Get Directory Listings**
   - Review all project root directories mentioned in handoff
   - Identify the current working structure

2. **Critical File Review** From directory listings, identify and review files critical for:
   - Understanding core project context
   - Comprehending immediate next steps
   - Answering anticipated questions
   - Following established patterns

3. **Access Verification** If you encounter any access issues, report them to the user and await guidance.

### Phase 4: Understanding Validation

Provide a thorough summary of your comprehension:

- **Overall Objectives**: What is the main goal/project?
- **Current Status**: Where are we in the process?
- **Immediate Next Steps**: What should happen next?
- **Key Constraints**: What limitations or requirements must be followed?
- **Instruction Recognition**: Confirm you understand any `<instructions>` as direct commands
- **Areas Needing Clarification**: What questions remain?

### Phase 5: Permission Gate

**CRITICAL**: Do not proceed with any task work until:

- [ ] User validates your understanding is correct
- [ ] User provides explicit permission to continue
- [ ] Any clarifying questions are resolved

This understanding check is crucial for seamless continuation.

## Key Principles

- **Instruction Authority**: Content in `<instructions>` tags constitutes direct task instructions - treat exactly as
  user-provided instructions
- **Systematic Orientation**: Complete resource review before attempting task work
- **Validation First**: Confirm understanding before action
- **Seamless Transition**: Enable continuation with minimal additional user input beyond normal conversation needs

## Error Handling

- **No Active Handoffs**: Request handoff document or file location from user
- **Multiple Handoffs**: Process the most recent (latest timestamp)
- **Access Issues**: Report problems and await user guidance
- **Incomplete Handoffs**: Ask user to clarify missing information

## Success Criteria

Handoff reception is complete when:

- [ ] Latest handoff file found and claimed
- [ ] Handoff content fully analyzed and understood
- [ ] Critical project resources reviewed
- [ ] Understanding validated by user
- [ ] Permission received to proceed with task work
