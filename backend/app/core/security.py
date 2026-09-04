"""Security, Rate Limiting, and Abuse Detection for Merchant DNA APIs."""

import time
from typing import Dict, Set, Tuple, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TrustApiRateLimiter:
    """Sliding-window rate limiter with reverse-engineering score probing abuse detection."""

    def __init__(
        self,
        max_requests_per_minute: int = 60,
        probe_threshold_distinct_merchants: int = 20,
        probe_window_seconds: int = 300,  # 5 minutes
    ):
        self.max_requests = max_requests_per_minute
        self.window_seconds = 60
        self.probe_threshold = probe_threshold_distinct_merchants
        self.probe_window = probe_window_seconds

        # IP -> list of timestamps
        self.request_timestamps: Dict[str, list] = defaultdict(list)
        # IP -> list of (timestamp, merchant_id)
        self.merchant_queries: Dict[str, list] = defaultdict(list)
        # Set of flagged abuse IPs
        self.flagged_probe_ips: Set[str] = set()

    def check_rate_limit(
        self,
        client_ip: str,
        merchant_id: str,
    ) -> Tuple[bool, int, int, bool]:
        """Checks rate limit and detects scraping/probing patterns.
        
        Returns:
            (is_allowed, remaining_requests, retry_after_seconds, is_abuse_flagged)
        """
        now = time.time()
        
        # 1. Clean old request timestamps for standard rate limit (1 min window)
        timestamps = self.request_timestamps[client_ip]
        self.request_timestamps[client_ip] = [t for t in timestamps if now - t < self.window_seconds]
        current_req_count = len(self.request_timestamps[client_ip])

        # 2. Clean old merchant query history (5 min window)
        queries = self.merchant_queries[client_ip]
        self.merchant_queries[client_ip] = [(t, m) for (t, m) in queries if now - t < self.probe_window]
        self.merchant_queries[client_ip].append((now, merchant_id))

        # Check distinct merchants in probe window
        distinct_merchants = set(m for (_, m) in self.merchant_queries[client_ip])
        is_abuse_flagged = False

        if len(distinct_merchants) >= self.probe_threshold:
            is_abuse_flagged = True
            if client_ip not in self.flagged_probe_ips:
                self.flagged_probe_ips.add(client_ip)
                logger.warning(
                    f"[SECURITY AUDIT] Reverse-engineering probing pattern detected! "
                    f"IP '{client_ip}' queried {len(distinct_merchants)} distinct merchant trust signals "
                    f"in under {self.probe_window}s. Throttling and logging abuse event."
                )

        # 3. Check rate limit threshold
        if current_req_count >= self.max_requests or is_abuse_flagged:
            # If abuse flagged, enforce stricter rate limit (max 5 req/min)
            if is_abuse_flagged and current_req_count >= 5:
                oldest_t = self.request_timestamps[client_ip][0] if self.request_timestamps[client_ip] else now
                retry_after = max(1, int(self.window_seconds - (now - oldest_t)))
                return False, 0, retry_after, True

            if current_req_count >= self.max_requests:
                oldest_t = self.request_timestamps[client_ip][0] if self.request_timestamps[client_ip] else now
                retry_after = max(1, int(self.window_seconds - (now - oldest_t)))
                return False, 0, retry_after, is_abuse_flagged

        # Record this valid request
        self.request_timestamps[client_ip].append(now)
        remaining = max(0, self.max_requests - (current_req_count + 1))
        return True, remaining, 0, is_abuse_flagged

    def reset(self):
        """Clears all tracking state (used in unit testing)."""
        self.request_timestamps.clear()
        self.merchant_queries.clear()
        self.flagged_probe_ips.clear()


# Global security rate limiter singleton
trust_rate_limiter = TrustApiRateLimiter()
