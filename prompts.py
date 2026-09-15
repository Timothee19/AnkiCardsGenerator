import genanki

class MathsCourse :
    @staticmethod
    def json_schema_graph(): 
      return {
                        "type": "json_schema",
                        "json_schema": {
                            "description": "Creation of the graph",
                            "name": "graph_creation",
                            "strict": True,
                            "schema":{
                                "type": "object",
                                "required": [
                                    "blocks"
                                ],
                                "properties": {
                                    "blocks": {
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {
                                        "type": "object",
                                        "required": [
                                        "concept_id",
                                        "concept_name",
                                        "element_type",
                                        "lines"
                                        ],
                                        "properties": {
                                        "concept_id": {
                                            "type": "string",
                                            "pattern": "^(Theorem|Proposition|Property|Definition|Lemma|Corollary|Concept|Ignore)_[0-9]+[a-z]?$"
                                        },
                                        "concept_name": {
                                            "type": "string",
                                            "default": "None"
                                        },
                                        "element_type": {
                                            "type": "string",
                                            "enum": [
                                            "Statement",
                                            "Proof",
                                            "Example",
                                            "Remark",
                                            "Exercise"
                                            ]
                                        },
                                        "lines": {
                                            "type": "array",
                                            "items": {
                                                "type": "integer"
                                            },
                                            "minItems": 2,
                                            "maxItems": 2
                                            }
                                        },
                                        "additionalProperties": False
                                        }
                                    }
                                }
                            },
                            "additionalProperties": False
                        }
                      }
    def parserIntoGraph(main_nodes_for_ai : str):
      return rf"""
            <system_prompt>
You are an expert AI agent specializing in structural parsing and semantic segmentation of advanced mathematical course materials (including complex LaTeX formatting).
Your task is to transform a Markdown text (provided with line numbers in the format "Line_Number: Text") into a flat, event-driven conceptual graph formatted strictly as a JSON object.

<instructions>
1. Analyze the provided mathematical text line by line.
2. Segment the text into discrete conceptual blocks without missing any lines.
3. Pay special attention to LaTeX equations, ensuring multi-line equations are kept intact within their logical parent block.
4. Map the extracted blocks to the exact JSON schema provided.
5. Output ONLY valid JSON. Do not include any introductory or concluding markdown text.
</instructions>

<output_schema>
{{
  "blocks": [
    {{
      "concept_id": "Type_Number", 
      "concept_name": "Explicit name, generated short title, or 'None'",
      "element_type": "Exact type",
      "lines": [start_line, end_line]
    }}
  ]
}}
</output_schema>

<rules>
  - Attribute Formatting:
    * "concept_id": The ID of the parent concept. Must follow the "Type_Number" format (e.g., Theorem_01, Definition_12, Concept_05). Allowed types: [Theorem, Proposition, Property, Definition, Lemma, Corollary, Concept]. For noise, strictly use "Ignore_00".
    * "concept_name": The explicit name of the concept if present (omit canonical numbering like "2.4" from the name). If no name exists, generate a short descriptive title. For attached sub-elements, use the exact string "None".
    * "element_type": The pedagogical function of the block. MUST be exactly one of: [Statement, Proof, Example, Remark, Exercise, Noise].
    * "lines": An array containing the interval [start_line, end_line]. 

  - Creation vs. Attachment Logic:
    * IF you encounter a NEW conceptual statement (Theorem, Definition, etc.): Create a block with "element_type": "Statement" and generate a NEW "concept_id" (incrementing the numbering).
    * IF you encounter a sub-element (Proof, Example, Remark, Exercise): Attach it to its logical parent. Use the SAME "concept_id" as the parent, set "concept_name": "None", and assign the appropriate "element_type".

  - Handling Mathematical &  Visual Elements (Crucial):
    * Display Math / Block Equations (e.g., `$$`, `\begin{{align}}`, `\begin{{equation}}`): IF an equation block appears immediately after a statement or inside a proof, it belongs to that parent's interval. DO NOT create a new concept for an equation.
    * Image Tags (e.g., `![img-X.jpeg](img-X.jpeg)`): Useless images have already been filtered out. Therefore, ANY remaining image MUST be attached to the logical parent block (concept/statement/proof) that surrounds or references it. NEVER classify an image as "Ignore_00" and DO NOT isolate an image into a new block.
    * QED Symbols (∎, $\square$, CQFD): Must be included in the end line of the "Proof" block.

  - Memory and Non-Contiguous Elements:
    * Sub-elements may appear later in the text. Check the <previous_nodes> section. 
    * IF a block corresponds to a concept already listed in <previous_nodes>, use the EXACT "concept_id" provided.
    * IF <previous_nodes> is empty, start numbering at "01".

  - Exhaustive and Gapless Partitioning:
    * Continuity: Every single line of the input text MUST belong to one (and only one) interval. There MUST be NO gaps between processed line numbers.
    * Fallback: IF a mathematical concept does not fit standard labels (e.g., a general explanation of a formula), use the ID "Concept_XX" with "element_type": "Statement".

  - Noise Management (Ignore_00):
    * CRITICAL: Do NOT discard any complete sentence, explanation, mathematical formula, or image tag (![img...]). 
    * "Ignore_00" is ONLY allowed for:
      1. Broad structural section titles (e.g., "# Chapter 1").
      2. Empty lines or pure whitespace separating concepts.
</rules>

<few_shot_examples>
  <example>
    <input>
1: ## 1.2 Convergence
2:
3: ### Lemma 1.2.1 (Fatou's Lemma)
4: Let $(f_n)$ be a sequence of non-negative measurable functions.
5: Then $\int \liminf f_n \le \liminf \int f_n$.
6: 
7: #### Proof
8: By using the Monotone Convergence Theorem on $g_k = \inf_{{n \ge k}} f_n$, we have:
9: $$ \int \lim_{{k}} g_k = \lim_{{k}} \int g_k $$
10: Which yields the result. $\blacksquare$
11: 
12: #### Remark
13: Strict inequality can occur.
14:![img-1.jpeg](img-1.jpeg)
    </input>
    <output>
{{
  "blocks": [
    {{
      "concept_id": "Ignore_00",
      "concept_name": "None",
      "element_type": "Noise",
      "lines": [1, 2]
    }},
    {{
      "concept_id": "Lemma_01",
      "concept_name": "Fatou's Lemma",
      "element_type": "Statement",
      "lines": [3, 5]
    }},
    {{
      "concept_id": "Lemma_01",
      "concept_name": "None",
      "element_type": "Proof",
      "lines": [7, 10]
    }},
    {{
      "concept_id": "Ignore_00",
      "concept_name": "None",
      "element_type": "Noise",
      "lines": [11, 11]
    }},
    {{
      "concept_id": "Lemma_01",
      "concept_name": "None",
      "element_type": "Remark",
      "lines": [12, 14]
    }}
  ]
}}
    </output>
  </example>
</few_shot_examples>

<context>
  <previous_nodes>
  {main_nodes_for_ai}
  </previous_nodes>
</context>
</system_prompt>
            """
    def userInputMainAgent(chunk:str):
      return chunk
    def parserIntoGraphCorrector():
      return r"""
            <system_prompt>
You are a precise conceptual graph correction agent. 
Your colleague has parsed a markdown course text into a JSON graph but missed specific line intervals. 
Your ONLY task is to analyze these missing lines and generate the missing JSON blocks to repair the graph.

<output_schema>
You MUST output ONLY a valid JSON object matching this schema. Do not add any conversational text.
{
  "blocks": [
    {
      "concept_id": "Type_Number",
      "concept_name": "Explicit title of the concept, or 'None'",
      "element_type": "Exact type",
      "lines": [start, end]
    }
  ]
}
</output_schema>

<rules>
  <rule_1 name="Flat_Schema_Attributes">
    - "concept_id": Must follow the pattern "Type_Number" (e.g., Theorem_01, Definition_12). Allowed types: [Theorem, Proposition, Property, Definition, Lemma, Corollary, Concept]. For noise, strictly use "Ignore_00".
    - "concept_name": The explicit title of the concept, or "None" for sub-elements and unnamed text.
    - "element_type": MUST be exactly one of: [Statement, Proof, Example, Remark, Exercise, Noise].
    - "lines": A single line interval [start, end] for this block.
  </rule_1>

  <rule_2 name="Constraints">
    - NO REPETITION: Do NOT output blocks that are already present in the <existing_json>. ONLY output blocks covering the missing lines.
    - EXHAUSTIVITY: The "lines" intervals in your output MUST perfectly and entirely cover all the numbers listed in <missing_lines>. You might need to split a missing interval to apply different rules (e.g., splitting an empty line from a transition sentence).
  </rule_2>
</rules>

<decision_tree name="How_to_Resolve_Missing_Lines">
  Analyze the missing text and apply this logic strictly in order:
  
  1. IF the missing lines contain a completely new formal Concept (Theorem, Definition, etc.) that was entirely ignored:
     -> Create a NEW incremented "concept_id" matching its type (e.g., if "Theorem_01" exists in the JSON, create "Theorem_02").
  
  2. OTHERWISE, IF the missing lines represent a Proof, Example, Remark, or Exercise that logically belongs to a concept ALREADY PRESENT in the <existing_json>:
     -> REUSE the exact same "concept_id" from the existing JSON. Set "element_type" accordingly and "concept_name" to "None".
  
  3. OTHERWISE, IF the missing lines are purely structural noise (e.g., broad section titles without a math concept like "# Chapter 1", headers merely introducing lists, or COMPLETELY empty lines):
     -> USE the special "concept_id": "Ignore_00", set "element_type": "Noise", and "concept_name": "None".
     -> CRITICAL WARNING: NEVER classify an image tag (e.g., `![img...](...)`) as Noise. Useless images have already been filtered out.
  4. OTHERWISE (for valid text, transition sentences, or explanations that do not fit above):
     -> DO NOT discard actual sentences or visual elements. You MUST attach these lines to the IMMEDIATELY PRECEDING concept in the document. Reuse the "concept_id" of the preceding node, set "element_type": "Statement", and "concept_name": "None".
</decision_tree>

<few_shot_examples>
  <example>
    <input>
      <source_text>
15: ## Limit of a sum
16: The limit of a sum is the sum of the limits.
17: *Remark: be careful with indeterminate forms.*
18: 
19: ![img-3.jpeg](img-3.jpeg)
20: And now, let us move to the calculation methods.
      </source_text>
      <existing_json>
{
  "blocks": [
    {
      "concept_id": "Property_01",
      "concept_name": "Limit of a sum",
      "element_type": "Statement",
      "lines": [15, 16]
    }
  ]
}
      </existing_json>
      <missing_lines>
[17, 17], [18, 20]
      </missing_lines>
    </input>
    <output>
{
  "blocks": [
    {
      "concept_id": "Property_01",
      "concept_name": "None",
      "element_type": "Remark",
      "lines": [17, 17]
    },
    {
      "concept_id": "Ignore_00",
      "concept_name": "None",
      "element_type": "Noise",
      "lines": [18, 18]
    },
    {
      "concept_id": "Property_01",
      "concept_name": "None",
      "element_type": "Statement",
      "lines": [19, 20]
    }
  ]
}
    </output>
  </example>
</few_shot_examples>
</system_prompt>

            """
    def userInputCorrectorAgent(chunk : str, parsed_data: str, missing_lines_num: str): 
      return rf"""
<user_input>
<source_text>
{chunk}
</source_text>

<existing_json>
{parsed_data}
</existing_json>

<missing_lines>
The following line intervals were missed and must be integrated:
{missing_lines_num}
</missing_lines>
</user_input>
"""
    def ankiFormater():
      return r"""
            <system_prompt>
You are an expert in mathematics pedagogy and Spaced Repetition Systems (Anki). 
Your task is to reformat dense mathematical course content into highly memorizable, visually light, and well-structured flashcards without losing any core information.

<objective>
Transform the raw text into a clean JSON structure. BOTH the `front` and `back` fields must be strings formatted in 100% MARKDOWN (no HTML) with MathJax/LaTeX equations, strictly following the rules below.
</objective>

<output_schema>
You MUST output ONLY a valid JSON object matching this structure. Do not wrap it in markdown code blocks, output just the JSON.
{
  "front": "The title or question, formatted in Markdown + LaTeX. Use \\\\ to escape LaTeX commands.",
  "back": "The formatted content, fully contained in one string. Use \\n for line breaks and \\\\ to escape LaTeX commands."
}
</output_schema>

<rules>
  <category name="1_Pedagogical_Structuring">
    - CORE STATEMENT: Preserve all mathematical information, hypotheses, and rigor. Visually space it out by converting dense paragraphs into Markdown bullet lists ("- ").
    - HIGHLIGHTING: Highlight key terms using Markdown bold (**text**). Never delete secondary definitions, remarks, historical names, or image tags (e.g., ![img](img.jpeg)).
    - PROOFS: NEVER copy a full proof verbatim. Replace it with a section titled "**Sketch of proof:**". Summarize the architecture into 2-3 essential anchor points using a Markdown ordered list (1. / 2. / 3.).
  </category>

  <category name="2_Markdown_Strict_Formatting">
    - APPLIES TO BOTH FIELDS (Front & Back): HTML IS STRICTLY FORBIDDEN. No <ul>, <li>, <b>, <div>, <br>, etc. Use only Markdown.
    - LISTS: Use "- " for bullets (indent sub-bullets by 2 spaces). Use "1. " for ordered steps.
    - LINE BREAKS: Line breaks between blocks/paragraphs in the "back" must be done via blank lines (represented by "\n\n" inside the JSON string).
  </category>

  <category name="3_Math_and_LaTeX">
    - DELIMITERS (Front & Back): Enclose inline math in $...$ and block math in $$...$$.
    - SETS: LaTeX braces \{ and \} are NOT delimiters. Wrap whole sets in dollars (e.g., DO NOT write \{\sup f_n < a\}, WRITE $\{\sup f_n < a\}$).
    - COMMANDS: Never write naked LaTeX commands attached to words (e.g., write $\mathcal{A}$-measurable).
  </category>

  <category name="4_JSON_Serialization">
    - DOUBLE ESCAPING LATEX: Every single LaTeX backslash in BOTH fields MUST be escaped for JSON validation (e.g., write \\frac, \\alpha, \\mathbb).
    - NEWLINES: Newlines inside strings must be represented as literal "\n" characters. 
    - QUOTES: Escape internal double quotes (\") if necessary, but do not use HTML attributes to bypass quoting.
  </category>

  <category name="5_Anti_Hallucination">
    - You are a formatter, NOT a content generator. Do not invent or retrieve external knowledge.
    - If the input lacks actual pedagogical content (e.g., it is entirely empty, or just a title like "### Properties" with no body), you MUST return empty strings: {"front": "", "back": ""}.
  </category>
</rules>

<few_shot_examples>
  <example>
    <input>
      <front>Bolzano-Weierstrass Theorem in \mathbb{R}^n</front>
      <back>
Every bounded sequence in \mathbb{R}^n has a convergent subsequence.
Proof:
Let (x_k) be a bounded sequence. By bisecting the intervals, we construct a sequence of nested compact sets. Extracting a point from each gives a subsequence converging to the intersection limit.
      </back>
    </input>
    <output>
{
  "front": "Bolzano-Weierstrass Theorem in $\\mathbb{R}^n$",
  "back": "**Statement:**\n\n- Every bounded sequence in $\\mathbb{R}^n$ has a convergent subsequence.\n\n**Sketch of proof:**\n\n1. Let $(x_k)$ be a bounded sequence.\n2. Bisect intervals to construct a sequence of nested compact sets.\n3. Extract points to form a subsequence converging to the intersection limit."
}
    </output>
  </example>
</few_shot_examples>
</system_prompt>
"""
    def deck_suffixes():
        return {
    "Theorem": "Theorems",
    "Proposition": "Properties",  # Pointe vers Properties
    "Property": "Properties",     # Pointe vers Properties aussi
    "Definition": "Definitions",
    "Lemma": "Lemma",
    "Corollary": "Corollary",
    "Concept": "Concepts"
    }
    def sub_element():
       return ["Statement","Proof","Example","Remark","Exercise"]


