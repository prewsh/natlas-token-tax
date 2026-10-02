from transformers import AutoTokenizer

model_id = "meta-llama/Meta-Llama-3-8B"
text = "The children went to school today."

print(f"Loading tokenizer: {model_id}")

tokenizer = AutoTokenizer.from_pretrained(model_id)

token_ids = tokenizer.encode(
    text,
    add_special_tokens=False,
)

tokens = tokenizer.convert_ids_to_tokens(token_ids)

print("\nOriginal text:")
print(text)

print("\nTokens:")
print(tokens)

print("\nToken IDs:")
print(token_ids)

print("\nNumber of tokens:")
print(len(token_ids))

print("\nVocabulary size:")
print(len(tokenizer))