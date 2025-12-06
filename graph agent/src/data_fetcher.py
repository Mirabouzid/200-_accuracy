"""
Data Fetcher Module
Optimized to fetch only essential data for <30s constraint
Récupère les 10,000 dernières transactions du token selon spécifications hackathon
"""
import os
import httpx
import asyncio
import datetime
from typing import Dict, List, Optional
import time
import math
import random
from collections import defaultdict, OrderedDict
from config import Config


class DataFetcher:
    """
    Fetches blockchain data efficiently.
    Selon hackathon: fetch les 10,000 dernières transactions du token
    """
    
    # Cache LRU + TTL (partagé entre instances)
    _cache: OrderedDict = OrderedDict()
    _cache_lock = asyncio.Lock()

    def __init__(self, chain: str = "ethereum", preferred_provider: str = "auto"):
        self.chain = chain
        self.preferred_provider = preferred_provider.lower()
        # Track last successful provider used
        self.last_provider_used = None
        
        # Configurer les providers disponibles en fonction des clés API
        self.use_bitquery = bool(Config.BITQUERY_ACCESS_TOKEN)
        self.use_etherscan = bool(Config.ETHERSCAN_API_KEY)
        self.use_alchemy = bool(Config.ALCHEMY_API_KEY)

        if not self.use_bitquery and not self.use_etherscan and not self.use_alchemy:
            raise ValueError("Aucune clé API configurée")
        
        # Forcer l'utilisation d'un provider spécifique si demandé
        if self.preferred_provider == "bitquery":
            if not self.use_bitquery:
                available = []
                if self.use_etherscan:
                    available.append("Etherscan")
                if self.use_alchemy:
                    available.append("Alchemy")
                msg = "BitQuery API key not configured. Please add BITQUERY_ACCESS_TOKEN to .env"
                if available:
                    msg += f"\n\nAvailable APIs: {', '.join(available)}. You can use 'auto' mode or select one of these."
                raise ValueError(msg)
            self.use_etherscan = False
            self.use_alchemy = False
        elif self.preferred_provider == "etherscan":
            if not self.use_etherscan:
                available = []
                if self.use_bitquery:
                    available.append("BitQuery")
                if self.use_alchemy:
                    available.append("Alchemy")
                msg = "Etherscan API key not configured. Please add ETHERSCAN_API_KEY to .env"
                if available:
                    msg += f"\n\nAvailable APIs: {', '.join(available)}. You can use 'auto' mode or select one of these."
                raise ValueError(msg)
            self.use_bitquery = False
            self.use_alchemy = False
        elif self.preferred_provider == "alchemy":
            if not self.use_alchemy:
                available = []
                if self.use_bitquery:
                    available.append("BitQuery")
                if self.use_etherscan:
                    available.append("Etherscan")
                msg = "Alchemy API key not configured. Please add ALCHEMY_API_KEY to .env"
                if available:
                    msg += f"\n\nAvailable APIs: {', '.join(available)}. You can use 'auto' mode or select one of these."
                raise ValueError(msg)
            self.use_bitquery = False
            self.use_etherscan = False
        # Si "auto", on garde la priorité par défaut

    def _get_chain_id(self) -> int:
        """Map chain name to Etherscan V2 chainid (default Ethereum mainnet=1)."""
        mapping = {
            "ethereum": 1,
            "eth": 1,
            "mainnet": 1,
            "bsc": 56,
            "binance-smart-chain": 56,
            "polygon": 137,
            "matic": 137,
            "base": 8453,
            "arbitrum": 42161,
            "optimism": 10,
        }
        return mapping.get(self.chain.lower(), 1)
        
    # New helper for BitQuery network selection
    def _bitquery_networks(self):
        """
        Returns (v2_network_token, v1_network_name) for BitQuery per chain.
        V2 uses short tokens like eth/bsc/polygon/... in EVM(dataset: ..., network: <token>)
        V1 uses names like ethereum/bsc/polygon/... in ethereum(network: <name>)
        """
        chain = self.chain.lower()
        v2_map = {
            "ethereum": "eth",
            "eth": "eth",
            "mainnet": "eth",
            "bsc": "bsc",
            "binance-smart-chain": "bsc",
            "polygon": "polygon",
            "matic": "polygon",
            "arbitrum": "arbitrum",
            "optimism": "optimism",
            "base": "base",
        }
        v1_map = {
            "ethereum": "ethereum",
            "eth": "ethereum",
            "mainnet": "ethereum",
            "bsc": "bsc",
            "binance-smart-chain": "bsc",
            "polygon": "polygon",
            "matic": "polygon",
            "arbitrum": "arbitrum",
            "optimism": "optimism",
            "base": "base",
        }
        return v2_map.get(chain, "eth"), v1_map.get(chain, "ethereum")
        
    async def _cache_get(self, key: str):
        """Retourne la valeur en cache si TTL valide, sinon None"""
        async with self._cache_lock:
            if key in self._cache:
                entry = self._cache[key]
                if time.time() - entry["ts"] <= Config.CACHE_TTL_SECONDS:
                    # LRU: accès -> fin
                    self._cache.move_to_end(key, last=True)
                    return entry["value"]
                else:
                    # Expiré
                    del self._cache[key]
            return None
    
    async def _cache_set(self, key: str, value):
        """Insère/rafraîchit une entrée dans le cache avec TTL et LRU"""
        async with self._cache_lock:
            self._cache[key] = {"value": value, "ts": time.time()}
            self._cache.move_to_end(key, last=True)
            # Éviction LRU si dépassement
            if len(self._cache) > Config.MAX_CACHE_ITEMS:
                self._cache.popitem(last=False)
    
    def _cache_key(self, token_address: str) -> str:
        return f"{self.chain}:{token_address.lower()}"
    
    async def fetch_token_data(self, token_address: str) -> Dict:
        """
        Fetch les 10,000 dernières transactions du token selon spécifications hackathon
        """
        # Cache rapide (évite re-fetch pour tokens populaires)
        key = self._cache_key(token_address)
        cached = await self._cache_get(key)
        if cached is not None:
            # Si le cache contient un résultat vide, ne pas l'utiliser
            if cached.get("total_transactions_fetched", 0) > 0:
                print("  🧠 Cache hit: token data")
                return cached
            else:
                print("  🧠 Cache contient un résultat vide → rafraîchissement forcé")
        
        start = time.time()
        
        # Fetch transactions du token
        transactions = await self._fetch_token_transactions(token_address)
        
        # Extraire les wallets impliqués et leurs balances
        wallets_data = self._extract_wallets_from_transactions(transactions, token_address)
        
        # Trier par balance et prendre les top 50 pour l'output
        sorted_wallets = sorted(wallets_data.items(), key=lambda x: x[1]['balance'], reverse=True)
        top_holders = [
            {
                "address": addr,
                "balance": data['balance'],
                "transaction_count": data['transaction_count']
            }
            for addr, data in sorted_wallets[:Config.MAX_HOLDERS]
        ]
        
        # Fetch metadata du token
        metadata = await self._fetch_token_metadata(token_address)
        
        elapsed = time.time() - start
        print(f"  ✅ Data fetch: {len(transactions)} transactions, {len(wallets_data)} wallets uniques ({elapsed:.2f}s)")
        
        result = {
            "token_address": token_address,
            "chain": self.chain,
            "metadata": metadata,
            "top_holders": top_holders,
            "transactions": transactions,
            "all_wallets": list(wallets_data.keys()),  # Tous les wallets pour le graphe
            "total_transactions_fetched": len(transactions)
        }
        
        # Mettre en cache le résultat
        await self._cache_set(key, result)
        
        return result
    
    async def _fetch_token_transactions(self, token_address: str) -> List[Dict]:
        """
        Fetch les 10,000 dernières transactions du token ERC20
        Utilise le provider préféré ou la priorité par défaut (Alchemy > BitQuery > Etherscan)
        """
        transactions = []
        
        if self.use_alchemy:
            print(f"  📡 Using Alchemy API...")
            transactions = await self._fetch_transactions_alchemy(token_address)
            self.last_provider_used = "alchemy" if transactions else None
            if not transactions and self.use_bitquery:
                print("  ↪️ Alchemy returned 0 results. Falling back to BitQuery...")
                transactions = await self._fetch_transactions_bitquery(token_address)
                self.last_provider_used = "bitquery" if transactions else None
            if not transactions and self.use_etherscan:
                print("  ↪️ BitQuery returned 0 results. Falling back to Etherscan...")
                transactions = await self._fetch_transactions_etherscan(token_address)
                if not transactions:
                    print("    ↪️ Etherscan getLogs returned 0 results. Trying account.tokentx fallback...")
                    transactions = await self._fetch_transactions_etherscan_tokentx(token_address)
                self.last_provider_used = "etherscan" if transactions else None
        elif self.use_bitquery:
            print(f"  📡 Using BitQuery API...")
            transactions = await self._fetch_transactions_bitquery(token_address)
            self.last_provider_used = "bitquery" if transactions else None
            if not transactions and self.use_alchemy:
                print("  ↪️ BitQuery returned 0 results. Falling back to Alchemy...")
                transactions = await self._fetch_transactions_alchemy(token_address)
                self.last_provider_used = "alchemy" if transactions else None
            if not transactions and self.use_etherscan:
                print("  ↪️ Alchemy returned 0 results. Falling back to Etherscan...")
                transactions = await self._fetch_transactions_etherscan(token_address)
                if not transactions:
                    print("    ↪️ Etherscan getLogs returned 0 results. Trying account.tokentx fallback...")
                    transactions = await self._fetch_transactions_etherscan_tokentx(token_address)
                self.last_provider_used = "etherscan" if transactions else None
        elif self.use_etherscan:
            print(f"  📡 Using Etherscan API...")
            transactions = await self._fetch_transactions_etherscan(token_address)
            if not transactions:
                print("  ↪️ Etherscan getLogs returned 0 results. Trying account.tokentx fallback...")
                transactions = await self._fetch_transactions_etherscan_tokentx(token_address)
            self.last_provider_used = "etherscan" if transactions else None
            if not transactions and self.use_alchemy:
                print("  ↪️ Etherscan returned 0 results. Falling back to Alchemy...")
                transactions = await self._fetch_transactions_alchemy(token_address)
                self.last_provider_used = "alchemy" if transactions else None
            if not transactions and self.use_bitquery:
                print("  ↪️ Alchemy returned 0 results. Falling back to BitQuery...")
                transactions = await self._fetch_transactions_bitquery(token_address)
                self.last_provider_used = "bitquery" if transactions else None
        else:
            raise ValueError("No API provider available")
        
        return transactions[:Config.MAX_TRANSACTIONS_TO_FETCH]
    
    async def _fetch_transactions_etherscan(self, token_address: str) -> List[Dict]:
        """
        Implémentation propre et robuste d'Etherscan getLogs pour l'event ERC20 Transfer.
        - Récupère latest block via proxy, fallback getblocknobytime
        - Récupère décimales via tokeninfo, fallback eth_call(decimals)
        - Fenêtrage dynamique avec division récursive si "log response size exceeded" ou 1000 logs
        - Gestion du rate limit (HTTP 429 et payload status=0)
        """
        url = Config.ETHERSCAN_API_URL
        sem = asyncio.Semaphore(Config.MAX_CONCURRENT_REQUESTS)
        chain_id = self._get_chain_id()

        async with httpx.AsyncClient(timeout=Config.REQUEST_TIMEOUT_SECONDS) as client:
            async def get_latest_block() -> int:
                try:
                    r = await client.get(url, params={
                        "module": "proxy",
                        "action": "eth_blockNumber",
                        "chainid": str(chain_id),
                        "apikey": Config.ETHERSCAN_API_KEY,
                    })
                    r.raise_for_status()
                    hb = r.json().get("result", "0x0")
                    return int(hb, 16)
                except Exception:
                    try:
                        r2 = await client.get(url, params={
                            "module": "block",
                            "action": "getblocknobytime",
                            "timestamp": str(int(time.time())),
                            "closest": "before",
                            "chainid": str(chain_id),
                            "apikey": Config.ETHERSCAN_API_KEY,
                        })
                        r2.raise_for_status()
                        rb = r2.json().get("result")
                        return int(rb) if rb and str(rb).isdigit() else 0
                    except Exception:
                        return 0

            async def get_decimals() -> int:
                # Try tokeninfo
                try:
                    rm = await client.get(url, params={
                        "module": "token",
                        "action": "tokeninfo",
                        "contractaddress": token_address,
                        "chainid": str(chain_id),
                        "apikey": Config.ETHERSCAN_API_KEY,
                    })
                    rm.raise_for_status()
                    dm = rm.json()
                    if dm.get("status") == "1" and dm.get("result"):
                        val = dm["result"][0].get("decimals")
                        if val is not None:
                            return int(val)
                except Exception:
                    pass
                # Fallback eth_call(decimals)
                try:
                    # decimals() selector: 0x313ce567
                    rc = await client.get(url, params={
                        "module": "proxy",
                        "action": "eth_call",
                        "to": token_address,
                        "data": "0x313ce567",
                        "tag": "latest",
                        "chainid": str(chain_id),
                        "apikey": Config.ETHERSCAN_API_KEY,
                    })
                    rc.raise_for_status()
                    res = rc.json().get("result")
                    if isinstance(res, str) and res.startswith("0x"):
                        return int(res, 16)
                except Exception:
                    pass
                return 18

            latest_block = await get_latest_block()
            if latest_block <= 0 or latest_block > 100_000_000:
                latest_block = 20_000_000
            print(f"  🧱 Latest block (Etherscan): {latest_block}")

            decimals = await get_decimals()

            # Fenêtrage: on limite à ~10k blocs et on s'adapte au nombre de pages
            max_pages = min(max(1, math.ceil(Config.MAX_TRANSACTIONS_TO_FETCH / 1000)), 10)
            window = min(10_000, max(2_000, latest_block // max(max_pages * 12, 1)))
            transfer_topic0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

            async def fetch_window(idx: int, start_block: int, end_block: int, depth: int = 0) -> List[Dict]:
                await asyncio.sleep(idx / max(Config.REQUESTS_PER_SECOND, 1))
                async with sem:
                    tries = 0
                    backoff = 0.5
                    while tries < 3:
                        try:
                            params = {
                                "module": "logs",
                                "action": "getLogs",
                                "address": token_address,
                                "fromBlock": str(start_block),
                                "toBlock": str(end_block),
                                "topic0": transfer_topic0,
                                "chainid": str(chain_id),
                                "apikey": Config.ETHERSCAN_API_KEY,
                            }
                            resp = await client.get(url, params=params)
                            resp.raise_for_status()
                            data = resp.json()

                            message = str(data.get("message", ""))
                            result = data.get("result")
                            if data.get("status") == "1" and isinstance(result, list):
                                print(f"    📦 Fenêtre {start_block}-{end_block}: {len(result)} logs (depth {depth})")
                                if len(result) >= 1000 and depth < 6:
                                    mid = (start_block + end_block) // 2
                                    left = await fetch_window(idx, start_block, mid, depth + 1)
                                    right = await fetch_window(idx, mid + 1, end_block, depth + 1)
                                    return left + right
                                page = []
                                for log in result:
                                    try:
                                        topics = log.get("topics", [])
                                        if len(topics) < 3:
                                            continue
                                        from_addr = "0x" + topics[1][-40:].lower()
                                        to_addr = "0x" + topics[2][-40:].lower()
                                        raw_value_hex = log.get("data", "0x0")
                                        value = int(raw_value_hex, 16) / (10 ** decimals)
                                        ts = log.get("timeStamp")
                                        if isinstance(ts, str) and ts.startswith("0x"):
                                            timestamp = int(ts, 16)
                                        elif isinstance(ts, str) and ts.isdigit():
                                            timestamp = int(ts)
                                        else:
                                            timestamp = 0
                                        page.append({
                                            "hash": log.get("transactionHash", ""),
                                            "from": from_addr,
                                            "to": to_addr,
                                            "value": value,
                                            "timestamp": timestamp,
                                            "block": log.get("blockNumber", ""),
                                        })
                                    except Exception:
                                        continue
                                return page

                            # status=0
                            result_text = result if isinstance(result, str) else ""
                            low = result_text.lower() if isinstance(result_text, str) else ""
                            if "invalid api key" in low:
                                print(f"  ❌ Etherscan: Invalid API Key (message: '{message}')")
                                return []
                            if ("log response size exceeded" in low or "exceeded" in low) and depth < 6:
                                print(f"    ⚖️ Fenêtre trop large {start_block}-{end_block} (message: '{message}', result: '{result_text}'), split...")
                                mid = (start_block + end_block) // 2
                                left = await fetch_window(idx, start_block, mid, depth + 1)
                                right = await fetch_window(idx, mid + 1, end_block, depth + 1)
                                return left + right
                            if ("max rate limit" in low or "rate limit" in low or "too many" in low):
                                print(f"    ⏳ Rate limit Etherscan (message: '{message}', result: '{result_text}') -> retry")
                                await asyncio.sleep(backoff + random.uniform(0, 0.25))
                                backoff *= 2
                                tries += 1
                                continue

                            # Aucun résultat
                            print(f"    🧩 Fenêtre {start_block}-{end_block}: aucun log (message: '{message}', result: '{result_text}')")
                            return []
                        except httpx.HTTPStatusError as e:
                            status = e.response.status_code
                            if status in (429, 500, 502, 503, 504):
                                await asyncio.sleep(backoff + random.uniform(0, 0.25))
                                backoff *= 2
                                tries += 1
                                continue
                            else:
                                print(f"  ⚠️ Etherscan HTTP error (window {start_block}-{end_block}): {status}")
                                return []
                        except Exception:
                            tries += 1
                            await asyncio.sleep(backoff)
                            backoff *= 2
                    print(f"  ⚠️ Etherscan error persistant (window {start_block}-{end_block})")
                    return []

            tasks = []
            cursor = latest_block
            for i in range(max_pages):
                start = max(0, cursor - window + 1)
                end = cursor
                tasks.append(fetch_window(i + 1, start, end))
                cursor = start - 1
                if cursor <= 0:
                    break

            results = await asyncio.gather(*tasks)

        all_tx: List[Dict] = [tx for page_list in results for tx in page_list]
        seen = set()
        deduped = []
        for tx in all_tx:
            h = tx.get("hash", "")
            if h and h not in seen:
                seen.add(h)
                deduped.append(tx)
        deduped.sort(key=lambda t: t.get("timestamp", 0), reverse=True)
        return deduped[:Config.MAX_TRANSACTIONS_TO_FETCH]

    async def _fetch_transactions_etherscan_tokentx(self, token_address: str) -> List[Dict]:
        """
        Fallback Etherscan implementation using account.tokentx (ERC20 transfers list) with pagination.
        - Uses v2 API with chainid
        - Paginates by page and offset up to MAX_TRANSACTIONS_TO_FETCH
        - Leverages tokenDecimal field to compute value
        """
        url = Config.ETHERSCAN_API_URL
        chain_id = self._get_chain_id()
        max_needed = Config.MAX_TRANSACTIONS_TO_FETCH
        per_page = min(1000, max_needed)
        transfers: List[Dict] = []
        page = 1
        backoff = 0.5

        async with httpx.AsyncClient(timeout=Config.REQUEST_TIMEOUT_SECONDS) as client:
            while len(transfers) < max_needed:
                try:
                    params = {
                        "module": "account",
                        "action": "tokentx",
                        "contractaddress": token_address,
                        "page": str(page),
                        "offset": str(per_page),
                        "sort": "desc",
                        "chainid": str(chain_id),
                        "apikey": Config.ETHERSCAN_API_KEY,
                    }
                    resp = await client.get(url, params=params)
                    resp.raise_for_status()
                    data = resp.json()
                    status = data.get("status")
                    result = data.get("result")
                    if status == "1" and isinstance(result, list):
                        if not result:
                            break
                        for tx in result:
                            try:
                                # Parse typical tokentx fields
                                from_addr = tx.get("from", "").lower()
                                to_addr = tx.get("to", "").lower()
                                # tokenDecimal might be string, default 18
                                decimals_str = tx.get("tokenDecimal", "18")
                                decimals = int(decimals_str) if str(decimals_str).isdigit() else 18
                                value_raw = tx.get("value", "0")
                                value = int(value_raw) / (10 ** decimals)
                                # timeStamp is seconds string
                                ts_str = tx.get("timeStamp", "0")
                                timestamp = int(ts_str) if str(ts_str).isdigit() else 0
                                transfers.append({
                                    "hash": tx.get("hash", ""),
                                    "from": from_addr,
                                    "to": to_addr,
                                    "value": value,
                                    "timestamp": timestamp,
                                    "block": tx.get("blockNumber", ""),
                                })
                            except Exception:
                                continue
                        # Go next page
                        page += 1
                        # If we got less than per_page, likely final page
                        if len(result) < per_page:
                            break
                        continue
                    else:
                        # Handle rate limits or errors
                        msg = str(data.get("message", ""))
                        res_text = result if isinstance(result, str) else ""
                        low = str(res_text).lower()
                        if ("rate limit" in low or "too many" in low) or resp.status_code == 429:
                            await asyncio.sleep(backoff + random.uniform(0, 0.25))
                            backoff *= 2
                            continue
                        # No more results
                        break
                except httpx.HTTPStatusError as e:
                    if e.response.status_code in (429, 500, 502, 503, 504):
                        await asyncio.sleep(backoff + random.uniform(0, 0.25))
                        backoff *= 2
                        continue
                    else:
                        break
                except Exception:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
        # Deduplicate by hash and sort desc by timestamp
        seen = set()
        deduped = []
        for tx in transfers:
            h = tx.get("hash", "")
            if h and h not in seen:
                seen.add(h)
                deduped.append(tx)
        deduped.sort(key=lambda t: t.get("timestamp", 0), reverse=True)
        return deduped[:Config.MAX_TRANSACTIONS_TO_FETCH]

    async def _fetch_transactions_alchemy(self, token_address: str) -> List[Dict]:
        """
        Fetch transactions via Alchemy Transfers API (alchemy_getAssetTransfers) pour ERC20.
        - Filtre par contractAddresses = [token_address]
        - category=['erc20'] pour capturer les événements Transfer
        - Pagination via pageKey et maxCount jusqu'à MAX_TRANSACTIONS_TO_FETCH
        """
        endpoint = f"{Config.ALCHEMY_BASE_URL}/{Config.ALCHEMY_API_KEY}"
        normalized_token_address = token_address.lower()

        async def get_decimals_alchemy() -> int:
            try:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "eth_call",
                    "params": [
                        {"to": normalized_token_address, "data": "0x313ce567"},
                        "latest",
                    ],
                }
                async with httpx.AsyncClient(timeout=Config.REQUEST_TIMEOUT_SECONDS) as client:
                    r = await client.post(endpoint, json=payload)
                    r.raise_for_status()
                    res = r.json().get("result")
                    if isinstance(res, str) and res.startswith("0x"):
                        return int(res, 16)
            except Exception:
                pass
            return 18

        decimals = await get_decimals_alchemy()
        print(f"  🔢 Decimals (Alchemy): {decimals}")

        transfers: List[Dict] = []
        page_key: Optional[str] = None
        max_needed = Config.MAX_TRANSACTIONS_TO_FETCH
        max_per_page = min(1000, max_needed)

        # Boucle de pagination
        async with httpx.AsyncClient(timeout=Config.REQUEST_TIMEOUT_SECONDS) as client:
            while len(transfers) < max_needed:
                params_obj = {
                    "fromBlock": "0x0",   # depuis le début (pour robustesse)
                    "toBlock": "latest",
                    "order": "desc",
                    "category": ["erc20"],
                    "contractAddresses": [normalized_token_address],
                    "excludeZeroValue": True,
                    "withMetadata": True,
                    "maxCount": hex(max_per_page),  # Alchemy attend une quantité hexadécimale (ex: 1000 -> 0x3e8)
                }
                if page_key:
                    params_obj["pageKey"] = page_key

                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "alchemy_getAssetTransfers",
                    "params": [params_obj],
                }

                try:
                    resp = await client.post(endpoint, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    if "error" in data:
                        err = data["error"]
                        print(f"  ⚠️ Alchemy RPC error: {err}")
                        await asyncio.sleep(0.5)
                        continue
                    result = data.get("result", {})
                    page_transfers = result.get("transfers", [])
                    page_key = result.get("pageKey") or None

                    print(f"    📦 Alchemy page: {len(page_transfers)} transfers")

                    for t in page_transfers:
                        try:
                            from_addr = (t.get("from") or "").lower()
                            to_addr = (t.get("to") or "").lower()
                            tx_hash = t.get("hash") or ""
                            block_hex = t.get("blockNum") or "0x0"
                            block_int = int(block_hex, 16) if isinstance(block_hex, str) and block_hex.startswith("0x") else 0
                            raw = t.get("rawContract") or {}
                            raw_val_hex = raw.get("value") or "0x0"
                            value = int(raw_val_hex, 16) / (10 ** decimals)
                            # timestamp via metadata.blockTimestamp si présent
                            meta = t.get("metadata") or {}
                            ts = meta.get("blockTimestamp")
                            if isinstance(ts, str) and ts:
                                try:
                                    dt = ts.replace("Z", "+00:00")
                                    timestamp = int(datetime.datetime.fromisoformat(dt).timestamp())
                                except Exception:
                                    timestamp = 0
                            else:
                                timestamp = 0

                            transfers.append({
                                "hash": tx_hash,
                                "from": from_addr,
                                "to": to_addr,
                                "value": value,
                                "timestamp": timestamp,
                                "block": block_int,
                            })
                        except Exception:
                            continue

                    if not page_key or len(page_transfers) == 0:
                        break
                except httpx.HTTPStatusError as e:
                    status = e.response.status_code
                    print(f"  ⚠️ Alchemy HTTP error: {status}")
                    await asyncio.sleep(0.5)
                    continue

        # Déduplication et limite
        seen = set()
        deduped = []
        for tx in transfers:
            h = tx.get("hash", "")
            if h and h not in seen:
                seen.add(h)
                deduped.append(tx)
        deduped.sort(key=lambda t: t.get("timestamp", 0), reverse=True)
        return deduped[:max_needed]

    async def _fetch_transactions_bitquery(self, token_address: str) -> List[Dict]:
        """
        Fetch les dernières transactions via BitQuery (V2 puis V1) pour la chaîne demandée
        """
        transactions: List[Dict] = []

        # Resolve BitQuery network per chain
        v2_network, v1_network = self._bitquery_networks()
        
        # Essayer d'abord la nouvelle API V2 (streaming endpoint)
        query_v2 = f"""
        query ($token_address: String!, $limit: Int!) {{
          EVM(dataset: combined, network: {v2_network}) {{
            Transfers(
              limit: {{count: $limit}}
              orderBy: {{descending: Block_Time}}
              where: {{Transfer: {{Currency: {{SmartContract: {{is: $token_address}}}}}}}}
            ) {{
              Block {{
                Time
              }}
              Transaction {{
                Hash
              }}
              Transfer {{
                Sender
                Receiver
                Amount
                Currency {{
                  Symbol
                  SmartContract
                  Decimals
                }}
              }}
            }}
          }}
        }}
        """
        
        # Fallback vers V1 API
        query_v1 = f"""
        query ($token_address: String!, $limit: Int!) {{
          ethereum(network: {v1_network}) {{
            transfers(
              options: {{desc: "block.timestamp.unixtime", limit: $limit}}
              currency: {{is: $token_address}}
            ) {{
              block {{
                timestamp {{
                  unixtime
                }}
                height
              }}
              transaction {{
                hash
              }}
              sender {{
                address
              }}
              receiver {{
                address
              }}
              amount
              currency {{
                symbol
                decimals
              }}
            }}
          }}
        }}
        """
        
        variables = {
            "token_address": token_address,
            "limit": min(Config.MAX_TRANSACTIONS_TO_FETCH, 10000)
        }
        
        # Essayer V2 d'abord (streaming endpoint), puis V1
        endpoints_and_queries = [
            ("https://streaming.bitquery.io/graphql", query_v2, "V2"),
            (Config.BITQUERY_ENDPOINT, query_v1, "V1")
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint, query, version in endpoints_and_queries:
                try:
                    print(f"  📡 Fetching transactions via BitQuery {version} API...")
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {Config.BITQUERY_ACCESS_TOKEN}",
                        "X-API-KEY": Config.BITQUERY_ACCESS_TOKEN
                    }
                    
                    payload = {
                        "query": query,
                        "variables": variables
                    }
                    
                    response = await client.post(
                        endpoint,
                        json=payload,
                        headers=headers
                    )
                    
                    if response.status_code == 401:
                        print(f"  ⚠️ Authentication failed with {version} API. Trying next...")
                        continue
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # Vérifier les erreurs GraphQL
                    if "errors" in data:
                        print(f"  ⚠️ BitQuery GraphQL errors ({version}): {data['errors']}")
                        continue
                    
                    # Parser réponse V2
                    if version == "V2":
                        transfers = data.get("data", {}).get("EVM", {}).get("Transfers", [])
                        if transfers:
                            print(f"  ✅ BitQuery V2 returned {len(transfers)} transfers")
                            for transfer in transfers:
                                try:
                                    from datetime import datetime
                                    block_time = transfer.get("Block", {}).get("Time", "")
                                    if block_time:
                                        timestamp = int(datetime.fromisoformat(block_time.replace("Z", "+00:00")).timestamp())
                                    else:
                                        timestamp = 0
                                    
                                    decimals = transfer.get("Transfer", {}).get("Currency", {}).get("Decimals", 18)
                                    if decimals is None:
                                        decimals = 18
                                    
                                    amount_raw = transfer.get("Transfer", {}).get("Amount", 0)
                                    if amount_raw:
                                        amount = float(amount_raw) / (10 ** int(decimals))
                                    else:
                                        amount = 0
                                    
                                    tx_hash = transfer.get("Transaction", {}).get("Hash", "")
                                    sender_addr = transfer.get("Transfer", {}).get("Sender", "")
                                    receiver_addr = transfer.get("Transfer", {}).get("Receiver", "")
                                    
                                    if sender_addr and receiver_addr:
                                        transactions.append({
                                            "hash": tx_hash,
                                            "from": sender_addr.lower(),
                                            "to": receiver_addr.lower(),
                                            "value": amount,
                                            "timestamp": timestamp,
                                            "block": ""
                                        })
                                except Exception as e:
                                    print(f"  ⚠️ Error parsing V2 transfer: {e}")
                                    continue
                            
                            if transactions:
                                print(f"  ✅ Parsed {len(transactions)} transactions from BitQuery V2")
                                return transactions
                    
                    # Parser réponse V1
                    else:
                        transfers = data.get("data", {}).get("ethereum", {}).get("transfers", [])
                        if transfers:
                            print(f"  ✅ BitQuery V1 returned {len(transfers)} transfers")
                            for transfer in transfers:
                                try:
                                    decimals = transfer.get("currency", {}).get("decimals", 18)
                                    if decimals is None:
                                        decimals = 18
                                    
                                    amount_raw = transfer.get("amount", 0)
                                    if amount_raw:
                                        amount = float(amount_raw) / (10 ** int(decimals))
                                    else:
                                        amount = 0
                                    
                                    tx_hash = transfer.get("transaction", {}).get("hash", "")
                                    sender_addr = transfer.get("sender", {}).get("address", "")
                                    receiver_addr = transfer.get("receiver", {}).get("address", "")
                                    timestamp = transfer.get("block", {}).get("timestamp", {}).get("unixtime", 0)
                                    block_height = transfer.get("block", {}).get("height", "")
                                    
                                    if sender_addr and receiver_addr:
                                        transactions.append({
                                            "hash": tx_hash,
                                            "from": sender_addr.lower(),
                                            "to": receiver_addr.lower(),
                                            "value": amount,
                                            "timestamp": timestamp,
                                            "block": block_height
                                        })
                                except Exception as e:
                                    print(f"  ⚠️ Error parsing V1 transfer: {e}")
                                    continue
                            
                            if transactions:
                                print(f"  ✅ Parsed {len(transactions)} transactions from BitQuery V1")
                                return transactions
                    
                    print(f"  ⚠️ No data returned from {version} API. Trying next...")
                    
                except httpx.HTTPStatusError as e:
                    print(f"  ⚠️ BitQuery HTTP error ({version}): {e.response.status_code} - {e.response.text[:200]}")
                    if version == "V1":  # Dernière option
                        return []
                    continue
                except Exception as e:
                    print(f"  ⚠️ BitQuery API error ({version}): {e}")
                    if version == "V1":  # Dernière option
                        import traceback
                        traceback.print_exc()
                        return []
                    continue
            
            print(f"  ⚠️ Failed to fetch transactions from both V2 and V1 APIs")
            return []
    
    def _extract_wallets_from_transactions(
        self, 
        transactions: List[Dict], 
        token_address: str
    ) -> Dict[str, Dict]:
        """
        Extrait tous les wallets impliqués dans les transactions
        et calcule leurs balances (approximatives basées sur les transactions)
        """
        wallets = defaultdict(lambda: {"balance": 0, "transaction_count": 0, "sent": 0, "received": 0})
        
        for tx in transactions:
            from_addr = tx.get("from", "")
            to_addr = tx.get("to", "")
            value = tx.get("value", 0)
            
            if from_addr:
                wallets[from_addr]["sent"] += value
                wallets[from_addr]["transaction_count"] += 1
            
            if to_addr:
                wallets[to_addr]["received"] += value
                wallets[to_addr]["transaction_count"] += 1
        
        # Calculer balance approximative (received - sent)
        # Note: C'est une approximation, pour avoir les vraies balances il faudrait
        # interroger le contrat directement, mais ça prendrait trop de temps
        for addr, data in wallets.items():
            data["balance"] = max(0, data["received"] - data["sent"])
        
        return dict(wallets)
    
    async def _fetch_token_metadata(self, token_address: str) -> Dict:
        """Fetch basic token metadata"""
        # Try Alchemy first for metadata (align with transactions priority)
        if self.use_alchemy:
            metadata = await self._fetch_metadata_alchemy(token_address)
            if metadata.get("symbol") != "UNKNOWN":
                return metadata
        
        # Essayer BitQuery ensuite pour les métadonnées
        if self.use_bitquery:
            metadata = await self._fetch_metadata_bitquery(token_address)
            if metadata.get("symbol") != "UNKNOWN":
                return metadata
        
        # Fallback vers Etherscan
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                if self.use_etherscan:
                    url = Config.ETHERSCAN_API_URL
                    chain_id = self._get_chain_id()
                    params = {
                        "module": "token",
                        "action": "tokeninfo",
                        "contractaddress": token_address,
                        "chainid": str(chain_id),
                        "apikey": Config.ETHERSCAN_API_KEY
                    }
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get("status") == "1" and data.get("result"):
                        token_info = data["result"][0]
                        return {
                            "address": token_address,
                            "symbol": token_info.get("symbol", "UNKNOWN"),
                            "name": token_info.get("name", "Token"),
                            "decimals": int(token_info.get("decimals", 18)),
                            "total_supply": token_info.get("totalSupply", "0")
                        }
            except Exception as e:
                print(f"  ⚠️ Error fetching metadata: {e}")
        
        # Fallback: métadonnées basiques
        return {
            "address": token_address,
            "symbol": "UNKNOWN",
            "name": "Token",
            "decimals": 18
        }
    
    async def _fetch_metadata_bitquery(self, token_address: str) -> Dict:
        """Fetch token metadata via BitQuery"""
        # Resolve BitQuery network per chain
        _, v1_network = self._bitquery_networks()
        query = f"""
        {{
          ethereum(network: {v1_network}) {{
            address(address: {{is: "{token_address}"}}) {{
              smartContract {{
                currency {{
                  symbol
                  name
                  decimals
                  totalSupply
                }}
              }}
            }}
          }}
        }}
        """
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {Config.BITQUERY_ACCESS_TOKEN}",
                    "X-API-KEY": Config.BITQUERY_ACCESS_TOKEN,
                }
                response = await client.post(
                    Config.BITQUERY_ENDPOINT,
                    json={"query": query},
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                if "data" in data and "ethereum" in data["data"]:
                    address_data = data["data"]["ethereum"].get("address", [])
                    if address_data and address_data[0].get("smartContract"):
                        currency = address_data[0]["smartContract"].get("currency", {})
                        if currency:
                            return {
                                "address": token_address,
                                "symbol": currency.get("symbol", "UNKNOWN"),
                                "name": currency.get("name", "Token"),
                                "decimals": int(currency.get("decimals", 18)),
                                "total_supply": currency.get("totalSupply", "0")
                            }
            except Exception as e:
                print(f"  ⚠️ BitQuery metadata error: {e}")
        
        return {
            "address": token_address,
            "symbol": "UNKNOWN",
            "name": "Token",
            "decimals": 18
        }

    async def _fetch_metadata_alchemy(self, token_address: str) -> Dict:
        """Fetch token metadata via Alchemy JSON-RPC (name, symbol, decimals, totalSupply)"""
        endpoint = f"{Config.ALCHEMY_BASE_URL}/{Config.ALCHEMY_API_KEY}"
        normalized = token_address.lower()
        symbol = "UNKNOWN"
        name = "Token"
        decimals: Optional[int] = None
        total_supply: Optional[str] = None
        
        # Try Alchemy enhanced method first
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "alchemy_getTokenMetadata",
                "params": [normalized],
            }
            async with httpx.AsyncClient(timeout=Config.REQUEST_TIMEOUT_SECONDS) as client:
                resp = await client.post(endpoint, json=payload)
                resp.raise_for_status()
                data = resp.json()
                result = data.get("result") or {}
                symbol = result.get("symbol") or symbol
                name = result.get("name") or name
                if result.get("decimals") is not None:
                    try:
                        decimals = int(result.get("decimals"))
                    except Exception:
                        decimals = None
        except Exception as e:
            print(f"  ⚠️ Alchemy metadata error: {e}")
        
        # Fallback: get decimals via eth_call if missing
        if decimals is None:
            try:
                payload_dec = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "eth_call",
                    "params": [
                        {"to": normalized, "data": "0x313ce567"},
                        "latest",
                    ],
                }
                async with httpx.AsyncClient(timeout=Config.REQUEST_TIMEOUT_SECONDS) as client:
                    r = await client.post(endpoint, json=payload_dec)
                    r.raise_for_status()
                    res = r.json().get("result")
                    if isinstance(res, str) and res.startswith("0x"):
                        decimals = int(res, 16)
            except Exception:
                decimals = 18
        
        # Optional: totalSupply via eth_call
        try:
            payload_ts = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "eth_call",
                "params": [
                    {"to": normalized, "data": "0x18160ddd"},
                    "latest",
                ],
            }
            async with httpx.AsyncClient(timeout=Config.REQUEST_TIMEOUT_SECONDS) as client:
                r2 = await client.post(endpoint, json=payload_ts)
                r2.raise_for_status()
                rs = r2.json().get("result")
                if isinstance(rs, str) and rs.startswith("0x"):
                    total_supply = str(int(rs, 16))
        except Exception:
            total_supply = None
        
        metadata = {
            "address": normalized,
            "symbol": symbol,
            "name": name,
            "decimals": decimals if decimals is not None else 18,
        }
        if total_supply is not None:
            metadata["total_supply"] = total_supply
        return metadata
