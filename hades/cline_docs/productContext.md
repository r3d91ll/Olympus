# HADES Product Context

## Purpose
HADES (Heuristic Adaptive Data Extraction System) represents a self-improving knowledge system that learns through guided experience. Using Qwen2.5 as its foundation, HADES maintains a clear separation between procedural knowledge (how to do things, stored in the model through fine-tuning) and reference knowledge (facts and details, stored in ArangoDB). Like a skilled professional, HADES knows both how to work effectively and when to consult its reference materials.

## Problems Solved
1. **Knowledge Separation**: Most systems mix procedural and reference knowledge. HADES clearly separates "knowing how" (fine-tuned expertise) from "knowing what" (ArangoDB reference library).

2. **Self-Guided Learning**: Traditional systems require constant external updates. HADES learns from its own operations, developing expertise through guided experience while maintaining its reference library.

3. **Incremental Improvement**: Many systems need complete retraining. HADES uses LoRA adapters to capture specific skills and expertise incrementally, like a professional developing specialized knowledge.

4. **Practical Experience**: Systems often struggle to convert reference knowledge into practical skills. HADES learns by doing, developing expertise through actual usage while maintaining access to its reference materials.

## Core Functionality
1. **Self-Guided Learning**
   - Learns AQL through documentation and practice
   - Develops expertise through guided experience
   - Creates LoRA adapters for specialized skills

2. **Knowledge Distinction**
   - Fine-tuning captures procedural knowledge
   - ArangoDB stores reference materials
   - Clear separation of skills vs. facts

3. **Recursive Improvement**
   - Uses itself to build its own components
   - Learns from its development process
   - Continuously refines its capabilities

4. **Guided Evolution**
   - Manual oversight of learning process
   - Structured skill development
   - Progressive capability expansion

## Key Innovations
1. **Experience-Based Learning**
   - Learns through practical application
   - Develops expertise over time
   - Maintains reference knowledge separately

2. **Modular Expertise**
   - LoRA adapters capture specific skills
   - Incremental skill development
   - Expertise-focused fine-tuning

3. **Reference Integration**
   - Efficient use of documentation
   - Practical application of knowledge
   - Dynamic knowledge retrieval

## Target Users
1. **AI Trainers**
   - Guiding the learning process
   - Reviewing skill development
   - Structuring learning paths

2. **Knowledge Engineers**
   - Maintaining reference materials
   - Overseeing knowledge organization
   - Validating learned skills

3. **System Architects**
   - Designing learning workflows
   - Managing system evolution
   - Monitoring skill development
