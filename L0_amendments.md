### L0_amendments.md  

**HADES Project Build Amendments**  
_Last Updated: 2025-01-31_  

---

## 📌 Amendment #001 - Removing Manual Tiered Storage, Letting ArangoDB Handle It  

**Status:** Approved for Implementation  
**Date:** 2025-01-31  
**Author:** Project Architect  

### 🔹 Summary of Change  

Originally, HADES implemented a **manual three-tier memory system (Elysium, Asphodel, Lethe)** to optimize knowledge storage and retrieval. **We are now shifting to ArangoDB's built-in optimization mechanisms** and letting it manage data transitions **dynamically**.

### 🔹 Implementation Plan

✅ **Ensure collections are mounted correctly on RAID0 and RAID1.**  
✅ **Modify `arangod.conf` settings to optimize caching & WAL.**  
✅ **Monitor performance after deployment.**  

---

## 📌 Amendment #002 - Expanding Model Hosting Beyond Ollama  

**Status:** Proposed  
**Date:** 2025-01-31  
**Author:** Project Architect  

### 🔹 Summary of Change  

HADES will support **multiple model hosting backends** alongside **Ollama**, including:  
✅ **DeepSpeed** for optimized large-model inference.  
✅ **vLLM** for high-throughput batch inference.  

### 🔹 Implementation Plan  

✅ **Modify Layer 2 to support backend switching dynamically.**  
✅ **Update Fedora 41 installation instructions to include DeepSpeed & vLLM.**  
✅ **Verify performance across different workloads and adjust as needed.**  

---

## 📌 Amendment #003 - Separation of Judgment and Execution for Updates  

**Status:** 🔥 Important (Critical for System Architecture)  
**Date:** 2025-01-31  
**Author:** Project Architect  

### 🔹 Summary of Change  

ModernBERT models (Embedding, Graph, Document) act as **Judges** to determine updates, but **they do not modify the database directly**. Instead, an **Execution Layer** performs updates **only if the Judge rules an update is necessary**.

### 🔹 Implementation Plan  

✅ **Judges evaluate if an update is needed.**  
✅ **Execution Layer performs database updates only when approved.**  
✅ **This prevents unnecessary writes and improves efficiency.**  

---

## 📌 Amendment #004 - Moving Embedding Model Operations to CPU  

**Status:** 🔥 Important (Resource Optimization)  
**Date:** 2025-01-31  
**Author:** Project Architect  

### 🔹 Summary of Change  

All **embedding-related operations** in HADES will be **moved to CPU**, freeing **GPU resources for inference and reasoning models**.

### 🔹 Implementation Plan  

✅ **Ensure embedding inference & fine-tuning run on CPU.**  
✅ **Optimize ArangoDB indexing for CPU-based retrieval.**  
✅ **Automate weekly fine-tuning on CPU to keep retrieval accurate.**  

---

## 📌 Amendment #005 - Using ArangoDB TTL Collections Instead of Redis  

**Status:** 🔥 Important (Simplifies System Design)  
**Date:** 2025-01-31  
**Author:** Project Architect  

### 🔹 Summary of Change  

HADES Judges will store **temporary learning signals & past judgments** inside **ArangoDB’s TTL-based collections** instead of using **Redis**.

### 🔹 Implementation Plan  

✅ **Create a TTL-based cache inside ArangoDB for temporary judge decisions.**  
✅ **Avoid using Redis as an extra dependency.**  
✅ **Ensure ArangoDB’s cache is optimized for fast lookups.**  

## 📌 Amendment #006 - Introducing a 4th Decoder Model for the HADES Frontend  

**Status:** 🔥 Important (Core System Upgrade)  
**Date:** 2025-02-01  
**Author:** Project Architect  

### 🔹 Summary of Change  

HADES requires an additional **4th decoder model** to act as the **frontend interface for all user interactions**.  

- This model will **interpret user input**, classify intent, and route requests appropriately.  
- It will integrate deeply into **Layers 5, 6, and 7** to **handle orchestration, routing, and presentation**.  
- It will also enable **self-aware ECL usage**, ensuring that context retrieval is optimized.

### 🔹 Why This is Necessary  

✅ The **frontend model must dynamically determine when to use an ECL vs. standard retrieval.**  
✅ **Prompt engineering** will allow users to interact with ECLs, triggering playbooks via chat.  
✅ The model ensures **seamless context integration between InCA/ECL and ArangoDB**, maintaining up-to-date knowledge retrieval.

### 🔹 Implementation Plan  

✅ **Embed the 4th decoder model into Layer 5 (Orchestration), Layer 6 (Routing), and Layer 7 (Presentation).**  
✅ **Use prompt engineering to allow system-level commands like "Initiate ECL in this directory."**  
✅ **Integrate the ECL Registry into ArangoDB to track active ECLs and keep it in sync with file system updates.**  
✅ **Develop an automatic syncing mechanism to keep the ECL list updated without manual intervention.**  

---

## 📌 Amendment #007 - Implementing InCA/ECL for Dynamic Knowledge Tracking  

**Status:** 🔥 Important (Enhances Long-Term Learning)  
**Date:** 2025-02-01  
**Author:** Project Architect  

### 🔹 Summary of Change  

The **InCA framework** (In-context Continual Learning Assisted by an External Continual Learner) will be used in HADES to enable dynamic, incremental learning.  

- **ECLs act as metadata-driven "masks"** that refine how knowledge is retrieved and updated, without retraining the model.  
- **Instead of applying ECLs to all knowledge**, only specific domains (like codebases) will have designated ECLs.  
- **The frontend model will dynamically decide when to use an ECL** vs. standard RAG retrieval.

### 🔹 Why This is Necessary  

✅ **Ensures efficient knowledge tracking for specific domains.**  
✅ **Prevents catastrophic forgetting while allowing incremental updates.**  
✅ **Improves query performance by retrieving only the most relevant context dynamically.**  

### 🔹 Implementation Plan  

✅ **Assign ECLs dynamically to specific directories and store metadata in ArangoDB.**  
✅ **Develop a syncing mechanism that updates the ECL list whenever files in an ECL-tracked directory change.**  
✅ **Modify query routing to check if an ECL exists before deciding how to retrieve knowledge.**  
✅ **Enable user interaction via chat-based prompts for managing ECLs.**  

---

## 📌 Build Documents That Require Updates  

### **1️⃣ L5_Orchestration_Layer_Build.md**  

🔹 **What Needs to Be Updated?**  

- Introduce **4th decoder model** to manage **playbooks for ECL setup**.  
- Implement **trigger-based execution**, allowing the model to **run system commands like "Initiate ECL in this directory."**  

---

### **2️⃣ L6_Query_Presentation_Build.md**  

🔹 **What Needs to Be Updated?**  

- Modify query routing logic to **check for active ECLs before running a RAG query.**  
- Introduce **a database-backed registry of all active ECLs, stored in ArangoDB**.  
- Implement **syncing between ECLs and file system updates**.  

---

### **3️⃣ L7_UI_Sessions_Build.md**  

🔹 **What Needs to Be Updated?**  

- Implement **natural language prompts that allow users to interact with the ECL system.**  
- Add **interactive chat-based commands to manage ECLs** (e.g., "List all active ECLs.").  
- Ensure the **frontend can display real-time ECL usage and query routing behavior**.  

---

🔥 **These upgrades will make HADES fully dynamic, allowing it to manage and expand its own knowledge base recursively.** 🚀  
"""