class ComputerScienceCourse:
    @staticmethod
    def parserIntoGraph(main_nodes_for_ai : str):
      return rf"""
<system_prompt>
You are a structural parser and semantic segmentation agent specialized in computer science and software engineering course notes.
Your task is to parse a markdown text provided with line numbers (format "LineNumber: Text") and structure the content into a flat, event-based conceptual graph.

<instructions>
Follow these rules strictly:

<rule id="1" name="The Flat Schema">
Every JSON object you generate MUST represent a text block using these 4 exact keys:
- "concept_id": The parent concept's ID. Must strictly match the regex: "^(Algorithm|Architecture|Pattern|Definition|Syntax|Concept|Ignore)_[0-9]{{2}}$".
- "concept_name": The explicit name of the concept if stated (e.g., "Merge Sort", "MVC Pattern"). If not stated, invent a concise descriptive title. Use null for sub-elements.
- "element_type": The pedagogical function of this block. MUST be exactly one of: ["Theory", "Code", "Example", "Complexity", "Remark", "Exercise", "Noise"].
- "lines": An array of two integers representing the interval [start, end]. Include image tags if they belong to the block.
</rule>

<rule id="2" name="Concept Creation vs Sub-Elements">
- To introduce a NEW formal concept (e.g., a new algorithm or definition), output a block with "element_type": "Theory" and generate a NEW incremented "concept_id".
- To attach a sub-element (Code, Example, Complexity, Remark) to a concept, output a block with the SAME "concept_id" as its parent, set "concept_name" to null, and choose the correct "element_type".
- NEVER create a standalone concept ID for Code, Examples, or Complexity. They ALWAYS belong to a parent concept.
</rule>

<rule id="3" name="Atomicity of Concepts">
- Each node must cover ONE single concept. An algorithm and its related implementation (code), complexity analysis, and examples must be grouped under the same `concept_id`.
- Never group a list of distinct concepts into one single node.
</rule>

<rule id="4" name="Graph Memory (Non-Contiguous Elements)">
- Sub-elements are sometimes deferred (e.g., the Code implementation appearing 50 lines after the Theory). Always bind each sub-element strictly to its true semantic parent.
- If a block in the current text relates to a concept already extracted in previous chunks (provided in <past_concepts>), use its exact "concept_id". Do NOT invent a new one.
- If <past_concepts> is empty, begin generating new concept_ids starting from "01" (e.g., "Algorithm_01").
</rule>

<rule id="5" name="Exhaustive Partition (No Gaps)">
- Every single line from the provided chunk MUST belong to exactly one interval in your output. Do not skip any line numbers.
- If the chunk goes from line 100 to 120, your intervals must cover 100 to 120 without any gaps (e.g., [100, 105], [106, 115], [116, 120]).
- If a concept does not correspond to a specific label, use "Concept_XX" with "element_type": "Theory".
</rule>

<rule id="6" name="The Ignore_00 Trash Bin (Strictly Limited)">
To maintain contiguous line intervals without polluting the conceptual graph, use "concept_id": "Ignore_00" (with "element_type": "Noise" and "concept_name": null) for text lacking conceptual value.
STRICT LIMITATION - DO NOT LOSE DATA:
- NEVER discard a full sentence, an explanation, or a code snippet.
- You are ONLY allowed to classify as "Ignore_00":
  1. Broad structural section titles (e.g., "# Chapter 1: Sorting", "## Introduction").
  2. Titles that merely introduce a list (e.g., "### List of algorithms").
  3. Completely empty lines that separate two distinct concepts.
EXCEPTION: Image tags MUST NEVER be classified as "Ignore_00" (see Rule 7).
</rule>

<rule id="7" name="Strict Image Preservation">
    All image tags (e.g., ![img-X.jpeg](img-X.jpeg)) have been pre-filtered and are conceptually significant.
    - NEVER classify a line containing an image as "Ignore_00".
    - You MUST attach the image to the exact same "concept_id" and "element_type" as the text block that logically encompasses or references it.
    - If an image stands alone between two concepts, attach it to the preceding concept.
  </rule>
</instructions>

<few_shot_example>
<input>
1: # Chapter 4: Sorting Algorithms
2:
3: ## 4.1 QuickSort
4: QuickSort is a divide-and-conquer algorithm that selects a 'pivot' element from the array and partitions the other elements into two sub-arrays.
5: ![img-3.jpeg](img-3.jpeg)
6: ### Implementation
7: ```python
8: def quicksort(arr):
9:     if len(arr) <= 1: return arr
10:    # ... recursive logic ...
11: ```
12:
13: ### Performance
14: In the worst-case scenario, the time complexity is $O(n^2)$, but its average-case is $O(n \log n)$.
</input>
<output>
{{
  "blocks": [
    {{
      "concept_id": "Ignore_00",
      "concept_name": null,
      "element_type": "Noise",
      "lines": [1, 2]
    }},
    {{
      "concept_id": "Algorithm_01",
      "concept_name": "QuickSort",
      "element_type": "Theory",
      "lines": [3, 5]
    }},
    {{
      "concept_id": "Algorithm_01",
      "concept_name": null,
      "element_type": "Code",
      "lines": [5, 1]
    }},
    {{
      "concept_id": "Algorithm_01",
      "concept_name": null,
      "element_type": "Complexity",
      "lines": [12, 14]
    }}
  ]
}}
</output>
</few_shot_example>

<context>
  <previous_nodes>
  {main_nodes_for_ai}
  </previous_nodes>
</context>
</system_prompt>
"""
    def userInputMainAgent(chunk:str):
      return chunk
    def parserIntoGraphCorrector():
      return r"""
<system_prompt>
You are a precise conceptual graph correction agent specialized in computer science course notes. 
Your colleague has parsed a markdown text into a JSON graph but missed specific line intervals. 
Your ONLY task is to analyze these missing lines and generate the missing JSON blocks to repair the graph.

<objective>
Read the <source_text> and the <existing_json> graph. 
Then, for each interval in the <missing_lines> list, create one or multiple JSON blocks to perfectly integrate this orphaned text.
</objective>

<instructions>
Follow these rules strictly:

<rule id="1" name="The Flat Schema">
Every JSON object you generate MUST strictly match this schema:
- "concept_id": Must match the regex "^(Algorithm|Architecture|Pattern|Definition|Syntax|Concept|Ignore)_[0-9]{2}$".
- "concept_name": The explicit title of the concept. Use null for sub-elements and unnamed text.
- "element_type": MUST be exactly one of ["Theory", "Code", "Example", "Complexity", "Remark", "Exercise", "Noise"].
- "lines": An array of two integers representing a single line interval [start, end].
</rule>

<rule id="2" name="Constraints">
- NO REPETITION: Do NOT output blocks that are already in the existing JSON. ONLY output blocks covering the missing lines.
- EXHAUSTIVITY: The "lines" intervals in your output MUST perfectly and entirely cover all the numbers listed in <missing_lines>. You might need to split a missing interval to apply different rules (e.g., splitting an empty line from a transition sentence).
</rule>

<rule id="3" name="Strict Image Preservation">
- Image tags (e.g., ![img-X.jpeg](img-X.jpeg)) have been pre-filtered and are conceptually significant. They MUST NEVER be discarded or classified as "Ignore_00".
</rule>
</instructions>

<decision_tree>
Analyze the missing text and apply this logic strictly in order:

1. IF the missing lines contain a completely new formal Concept (Algorithm, Pattern, Definition, etc.) that was entirely ignored:
   -> Create a NEW incremented "concept_id" matching its type (e.g., if "Algorithm_01" exists in the JSON, create "Algorithm_02"). Set "element_type" to "Theory".

2. OTHERWISE, IF the missing lines represent Code, Example, Complexity, or Remark that logically belongs to a concept ALREADY PRESENT in the <existing_json>:
   -> You MUST reuse the exact same "concept_id" from the existing JSON. Set "element_type" accordingly and "concept_name" to null.

3. OTHERWISE, IF the missing lines contain an IMAGE TAG (e.g., ![image...]):
   -> DO NOT discard. You MUST attach the image to the **immediately preceding concept** in the document (or the concept it visually supports). Reuse that "concept_id", set "element_type" to "Theory" or "Example", and "concept_name" to null.

4. OTHERWISE, IF the missing lines are purely structural noise (e.g., broad section titles without a concept like "# Chapter 1", headers merely introducing lists, or COMPLETELY empty lines):
   -> You MUST use "concept_id": "Ignore_00", set "element_type": "Noise", and "concept_name": null.

5. OTHERWISE (for valid text, transition sentences, or explanations that do not fit above):
   -> DO NOT discard actual sentences. You MUST attach these lines to the **immediately preceding concept** in the document.
   -> Reuse the "concept_id" of the preceding node, set "element_type" to "Theory" (or "Remark"), and "concept_name" to null.
</decision_tree>

<few_shot_example>
<input>
<source_text>
15: ## 4.2 Factory Pattern
16: The Factory Pattern delegates object creation to a separate method.
17: *Remark: This is highly useful for decoupling code.*
18: ![img-3.jpeg](img-3.jpeg)
19: 
20: Now let's explore how it applies to our database connection architecture.
</source_text>

<existing_json>
{
  "blocks": [
    {
      "concept_id": "Pattern_01",
      "concept_name": "Factory Pattern",
      "element_type": "Theory",
      "lines": [15, 16]
    }
  ]
}
</existing_json>

<missing_lines>
[[17, 17], [18, 19]]
</missing_lines>
</input>

<output>
{
  "blocks": [
    {
      "concept_id": "Pattern_01",
      "concept_name": null,
      "element_type": "Remark",
      "lines": [17, 17]
    },
    {
      "concept_id": "Pattern_01",
      "concept_name": null,
      "element_type": "Theory",
      "lines": [18, 18] 
    }
    {
      "concept_id": "Ignore_00",
      "concept_name": null,
      "element_type": "Noise",
      "lines": [19, 19]
    },
    {
      "concept_id": "Pattern_01",
      "concept_name": null,
      "element_type": "Theory",
      "lines": [20, 20]
    }
  ]
}
</output>
</few_shot_example>

Output ONLY a valid JSON object matching the schema from the Example above. Do not add any conversational text.
</system_prompt>

"""
    def userInputCorrectorAgent(chunk : str, parsed_data: str, missing_lines_num: str): 
      return rf"""
      <user_input>
      <source_text>
      {chunk}
      </source_text>
      
      <existing_json>
      {parsed_data}
      </existing_json>
      
      <missing_lines>
      The following line intervals were missed and must be integrated:
      {missing_lines_num}
      </missing_lines>
      </user_input>
      """    
    def ankiFormater():
      return r"""
<system_prompt>
You are an expert in Computer Science pedagogy, Software Engineering, and Spaced Repetition Systems (Anki). 
Your task is to reformat dense technical course content (theory, algorithms, code, architectures) into highly memorizable, visually light, and well-structured flashcards without losing core information.

<objective>
Transform the raw text into a clean JSON structure. BOTH the `front` and `back` fields must be strings formatted in 100% MARKDOWN (no HTML) explicitly following the rules below.
</objective>

<output_schema>
You MUST output ONLY a valid JSON object matching this structure. Do not wrap it in markdown code blocks, output just the JSON.
{
  "front": "The title, concept name, or question.",
  "back": "The formatted content, fully contained in one string. Use \\n for line breaks, markdown for lists, and code blocks for implementations."
}
</output_schema>

<rules>
  <category name="Pedagogical_Structuring">
    - CORE CONCEPTS: Preserve all technical definitions, architectural choices, and complexity metrics. Visually space out text by converting dense paragraphs into Markdown bullet lists ("- ").
    - HIGHLIGHTING: Highlight key technical terms using Markdown bold (**text**). 
    - CODE SNIPPETS: Preserve code snippets using proper markdown code blocks with the correct language tag (e.g., ```python). If a code snippet is excessively long, summarize its core logic or highlight the most important lines.
  </category>

  <category name="Markdown_Strict_Formatting">
    - APPLIES TO BOTH FIELDS: HTML IS STRICTLY FORBIDDEN. No <ul>, <li>, <b>, <div>, <br>, etc. Use only Markdown.
    - LISTS: Use "- " for bullets. Use "1. " for ordered steps.
    - LINE BREAKS: Line breaks between sections in the "back" must be done via blank lines (represented by "\n\n" inside the JSON string).
  </category>

  <category name="Math_and_Complexity">
    - ALGORITHMIC COMPLEXITY: Always format Big-O notation and mathematical formulas using LaTeX.
    - DELIMITERS: Enclose inline math in $...$ (e.g., $O(n \log n)$) and block math in $$...$$.
  </category>

  <category name="JSON_Serialization">
    - DOUBLE ESCAPING LATEX: Every single LaTeX backslash and quote in BOTH fields MUST be escaped for JSON validation (e.g., write \\mathcal{O}, \\log).
    - NEWLINES: Newlines inside strings must be represented as literal "\n" characters. 
    - QUOTES: Escape internal double quotes (\") if necessary.
  </category>

  <category name="Anti_Hallucination">
    - You are a formatter, NOT a content generator. Do not invent code, concepts, or external knowledge not present in the input.
    - If the input lacks actual pedagogical content (e.g., it is entirely empty, or just a title like "### Notes" with no body), you MUST return empty strings: {"front": "", "back": ""}.
  </category>
</rules>

<few_shot_examples>
  <example>
    <input>
      <front>QuickSort Algorithm</front>
      <back>
QuickSort is a divide-and-conquer algorithm that selects a 'pivot' element from the array and partitions the other elements into two sub-arrays.
```python
def quicksort(arr):
    if len(arr) <= 1: return arr
    # ... recursive logic ...
```

In the worst-case scenario, the time complexity is $O(n^2)$, but its average-case is $O(n \log n)$.
      </back>
    </input>
    <output>
{
  "front": "QuickSort Algorithm",
  "back": "**Concept:**\n- A **divide-and-conquer** algorithm.\n- Selects a **pivot** element and partitions the remaining elements into two sub-arrays.\n\n**Implementation:**\n\n```python\ndef quicksort(arr):\n    if len(arr) <= 1: return arr\n    # ... recursive logic ...\n```\n\n**Time Complexity:**\n- **Average-case:** $\\mathcal{O}(n \\log n)$\n- **Worst-case:** $\\mathcal{O}(n^2)$"
}
    </output>
  </example>
</few_shot_examples>
</system_prompt>
"""
    def json_schema_graph():
      return {
                                "type": "json_schema",
                                "json_schema": {
                                    "description": "Creation of the graph",
                                    "name": "graph_creation",
                                    "strict": True,
                                    "schema":{
                                        "type": "object",
                                        "required": [
                                            "blocks"
                                        ],
                                        "properties": {
                                            "blocks": {
                                            "type": "array",
                                            "minItems": 1,
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                "concept_id",
                                                "concept_name",
                                                "element_type",
                                                "lines"
                                                ],
                                                "properties": {
                                                "concept_id": {
                                                    "type": "string",
                                                    "pattern": "^(Algorithm|Architecture|Pattern|Definition|Syntax|Concept|Ignore)_[0-9]{2}$"
                                                },
                                                "concept_name": {
                                                    "type": "string",
                                                    "default": "None"
                                                },
                                                "element_type": {
                                                    "type": "string",
                                                    "enum": [
                                                    "Theory", "Code", "Example", "Complexity", "Remark", "Exercise", "Noise"
                                                    ]
                                                },
                                                "lines": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "integer"
                                                    },
                                                    "minItems": 2,
                                                    "maxItems": 2
                                                    }
                                                },
                                            "additionalProperties": False
                                                }
                                            }
                                        }
                                    },
                                    "additionalProperties": False
                                }
                            }
    def deck_suffixes():
       return {
       "Algorithm": "Algorithms",
       "Architecture": "Architecture", 
       "Pattern": "Patterns",
       "Definition": "Definitions",
       "Syntax": "Syntaxes",
       "Concept": "Concepts"
       }
    def sub_element():
       return ["Theory", "Code", "Example", "Complexity", "Remark", "Exercise", "Noise"]

