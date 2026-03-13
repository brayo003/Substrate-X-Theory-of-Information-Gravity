import stripe

def process_mercor_payroll(api_key):
    # 1. Access the Stripe Substrate
    stripe.api_key = api_key
    try:
        data = stripe.Charge.list(limit=50)
        # 2. Apply Deterministic Logic (The Governor)
        sorted_equity = sorted(data.data, key=lambda x: x.created, reverse=True)
        print(f"Successfully sorted {len(sorted_equity)} transactions.")
        return sorted_equity
    except Exception as e:
        print(f"Substrate Error: {e}")

if __name__ == "__main__":
    print("Mercor Stripe Module Active.")
