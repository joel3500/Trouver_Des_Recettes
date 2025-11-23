import time, os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


API_KEY = (
    os.getenv("OPENAI_API_KEY")
    or os.getenv("OPENAI_API_KEY_2")
    or os.getenv("OPENAI_API_KEY_3")
)
if not API_KEY:
    raise RuntimeError("Aucune clé API trouvée dans .env (OPENAI_API_KEY).")
client = OpenAI(api_key=API_KEY)



def bench_model(model_name: str, prompt: str):
    t0 = time.perf_counter()
    result = client.images.generate(
        model=model_name,
        prompt=prompt,
        n=1,
        size="1024x1024"  # tu peux tester d'autres tailles
        # quality="standard"  # pour dall-e-3 seulement
    )
    dt = time.perf_counter() - t0
    print(f"{model_name} -> {dt:.2f} s")
    return result

prompt = "Couscous èa la sauce légume"

bench_model("gpt-image-1", prompt)
bench_model("dall-e-3", prompt)