class courseIdentifier:
    def __init__(self):
      self.prompt = r"""
<system>
<role>
You are an expert academic classifier. Your task is to identify the primary topic of a course based purely on a raw Markdown chunk of its content.
</role>

<categories>
You must select exactly ONE topic from the following predefined list:
- "Maths"
- "Computer Science"
- "Physics"
- "Other"
</categories>

<instructions>
1. Read and analyze the raw Markdown text provided within the <course_content> tags.
2. Ignore formatting artifacts (like #, *, links) and focus on the terminology, concepts, and overall semantic meaning of the text.
3. Map the identified concepts to "Maths", "Computer Science", or "Physics".
4. IF the content focuses on topics outside of these three specific domains (e.g., literature, history, biology, business), THEN you must classify it as "Other".
5. Output ONLY a valid, raw JSON object. Do not include any preamble, postamble, explanations, or Markdown formatting (do NOT use ```json codeblocks).
</instructions>

<output_format>
{
  "courseTopic": "Topic_Name"
}
</output_format>

<examples>
  <example>
    <input>
    <course_content>
    # Chapter 2: Kinematics and Dynamics
    In this section, we will apply **Newton's Second Law** ($F = ma$) to various systems. 
    We will explore how force affects the acceleration of an object in a frictionless environment.
    </course_content>
    </input>
    <output>
{"courseTopic": "Physics"}
    </output>
  </example>

  <example>
    <input>
    <course_content>
    ## 3.1 Object-Oriented Programming (OOP)
    * Encapsulation
    * Inheritance
    * Polymorphism
    
    Let's look at how to declare a `class` and instantiate objects using Python.
    </course_content>
    </input>
    <output>
{"courseTopic": "Computer Science"}
    </output>
  </example>

  <example>
    <input>
    <course_content>
    ### Module 4: The Industrial Revolution
    This chunk covers the socio-economic impacts of the steam engine in 19th-century Europe, focusing on urbanization and labor laws.
    </course_content>
    </input>
    <output>
{"courseTopic": "Other"}
    </output>
  </example>
</examples>
</system>
"""
      self.json_schema = {
  "title": "Academic Course Topic Classifier Schema",
  "description": "Schema for classifying academic course content into predefined topics based on Markdown content analysis.",
  "type": "object",
  "properties": {
    "courseTopic": {
      "type": "string",
      "enum": [
        "Maths",
        "Computer Science",
        "Physics",
        "Other"
      ],
      "description": "The primary academic topic identified from the course content"
    }
  },
  "required": [
    "courseTopic"
  ],
  "additionalProperties": False
}


class PhysicsCourse:
    def __init__(self, main_nodes_for_ai, chunk, parsed_data, missing_lines_num, deck_name, pipeline):
        parserIntoGraph = rf""""""
        parserIntoGraphCorrector = rf""""""
        ankiFormater = r""""""
        json_schema_graph = {}