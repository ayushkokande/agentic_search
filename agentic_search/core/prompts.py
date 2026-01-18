# Prompt templates for LLM steps

PROMPT_PARSE = (
    "You are an assistant that parses user search queries. "
    "Given the query, determine the domain (generic or healthcare) and any key terms. "
    "Respond with a JSON of form {\"domain\": ..., \"keywords\": ...}. "
)

PROMPT_EXPAND = (
    "Given the query and domain, generate an expanded query for improved search results. "
    "For example, add synonyms or related terms. Respond with the expanded query as plain text."
)

PROMPT_RELAX = (
    "The current search returned no results. Suggest a relaxed query or additional terms to broaden the search. "
    "Respond with the new query string."
)
