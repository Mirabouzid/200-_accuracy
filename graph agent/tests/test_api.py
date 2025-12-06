"""
Script de test simple pour l'API BlockStat
Usage: python test_api.py
"""
import requests
import json
import sys

API_URL = "http://localhost:8000"


def test_health():
    """Test du health check"""
    print("🔍 Test Health Check...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        print("✅ Health Check OK")
        print(f"   Status: {response.json()['status']}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False


def test_analyze(token_address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"):
    """Test de l'analyse d'un token"""
    print(f"\n🔍 Test Analyse Token: {token_address[:20]}...")
    
    data = {
        "token_address": token_address,
        "chain": "ethereum"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/analyze",
            json=data,
            timeout=35  # Un peu plus que 30s pour le timeout
        )
        response.raise_for_status()
        result = response.json()
        
        # Afficher les résultats
        print("\n" + "="*50)
        print("📊 RÉSULTATS")
        print("="*50)
        
        time_taken = result.get('analysis_time_seconds', 0)
        print(f"⏱️  Temps d'analyse: {time_taken}s", end="")
        if time_taken < 30:
            print(" ✅ (<30s)")
        else:
            print(" ❌ (>30s - ÉCHEC hackathon)")
        
        risk_score = result.get('risk_score', 0)
        print(f"⚠️  Score de risque: {risk_score:.1%}")
        
        metrics = result.get('metrics', {})
        print(f"📈 Coefficient Gini: {metrics.get('gini', 0):.3f}")
        
        print(f"\n👥 Holders analysés: {len(result.get('top_holders', []))}")
        print(f"🔗 Clusters suspects: {len(result.get('suspicious_clusters', []))}")
        print(f"🔄 Paires wash trading: {len(result.get('wash_trade_pairs', []))}")
        print(f"🚨 Connexions mixers: {sum(1 for f in result.get('mixer_flags', []) if f.get('is_mixer'))}")
        
        graph_data = result.get('graph_data', {})
        print(f"\n🕸️  Graphe:")
        print(f"   - Nodes: {len(graph_data.get('nodes', []))}")
        print(f"   - Links: {len(graph_data.get('links', []))}")
        
        print("\n" + "="*50)
        print("✅ Analyse réussie!")
        
        return True
        
    except requests.exceptions.Timeout:
        print("❌ Timeout (>35s)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion. Vérifiez que le serveur est lancé:")
        print("   python main.py")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"   Détail: {error_detail.get('detail', 'Unknown error')}")
            except:
                print(f"   Réponse: {e.response.text[:200]}")
        return False


def main():
    """Fonction principale"""
    print("🚀 BlockStat - Test API")
    print("="*50)
    
    # Test 1: Health Check
    if not test_health():
        print("\n❌ Le serveur ne répond pas. Lancez-le avec: python main.py")
        sys.exit(1)
    
    # Test 2: Analyse
    token_address = sys.argv[1] if len(sys.argv) > 1 else None
    if token_address:
        test_analyze(token_address)
    else:
        # Token par défaut (USDC)
        test_analyze()
    
    print("\n💡 Pour tester avec un autre token:")
    print("   python test_api.py 0xADRESSE_DU_TOKEN")


if __name__ == "__main__":
    main()

