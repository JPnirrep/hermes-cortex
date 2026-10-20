import sys
import time

# Constantes de coût Antigravity (DNA F1)
COST_PER_1K_TOKENS = 0.015  # Moyenne pondérée
CRITICAL_THRESHOLD = 5000   # Seuil de vigilance (tokens)

def log_telemetry(tokens_in, tokens_out):
    total_tokens = tokens_in + tokens_out
    estimated_cost = (total_tokens / 1000) * COST_PER_1K_TOKENS
    
    # Écriture asynchrone dans un log circulaire (très rapide)
    with open("telemetry.log", "a") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] T:{total_tokens} C:{estimated_cost:.4f}$\n")
    
    # Alerte non-bloquante
    if total_tokens > CRITICAL_THRESHOLD:
        print(f"\n⚠️  [TELEMETRY ALERT] High fuel consumption: {total_tokens} tokens used.")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Invoqué asynchronement par l'orchestrateur
        log_telemetry(int(sys.argv[1]), int(sys.argv[2]))
