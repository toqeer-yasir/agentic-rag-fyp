import torch
import tiktoken

# my model architecture imports
from llm_for_title_generation.gpt_model import GPTModel
from llm_for_title_generation.config import GPTConfig
from transformers.generation.utils import GenerationMixin

# ==================================================
# loading model:

if GenerationMixin not in GPTModel.__bases__: GPTModel.__bases__ = ( GPTModel.__bases__[0], GenerationMixin, *GPTModel.__bases__[1:])
config = GPTConfig()
model = GPTModel(config)

state_dict = torch.load("llm_for_title_generation/chat_title_generator_model.pth", map_location="cpu")
model.load_state_dict(state_dict)
model.eval()

tokenizer = tiktoken.get_encoding("gpt2")

# function to predict title:
def predict_chat_title(chat_msgs: str, max_tokens: int = 15):

    chat_msgs_lowered = chat_msgs.lower()

    coding_keywords = [
        "how",
        "write",
        "code",
        "delete",
        "run",
        "fix"
    ]

    if any(word in chat_msgs_lowered for word in coding_keywords):
        instruction = (
            "Read the following chat log and provide a short title "
            "describing what the user wants or what is being discussed."
        )
    else:
        instruction = (
            "Read the following conversation and generate a short "
            "declarative title summarizing its core conceptual theme."
        )

    prompt = (
        f"### Instruction:\n"
        f"{instruction}\n\n"
        f"### Conversation:\n"
        f"{chat_msgs.strip()}\n\n"
        f"### Title:\n"
    )

    input_ids = tokenizer.encode(prompt)

    input_tensor = torch.tensor([input_ids])

    generated_tokens = []

    with torch.no_grad():

        for _ in range(max_tokens):

            outputs = model(input_tensor)

            logits = (outputs[1] if isinstance(outputs, tuple) else outputs)

            next_token = torch.argmax(logits[:, -1, :], dim=-1).item()

            if next_token == tokenizer.eot_token:
                break

            generated_tokens.append(next_token)

            input_tensor = torch.cat(
                [
                    input_tensor,
                    torch.tensor([[next_token]])
                ],
                dim=1
            )

    title = tokenizer.decode(generated_tokens)

    title = (
        title.split("\n")[0]
        .replace("###", "")
        .strip(".,!? ")
    )

    return title or "New Chat"